"""
Validator for the RAG system
This script validates semantic retrieval from the vector database.
"""

import json
import cohere
import os
from typing import List, Dict
import logging
from embedder import QdrantVectorStore, CohereEmbedder

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGValidator:
    def __init__(self, cohere_api_key: str = None):
        """
        Initialize the RAG validator

        Args:
            cohere_api_key: Cohere API key for generating query embeddings
        """
        self.embedder = CohereEmbedder(cohere_api_key)
        self.vector_store = QdrantVectorStore(collection_name="ebook_rag")

    def validate_retrieval(self, queries: List[str], expected_results: List[List[str]] = None) -> Dict:
        """
        Validate retrieval quality for a set of queries

        Args:
            queries: List of query strings to test
            expected_results: Optional list of expected results for each query

        Returns:
            Dictionary with validation results
        """
        results = {
            "queries": [],
            "retrieval_success": True,
            "average_recall": 0.0,
            "average_precision": 0.0,
            "total_queries": len(queries),
            "failed_queries": 0
        }

        total_recall = 0.0
        total_precision = 0.0
        successful_queries = 0

        for i, query in enumerate(queries):
            logger.info(f"Validating query {i+1}/{len(queries)}: {query[:50]}...")

            try:
                # Generate embedding for the query
                query_embeddings = self.embedder.embed_texts([query])
                query_embedding = query_embeddings[0]

                # Retrieve results from vector store
                retrieved_docs = self.vector_store.search(query_embedding, top_k=5)

                query_result = {
                    "query": query,
                    "retrieved_docs": retrieved_docs,
                    "success": True,
                    "recall": 0.0,
                    "precision": 0.0
                }

                # If expected results are provided, calculate recall and precision
                if expected_results and i < len(expected_results):
                    expected = set(expected_results[i])
                    retrieved = set([doc["text"][:100] for doc in retrieved_docs])  # Use first 100 chars as identifier

                    # Calculate recall and precision
                    intersection = expected.intersection(retrieved)
                    recall = len(intersection) / len(expected) if expected else 0.0
                    precision = len(intersection) / len(retrieved) if retrieved else 0.0

                    query_result["recall"] = recall
                    query_result["precision"] = precision
                    query_result["expected_results"] = expected_results[i]

                    total_recall += recall
                    total_precision += precision

                results["queries"].append(query_result)
                successful_queries += 1

            except Exception as e:
                logger.error(f"Failed to validate query '{query[:30]}...': {e}")
                results["queries"].append({
                    "query": query,
                    "success": False,
                    "error": str(e)
                })
                results["failed_queries"] += 1

        # Calculate averages if there were successful queries with expected results
        if successful_queries > 0 and expected_results:
            results["average_recall"] = total_recall / successful_queries
            results["average_precision"] = total_precision / successful_queries

        results["retrieval_success"] = results["failed_queries"] == 0

        return results

    def run_comprehensive_validation(self) -> Dict:
        """
        Run comprehensive validation with predefined test queries

        Returns:
            Dictionary with comprehensive validation results
        """
        # Define test queries related to the e-book topics
        test_queries = [
            "What is ROS 2 and its significance in robotics?",
            "How to set up a robotic nervous system?",
            "What are the components of NVIDIA Isaac?",
            "Explain digital twin technology in robotics",
            "How does Gazebo physics simulation work?",
            "What are Vision-Language-Action systems?",
            "How to implement cognitive planning in robots?",
            "What is URDF and its role in humanoid robotics?",
            "Explain ROS 2 nodes, topics, and services",
            "How to simulate sensors in digital twins?"
        ]

        logger.info("Running comprehensive validation with {} test queries".format(len(test_queries)))

        validation_results = self.validate_retrieval(test_queries)

        return validation_results

    def check_coverage(self) -> Dict:
        """
        Check how well the vector database covers the original content

        Returns:
            Dictionary with coverage analysis
        """
        try:
            # Load original chunks to assess coverage
            with open("chunks.json", "r", encoding="utf-8") as f:
                original_chunks = json.load(f)

            # Count total chunks in vector store
            collection_info = self.vector_store.client.get_collection("ebook_rag")
            vector_count = collection_info.points_count

            coverage_analysis = {
                "original_chunks_count": len(original_chunks),
                "stored_vectors_count": vector_count,
                "coverage_percentage": (vector_count / len(original_chunks)) * 100 if original_chunks else 0,
                "is_complete": vector_count == len(original_chunks)
            }

            return coverage_analysis
        except Exception as e:
            logger.error(f"Error checking coverage: {e}")
            return {"error": str(e)}

    def print_validation_report(self, validation_results: Dict, coverage_analysis: Dict = None):
        """
        Print a formatted validation report

        Args:
            validation_results: Results from validation
            coverage_analysis: Coverage analysis results
        """
        print("\n" + "="*60)
        print("RAG SYSTEM VALIDATION REPORT")
        print("="*60)

        print(f"\n📊 RETRIEVAL STATISTICS:")
        print(f"   Total Queries: {validation_results['total_queries']}")
        print(f"   Successful: {validation_results['total_queries'] - validation_results['failed_queries']}")
        print(f"   Failed: {validation_results['failed_queries']}")
        print(f"   Success Rate: {(1 - validation_results['failed_queries']/validation_results['total_queries'])*100:.2f}%")

        if validation_results['average_recall'] > 0:
            print(f"\n📈 ACCURACY METRICS:")
            print(f"   Average Recall: {validation_results['average_recall']:.3f}")
            print(f"   Average Precision: {validation_results['average_precision']:.3f}")

        if coverage_analysis:
            print(f"\n🔍 COVERAGE ANALYSIS:")
            print(f"   Original Chunks: {coverage_analysis.get('original_chunks_count', 'N/A')}")
            print(f"   Stored Vectors: {coverage_analysis.get('stored_vectors_count', 'N/A')}")
            print(f"   Coverage: {coverage_analysis.get('coverage_percentage', 'N/A'):.2f}%")
            print(f"   Complete: {'Yes' if coverage_analysis.get('is_complete', False) else 'No'}")

        print(f"\n✅ Retrieval Success: {'Yes' if validation_results['retrieval_success'] else 'No'}")

        # Show sample results
        print(f"\n📋 SAMPLE RETRIEVAL RESULTS:")
        for i, query_result in enumerate(validation_results['queries'][:3]):  # Show first 3
            if query_result.get('success', False):
                print(f"\n   Query {i+1}: {query_result['query'][:60]}...")
                print(f"   Retrieved {len(query_result['retrieved_docs'])} documents")
                if query_result['retrieved_docs']:
                    top_doc = query_result['retrieved_docs'][0]
                    print(f"   Top result score: {top_doc['score']:.3f}")
                    print(f"   Top result preview: {top_doc['text'][:100]}...")
            else:
                print(f"\n   Query {i+1}: FAILED - {query_result.get('error', 'Unknown error')}")

        print("\n" + "="*60)


def main():
    # Initialize validator
    try:
        validator = RAGValidator()

        # Run comprehensive validation
        validation_results = validator.run_comprehensive_validation()

        # Check coverage
        coverage_analysis = validator.check_coverage()

        # Print validation report
        validator.print_validation_report(validation_results, coverage_analysis)

        # Save validation results
        with open("validation_results.json", "w", encoding="utf-8") as f:
            json.dump(validation_results, f, ensure_ascii=False, indent=2)

        print(f"\nValidation results saved to validation_results.json")

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        print(f"Validation failed: {e}")


if __name__ == "__main__":
    main()