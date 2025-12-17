"""
Setup script for the RAG system
This script handles installation of dependencies and initialization of the vector database.
"""

import subprocess
import sys
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def install_dependencies():
    """
    Install required Python packages
    """
    requirements_file = "requirements.txt"

    if not os.path.exists(requirements_file):
        logger.error(f"Requirements file {requirements_file} not found")
        return False

    try:
        logger.info("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
        logger.info("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        return False


def setup_qdrant():
    """
    Setup Qdrant vector database
    """
    try:
        import qdrant_client
        logger.info("Qdrant client is available")

        # Test connection to Qdrant
        from qdrant_client import QdrantClient

        # Using in-memory storage for development
        client = QdrantClient(location=":memory:")

        # Test creating a collection
        from qdrant_client.http.models import Distance, VectorParams

        collection_name = "ebook_rag_test"
        try:
            client.delete_collection(collection_name)  # Clean up if exists
        except:
            pass  # Collection doesn't exist, which is fine

        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
        )

        # Clean up test collection
        client.delete_collection(collection_name)

        logger.info("Qdrant setup verified successfully")
        return True
    except ImportError:
        logger.error("Qdrant client not available. Install with: pip install qdrant-client")
        return False
    except Exception as e:
        logger.error(f"Error setting up Qdrant: {e}")
        return False


def setup_cohere():
    """
    Verify Cohere API setup
    """
    try:
        import cohere
        logger.info("Cohere client is available")

        # Check if API key is available
        import os
        api_key = os.getenv('COHERE_API_KEY')
        if not api_key:
            logger.warning("COHERE_API_KEY environment variable not set. Please set it before running embedding.")
            return False

        # Test initializing client
        client = cohere.Client(api_key)
        logger.info("Cohere client initialized successfully")
        return True
    except ImportError:
        logger.error("Cohere client not available. Install with: pip install cohere")
        return False
    except Exception as e:
        logger.error(f"Error setting up Cohere: {e}")
        return False


def create_env_file():
    """
    Create a .env file template for API keys
    """
    env_content = """# Environment variables for RAG System
COHERE_API_KEY=your_cohere_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
QDRANT_URL=http://localhost:6333  # Optional: for remote Qdrant instance
QDRANT_API_KEY=your_qdrant_api_key_here  # Optional: for authenticated Qdrant instance
"""

    env_file = ".env"
    if not os.path.exists(env_file):
        with open(env_file, "w") as f:
            f.write(env_content)
        logger.info(f"Created {env_file} template file")
    else:
        logger.info(f"{env_file} already exists")


def main():
    """
    Main setup function
    """
    print("Setting up RAG System...")

    # Create rag-system directory if it doesn't exist
    rag_dir = Path("rag-system")
    rag_dir.mkdir(exist_ok=True)

    # Change to rag-system directory
    os.chdir(rag_dir)

    # Create src directory if it doesn't exist
    src_dir = Path("src")
    src_dir.mkdir(exist_ok=True)

    # Install dependencies
    if not install_dependencies():
        print("Failed to install dependencies. Please install manually using: pip install -r requirements.txt")
        return False

    # Create .env file
    create_env_file()

    # Setup Qdrant
    qdrant_ok = setup_qdrant()

    # Setup Cohere
    cohere_ok = setup_cohere()

    print("\nSetup Summary:")
    print(f"- Dependencies: {'✓' if True else '✗'}")  # Dependencies installation succeeded if we got this far
    print(f"- Qdrant: {'✓' if qdrant_ok else '✗'}")
    print(f"- Cohere: {'✓' if cohere_ok else '✗'}")

    if qdrant_ok and cohere_ok:
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Set your API keys in the .env file")
        print("2. Run the content extractor: python src/content_extractor.py")
        print("3. Run the embedder: python src/embedder.py")
        print("4. Validate the system: python src/validator.py")
        return True
    else:
        print("\n⚠️  Setup completed with warnings. Please address the issues above.")
        print("Make sure to set your API keys and verify the services are working.")
        return False


if __name__ == "__main__":
    main()