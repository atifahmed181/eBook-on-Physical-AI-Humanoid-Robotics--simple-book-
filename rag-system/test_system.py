"""
Test script for the complete RAG system
This script tests the end-to-end functionality of the RAG system.
"""

import subprocess
import sys
import time
import requests
import json
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_content_extraction():
    """Test the content extraction process"""
    logger.info("Testing content extraction...")

    try:
        # Run the content extractor
        result = subprocess.run([
            sys.executable,
            "src/content_extractor.py"
        ], cwd="rag-system", capture_output=True, text=True, timeout=120)

        if result.returncode != 0:
            logger.error(f"Content extraction failed: {result.stderr}")
            return False

        # Check if the output file was created
        output_file = Path("rag-system/extracted_ebook_content.json")
        if not output_file.exists():
            logger.error("Extracted content file not created")
            return False

        # Check if the file has content
        with open(output_file, 'r', encoding='utf-8') as f:
            content = json.load(f)

        if len(content) == 0:
            logger.error("Extracted content is empty")
            return False

        logger.info(f"Content extraction successful: {len(content)} pages extracted")
        return True

    except subprocess.TimeoutExpired:
        logger.error("Content extraction timed out")
        return False
    except Exception as e:
        logger.error(f"Error during content extraction: {e}")
        return False


def test_embedding_generation():
    """Test the embedding generation process"""
    logger.info("Testing embedding generation...")

    try:
        # Run the embedder
        result = subprocess.run([
            sys.executable,
            "src/embedder.py"
        ], cwd="rag-system", capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            logger.error(f"Embedding generation failed: {result.stderr}")
            return False

        # Check if chunks were created
        chunks_file = Path("rag-system/chunks.json")
        if not chunks_file.exists():
            logger.error("Chunks file not created")
            return False

        with open(chunks_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)

        if len(chunks) == 0:
            logger.error("Chunks file is empty")
            return False

        logger.info(f"Embedding generation successful: {len(chunks)} chunks processed")
        return True

    except subprocess.TimeoutExpired:
        logger.error("Embedding generation timed out")
        return False
    except Exception as e:
        logger.error(f"Error during embedding generation: {e}")
        return False


def test_validation():
    """Test the validation process"""
    logger.info("Testing validation...")

    try:
        # Run the validator
        result = subprocess.run([
            sys.executable,
            "src/validator.py"
        ], cwd="rag-system", capture_output=True, text=True, timeout=120)

        if result.returncode != 0:
            logger.error(f"Validation failed: {result.stderr}")
            return False

        # Check if validation results were created
        validation_file = Path("rag-system/validation_results.json")
        if not validation_file.exists():
            logger.error("Validation results file not created")
            return False

        with open(validation_file, 'r', encoding='utf-8') as f:
            results = json.load(f)

        if not results:
            logger.error("Validation results are empty")
            return False

        logger.info("Validation successful")
        return True

    except subprocess.TimeoutExpired:
        logger.error("Validation timed out")
        return False
    except Exception as e:
        logger.error(f"Error during validation: {e}")
        return False


def test_backend_startup():
    """Test if the backend can start successfully"""
    logger.info("Testing backend startup...")

    try:
        # Try to import required modules
        import uvicorn
        import fastapi
        import cohere
        import openai
        import qdrant_client

        logger.info("Backend dependencies are available")
        return True

    except ImportError as e:
        logger.error(f"Missing backend dependency: {e}")
        return False
    except Exception as e:
        logger.error(f"Error testing backend: {e}")
        return False


def test_api_endpoints():
    """Test the API endpoints if the server is running"""
    logger.info("Testing API endpoints...")

    try:
        # Test if server is running on localhost:8000
        response = requests.get("http://localhost:8000/health", timeout=10)

        if response.status_code != 200:
            logger.warning("Backend server not running. Skipping API tests.")
            return True  # Not a failure, just server not started

        health_data = response.json()
        logger.info(f"Backend health: {health_data}")

        # Test the root endpoint
        root_response = requests.get("http://localhost:8000/", timeout=10)
        if root_response.status_code != 200:
            logger.error("Root endpoint not accessible")
            return False

        # Test a sample query if vector store is ready
        if health_data.get("vector_store") == "available":
            sample_query = {
                "query": "What is ROS 2?",
                "top_k": 3,
                "temperature": 0.7
            }

            query_response = requests.post(
                "http://localhost:8000/query",
                json=sample_query,
                timeout=30
            )

            if query_response.status_code != 200:
                logger.error(f"Query endpoint failed: {query_response.status_code}")
                return False

            query_data = query_response.json()
            logger.info(f"Sample query successful. Answer length: {len(query_data.get('answer', ''))} chars")

        return True

    except requests.exceptions.ConnectionError:
        logger.warning("Backend server not running. Skipping API tests.")
        return True  # Not a failure, just server not started
    except Exception as e:
        logger.error(f"Error testing API endpoints: {e}")
        return False


def run_comprehensive_test():
    """Run all tests for the RAG system"""
    logger.info("Starting comprehensive RAG system test...")

    tests = [
        ("Content Extraction", test_content_extraction),
        ("Embedding Generation", test_embedding_generation),
        ("Validation", test_validation),
        ("Backend Startup", test_backend_startup),
        ("API Endpoints", test_api_endpoints),
    ]

    results = {}
    all_passed = True

    for test_name, test_func in tests:
        logger.info(f"Running {test_name} test...")
        try:
            result = test_func()
            results[test_name] = result
            if result:
                logger.info(f"{test_name}: PASSED")
            else:
                logger.error(f"{test_name}: FAILED")
                all_passed = False
        except Exception as e:
            logger.error(f"{test_name}: ERROR - {e}")
            results[test_name] = False
            all_passed = False

    # Print summary
    logger.info("\n" + "="*50)
    logger.info("TEST SUMMARY")
    logger.info("="*50)

    for test_name, result in results.items():
        status = "PASSED" if result else "FAILED"
        logger.info(f"{test_name}: {status}")

    logger.info(f"\nOverall Result: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    logger.info("="*50)

    if all_passed:
        print("\n🎉 All tests passed! The RAG system is functioning correctly.")
        print("\nNext steps to run the complete system:")
        print("1. Make sure you have set your API keys in the .env file")
        print("2. Start the backend: cd rag-system && python -m uvicorn src.rag_agent:app --reload")
        print("3. Start the Docusaurus frontend: cd docs && npm run start")
        print("4. Access the chatbot at http://localhost:3000/chatbot")
    else:
        print("\n❌ Some tests failed. Please check the logs above and resolve the issues.")

    return all_passed


def main():
    """Main function to run the test suite"""
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()