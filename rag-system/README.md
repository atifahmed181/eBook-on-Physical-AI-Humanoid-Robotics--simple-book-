# RAG System for Physical AI and Humanoid Robotics E-Book

This repository implements a Retrieval-Augmented Generation (RAG) system for the Physical AI and Humanoid Robotics e-book. The system allows users to ask questions about the e-book content and receive AI-generated answers based on the provided documentation.

## Architecture

The RAG system consists of the following components:

1. **Content Extractor**: Extracts content from the deployed Docusaurus e-book
2. **Embedder**: Chunks the content and generates embeddings using Cohere
3. **Vector Store**: Stores embeddings in Qdrant vector database
4. **RAG Agent**: Combines retrieval and generation using OpenAI
5. **FastAPI Backend**: Provides REST API endpoints
6. **Frontend Chatbot**: React component integrated into Docusaurus

## Prerequisites

- Python 3.8+
- Node.js 18+
- API Keys:
  - Cohere API Key (for embeddings)
  - OpenAI API Key (for generation)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Install Backend Dependencies

```bash
cd rag-system
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the `rag-system` directory:

```bash
COHERE_API_KEY=your_cohere_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. Run the Complete Pipeline

#### Step 1: Extract Content
```bash
cd rag-system
python src/content_extractor.py
```

#### Step 2: Generate Embeddings
```bash
python src/embedder.py
```

#### Step 3: Validate the System
```bash
python src/validator.py
```

#### Step 4: Start the Backend Server
```bash
python -m uvicorn src.rag_agent:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Run the Frontend

In a separate terminal, from the main project directory:

```bash
cd docs
npm install
npm run start
```

The Docusaurus site will be available at `http://localhost:3000`, and the chatbot will be accessible at `http://localhost:3000/chatbot`.

## API Endpoints

Once the backend is running, the following endpoints are available:

- `GET /`: Health check
- `GET /health`: Detailed health status
- `POST /query`: Submit a query to the RAG system
- `GET /search`: Direct search of the vector database

Example query request:
```json
{
  "query": "What is ROS 2?",
  "top_k": 5,
  "temperature": 0.7
}
```

## Testing

To run the comprehensive test suite:

```bash
cd rag-system
python test_system.py
```

## Project Structure

```
rag-system/
├── src/
│   ├── content_extractor.py    # Extract content from Docusaurus site
│   ├── embedder.py             # Generate embeddings and store in Qdrant
│   ├── validator.py            # Validate retrieval quality
│   └── rag_agent.py            # RAG agent with FastAPI backend
├── requirements.txt            # Python dependencies
├── .env                       # Environment variables
└── test_system.py             # Comprehensive test suite
```

## Troubleshooting

1. **API Keys**: Ensure your API keys are correctly set in the `.env` file
2. **Port Conflicts**: If port 8000 is in use, change it in the uvicorn command
3. **CORS Issues**: The backend allows all origins for development; restrict in production
4. **Content Extraction**: If the deployed site structure changes, update the extractor accordingly

## Deployment

For production deployment:

1. Use a hosted Qdrant instance instead of in-memory storage
2. Set up proper CORS policies
3. Use environment-specific configurations
4. Consider containerizing the backend with Docker