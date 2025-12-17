"""
RAG-enabled AI Agent Backend
This script creates a RAG-enabled AI agent using OpenAI's API, FastAPI, and Qdrant.
"""

import os
import json
import logging
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import cohere
import openai
from dotenv import load_dotenv

from embedder import QdrantVectorStore, CohereEmbedder

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="E-Book RAG API",
    description="RAG system API for the Physical AI and Humanoid Robotics e-book",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
try:
    # Initialize Cohere embedder
    cohere_embedder = CohereEmbedder()

    # Initialize Qdrant vector store
    vector_store = QdrantVectorStore(collection_name="ebook_rag")

    # Initialize OpenAI client
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")

    openai_client = openai.OpenAI(api_key=openai_api_key)

    logger.info("Services initialized successfully")
    services_initialized = True
except Exception as e:
    logger.error(f"Failed to initialize services: {e}")
    services_initialized = False


class QueryRequest(BaseModel):
    query: str
    top_k: int = Query(5, ge=1, le=10, description="Number of top results to retrieve")
    temperature: float = Query(0.7, ge=0.0, le=1.0, description="Temperature for response generation")


class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[Dict]
    retrieved_texts: List[str]


class RAGAgent:
    def __init__(self, vector_store: QdrantVectorStore, cohere_embedder: CohereEmbedder, openai_client):
        self.vector_store = vector_store
        self.cohere_embedder = cohere_embedder
        self.openai_client = openai_client

    def retrieve_context(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve relevant context from the vector store

        Args:
            query: User query
            top_k: Number of results to retrieve

        Returns:
            List of retrieved documents
        """
        # Generate embedding for the query
        query_embeddings = self.cohere_embedder.embed_texts([query])
        query_embedding = query_embeddings[0]

        # Retrieve results from vector store
        retrieved_docs = self.vector_store.search(query_embedding, top_k=top_k)

        return retrieved_docs

    def generate_answer(self, query: str, context: List[Dict], temperature: float = 0.7) -> str:
        """
        Generate an answer using OpenAI based on the retrieved context

        Args:
            query: User query
            context: Retrieved context documents
            temperature: Temperature for response generation

        Returns:
            Generated answer
        """
        # Format context for the prompt
        context_text = "\n\n".join([f"Source: {doc['title']}\nURL: {doc['url']}\nContent: {doc['text'][:1000]}"
                                   for doc in context])  # Limit content length

        # Create the prompt for OpenAI
        prompt = f"""
        You are an AI assistant for the Physical AI and Humanoid Robotics e-book.
        Answer the user's question based strictly on the provided context from the e-book.
        If the answer cannot be found in the context, clearly state that the information is not available in the provided documents.

        Context:
        {context_text}

        Question: {query}

        Answer:
        """

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",  # You can change this to gpt-4 if preferred
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant for the Physical AI and Humanoid Robotics e-book. Answer questions based strictly on the provided context."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=1000
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return f"Error generating answer: {str(e)}"

    def answer_query(self, query: str, top_k: int = 5, temperature: float = 0.7) -> QueryResponse:
        """
        Complete RAG pipeline: retrieve context and generate answer

        Args:
            query: User query
            top_k: Number of results to retrieve
            temperature: Temperature for response generation

        Returns:
            QueryResponse with answer and sources
        """
        # Retrieve relevant context
        context = self.retrieve_context(query, top_k)

        if not context:
            return QueryResponse(
                query=query,
                answer="No relevant documents found for your query.",
                sources=[],
                retrieved_texts=[]
            )

        # Generate answer based on context
        answer = self.generate_answer(query, context, temperature)

        # Prepare response
        sources = [
            {
                "title": doc["title"],
                "url": doc["url"],
                "score": doc["score"]
            }
            for doc in context
        ]

        retrieved_texts = [doc["text"] for doc in context]

        return QueryResponse(
            query=query,
            answer=answer,
            sources=sources,
            retrieved_texts=retrieved_texts
        )


# Initialize RAG agent
rag_agent = RAGAgent(vector_store, cohere_embedder, openai_client) if services_initialized else None


@app.get("/")
def read_root():
    """Root endpoint"""
    return {"message": "E-Book RAG API is running", "status": "healthy"}


@app.post("/query", response_model=QueryResponse)
def query_endpoint(request: QueryRequest):
    """
    Endpoint to query the RAG system
    """
    if not services_initialized:
        raise HTTPException(status_code=500, detail="Services not properly initialized. Check API keys and connections.")

    try:
        response = rag_agent.answer_query(
            query=request.query,
            top_k=request.top_k,
            temperature=request.temperature
        )
        return response
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services_initialized": services_initialized,
        "vector_store": "available" if services_initialized else "unavailable"
    }


@app.get("/search")
def search_endpoint(query: str, top_k: int = Query(5, ge=1, le=10)):
    """
    Endpoint to search the vector database directly
    """
    if not services_initialized:
        raise HTTPException(status_code=500, detail="Services not properly initialized. Check API keys and connections.")

    try:
        # Generate embedding for the query
        query_embeddings = cohere_embedder.embed_texts([query])
        query_embedding = query_embeddings[0]

        # Retrieve results from vector store
        retrieved_docs = vector_store.search(query_embedding, top_k=top_k)

        return {
            "query": query,
            "results": [
                {
                    "title": doc["title"],
                    "url": doc["url"],
                    "text": doc["text"][:500] + "..." if len(doc["text"]) > 500 else doc["text"],  # Truncate for response
                    "score": doc["score"]
                }
                for doc in retrieved_docs
            ]
        }
    except Exception as e:
        logger.error(f"Error in search: {e}")
        raise HTTPException(status_code=500, detail=f"Error in search: {str(e)}")


def main():
    """Run the FastAPI application"""
    import uvicorn

    if not services_initialized:
        logger.error("Cannot start server: services not properly initialized. Check API keys.")
        print("Error: Services not properly initialized. Please check your API keys and environment setup.")
        return

    logger.info("Starting RAG API server...")
    print("Starting RAG API server...")
    print("API documentation available at: http://localhost:8000/docs")

    uvicorn.run(
        "rag_agent:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Enable auto-reload during development
    )


if __name__ == "__main__":
    main()