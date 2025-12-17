"""
Embedding generator for the e-book content
This script chunks the extracted content and generates embeddings using Cohere.
"""

import json
import cohere
from typing import List, Dict, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import logging
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentChunker:
    def __init__(self, max_chunk_size: int = 512, overlap: int = 50):
        """
        Initialize the content chunker

        Args:
            max_chunk_size: Maximum size of each chunk in tokens
            overlap: Number of overlapping tokens between chunks
        """
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str, title: str = "", url: str = "") -> List[Dict]:
        """
        Split text into overlapping chunks

        Args:
            text: Text to chunk
            title: Title of the document
            url: URL of the document

        Returns:
            List of chunk dictionaries
        """
        # Simple tokenization by words (for now)
        words = text.split()

        chunks = []
        start_idx = 0

        while start_idx < len(words):
            # Calculate end index for the chunk
            end_idx = start_idx + self.max_chunk_size

            # Adjust end index if it goes beyond the text
            if end_idx > len(words):
                end_idx = len(words)

            # Create the chunk text
            chunk_text = " ".join(words[start_idx:end_idx])

            # Create chunk metadata
            chunk_data = {
                "text": chunk_text,
                "title": title,
                "url": url,
                "start_idx": start_idx,
                "end_idx": end_idx
            }

            chunks.append(chunk_data)

            # Move start index forward by chunk size minus overlap
            start_idx = end_idx - self.overlap

            # If no progress is made, break to avoid infinite loop
            if start_idx >= end_idx:
                break

        return chunks

    def chunk_documents(self, documents: List[Dict]) -> List[Dict]:
        """
        Chunk a list of documents

        Args:
            documents: List of document dictionaries with 'content', 'title', 'url'

        Returns:
            List of chunk dictionaries
        """
        all_chunks = []

        for doc in documents:
            content = doc.get('content', '')
            title = doc.get('title', '')
            url = doc.get('url', '')

            if content:
                chunks = self.chunk_text(content, title, url)
                all_chunks.extend(chunks)

        return all_chunks


class CohereEmbedder:
    def __init__(self, api_key: str = None):
        """
        Initialize the Cohere embedder

        Args:
            api_key: Cohere API key. If None, will try to get from environment variable COHERE_API_KEY
        """
        if not api_key:
            api_key = os.getenv('COHERE_API_KEY')

        if not api_key:
            raise ValueError("Cohere API key is required. Set COHERE_API_KEY environment variable or pass as parameter.")

        self.client = cohere.Client(api_key)
        self.model = "embed-multilingual-v3.0"  # Using multilingual model for broader coverage

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts

        Args:
            texts: List of texts to embed

        Returns:
            List of embeddings (each embedding is a list of floats)
        """
        try:
            response = self.client.embed(
                texts=texts,
                model=self.model,
                input_type="search_document"  # Using search_document for content indexing
            )
            return response.embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return [[] for _ in texts]  # Return empty embeddings in case of error


class QdrantVectorStore:
    def __init__(self, collection_name: str = "ebook_rag"):
        """
        Initialize the Qdrant vector store

        Args:
            collection_name: Name of the Qdrant collection
        """
        self.collection_name = collection_name

        # Import qdrant_client here to handle the case where it's not installed
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.http.models import Distance, VectorParams
        except ImportError:
            raise ImportError("qdrant-client is required. Install it with: pip install qdrant-client")

        # Initialize Qdrant client (using local instance by default)
        self.client = QdrantClient(location=":memory:")  # Using in-memory storage for now

        # Create collection if it doesn't exist
        self._create_collection()

    def _create_collection(self):
        """Create the Qdrant collection if it doesn't exist"""
        from qdrant_client.http.models import Distance, VectorParams

        try:
            # Try to get collection info to check if it exists
            self.client.get_collection(self.collection_name)
            logger.info(f"Collection '{self.collection_name}' already exists")
        except:
            # Collection doesn't exist, create it
            # Assuming embedding dimension of 1024 for Cohere embeddings
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
            )
            logger.info(f"Created collection '{self.collection_name}'")

    def store_embeddings(self, chunks: List[Dict], embeddings: List[List[float]]):
        """
        Store chunks and their embeddings in Qdrant

        Args:
            chunks: List of chunk dictionaries
            embeddings: List of corresponding embeddings
        """
        from qdrant_client.http.models import PointStruct
        import uuid

        # Prepare points for insertion
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "text": chunk["text"],
                    "title": chunk.get("title", ""),
                    "url": chunk.get("url", ""),
                    "start_idx": chunk.get("start_idx", 0),
                    "end_idx": chunk.get("end_idx", 0)
                }
            )
            points.append(point)

        # Upload points to Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        logger.info(f"Stored {len(points)} embeddings in Qdrant collection '{self.collection_name}'")

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """
        Search for similar documents in the vector store

        Args:
            query_embedding: Embedding of the query
            top_k: Number of top results to return

        Returns:
            List of similar document dictionaries
        """
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k
        )

        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "text": result.payload["text"],
                "title": result.payload["title"],
                "url": result.payload["url"],
                "score": result.score
            })

        return formatted_results


def load_extracted_content(input_file: str) -> List[Dict]:
    """
    Load extracted content from JSON file

    Args:
        input_file: Path to input file

    Returns:
        List of content dictionaries
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        content = json.load(f)
    logger.info(f"Loaded {len(content)} documents from {input_file}")
    return content


def main():
    # Load the extracted content
    input_file = "extracted_ebook_content.json"

    if not os.path.exists(input_file):
        logger.error(f"Input file {input_file} does not exist. Run content_extractor.py first.")
        return

    documents = load_extracted_content(input_file)

    # Chunk the content
    chunker = ContentChunker(max_chunk_size=512, overlap=50)
    chunks = chunker.chunk_documents(documents)

    logger.info(f"Chunked content into {len(chunks)} chunks")

    # Generate embeddings using Cohere
    # Note: You'll need to set your Cohere API key as an environment variable
    try:
        embedder = CohereEmbedder()

        # Extract texts for embedding
        texts = [chunk["text"] for chunk in chunks]

        # Generate embeddings in batches to avoid rate limits
        batch_size = 96  # Cohere's batch limit is 96
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")

            batch_embeddings = embedder.embed_texts(batch_texts)
            all_embeddings.extend(batch_embeddings)

        logger.info(f"Generated embeddings for {len(all_embeddings)} chunks")

        # Store in Qdrant
        vector_store = QdrantVectorStore(collection_name="ebook_rag")
        vector_store.store_embeddings(chunks, all_embeddings)

        logger.info("Successfully stored embeddings in Qdrant vector store")

        # Save chunks to file for reference
        with open("chunks.json", "w", encoding="utf-8") as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)

        print(f"Embedding process complete! Processed {len(chunks)} chunks and stored in Qdrant.")

    except Exception as e:
        logger.error(f"Error during embedding process: {e}")
        print(f"Embedding failed: {e}")


if __name__ == "__main__":
    main()