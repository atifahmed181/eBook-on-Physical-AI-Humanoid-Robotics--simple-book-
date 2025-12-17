"""
Content extractor for Docusaurus-based e-book
This script extracts content from the deployed Docusaurus site and prepares it for vectorization.
"""

import os
import requests
from bs4 import BeautifulSoup
import markdown
from pathlib import Path
import json
import time
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocusaurusContentExtractor:
    def __init__(self, base_url: str):
        """
        Initialize the content extractor

        Args:
            base_url: The base URL of the deployed Docusaurus site
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_page_content(self, url: str) -> Optional[str]:
        """
        Fetch content from a single page

        Args:
            url: The URL to fetch

        Returns:
            Page content as string or None if failed
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None

    def parse_html_content(self, html: str) -> Dict[str, str]:
        """
        Parse HTML content and extract relevant parts

        Args:
            html: Raw HTML content

        Returns:
            Dictionary with parsed content
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()

        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else ""

        # Extract main content (usually in main or article tags, or with specific classes)
        main_content = soup.find('main') or soup.find('article') or soup.find(class_='container')
        if not main_content:
            # Fallback to content divs commonly used in Docusaurus
            main_content = soup.find(class_='main-wrapper') or soup.find(id='content')

        content_text = main_content.get_text(strip=True) if main_content else ""

        # Extract headings for context
        headings = []
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
            headings.append(heading.get_text().strip())

        return {
            'title': title,
            'content': content_text,
            'headings': headings
        }

    def get_sitemap_urls(self) -> List[str]:
        """
        Attempt to get URLs from sitemap.xml or by navigating the site structure

        Returns:
            List of URLs to extract content from
        """
        urls = []

        # First, try to get from sitemap
        sitemap_url = f"{self.base_url}/sitemap.xml"
        try:
            response = self.session.get(sitemap_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'xml')
                for loc in soup.find_all('loc'):
                    url = loc.text.strip()
                    # Filter out non-documentation URLs
                    if '/docs/' in url or url.endswith('.html') or url == self.base_url:
                        urls.append(url)
        except Exception as e:
            logger.warning(f"Sitemap not available or failed to parse: {e}")

        # If sitemap didn't yield results, construct URLs based on known structure
        if not urls:
            logger.info("Generating URLs based on known documentation structure")

            # Base documentation pages
            base_docs = [
                "",
                "/docs/intro",
                "/docs/module1-ros2/index",
                "/docs/module1-ros2/nodes-topics-services",
                "/docs/module1-ros2/rclpy-bridge",
                "/docs/module1-ros2/urdf-for-humanoids",
                "/docs/module2-digital-twin/index",
                "/docs/module2-digital-twin/gazebo-physics",
                "/docs/module2-digital-twin/unity-rendering",
                "/docs/module2-digital-twin/simulating-sensors",
                "/docs/module3-ai-robot-brain/index",
                "/docs/module3-ai-robot-brain/nvidia-isaac-sim",
                "/docs/module3-ai-robot-brain/isaac-ros",
                "/docs/module3-ai-robot-brain/nav2-path-planning",
                "/docs/module4-vla/index",
                "/docs/module4-vla/voice-to-action",
                "/docs/module4-vla/cognitive-planning",
                "/docs/module4-vla/capstone-project"
            ]

            urls = [f"{self.base_url}{path}" for path in base_docs]

        return urls

    def extract_all_content(self) -> List[Dict]:
        """
        Extract content from all pages

        Returns:
            List of dictionaries containing page content
        """
        urls = self.get_sitemap_urls()
        all_content = []

        logger.info(f"Found {len(urls)} URLs to extract content from")

        for i, url in enumerate(urls, 1):
            logger.info(f"Processing ({i}/{len(urls)}): {url}")

            html_content = self.get_page_content(url)
            if html_content:
                parsed_content = self.parse_html_content(html_content)
                parsed_content['url'] = url
                all_content.append(parsed_content)

                # Be respectful to the server
                time.sleep(0.5)
            else:
                logger.warning(f"Failed to extract content from {url}")

        return all_content

def save_extracted_content(content_list: List[Dict], output_file: str):
    """
    Save extracted content to a JSON file

    Args:
        content_list: List of extracted content dictionaries
        output_file: Path to output file
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(content_list, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved extracted content to {output_file}")

def main():
    # Use the deployed URL from the docusaurus.config.ts
    base_url = "https://e-book-on-physical-ai-git-eb9bba-atif-ahmeds-projects-794cf321.vercel.app"

    extractor = DocusaurusContentExtractor(base_url)
    content = extractor.extract_all_content()

    # Save the extracted content
    output_file = "extracted_ebook_content.json"
    save_extracted_content(content, output_file)

    print(f"Extraction complete! Extracted content from {len(content)} pages.")
    print(f"Content saved to {output_file}")

if __name__ == "__main__":
    main()