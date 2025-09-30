#!/usr/bin/env python3
"""
HU Content Extractor

Extracts HU content from Jira using configuration from Excel file.
Integrates HUConfigurationManager with JiraScraper for automated content extraction.
"""

import asyncio
import json
import os
import logging
from pathlib import Path
from typing import List, Dict, Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.hu_config_manager import HUConfigurationManager
from src.jira_import.jira_scraper import JiraScraper
from src.core.base import BaseExtractor, ExtractionError
from src.core.utils import FileManager, BatchProcessor, Logger

logger = Logger.setup_logger(__name__)


class HUContentExtractor(BaseExtractor):
    """
    Extracts HU content from Jira using Excel configuration.

    Combines HU configuration management with Jira scraping to automatically
    extract and organize HU content for correction workflows.
    """

    def __init__(self, excel_path: str = 'data/USERNAME.xlsx'):
        """
        Initialize with Excel configuration file.

        Args:
            excel_path: Path to the Excel file containing HU configuration
        """
        super().__init__(excel_path)
        self.excel_path = excel_path
        self.hu_manager = HUConfigurationManager(excel_path)
        self.scraper = None

    def extract(self) -> Dict[str, Any]:
        """
        Extract all HU content (sync wrapper for async operation).
        
        Implementation of the abstract method from BaseExtractor.
        
        Returns:
            Dictionary containing extracted HU content and metadata
        """
        try:
            # Run the async extraction
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an event loop, create a new task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._async_extract())
                    return future.result()
            else:
                return asyncio.run(self._async_extract())
        except Exception as e:
            self.logger.error(f"Failed to extract HU content: {e}")
            raise ExtractionError(f"HU content extraction failed: {e}")

    async def _async_extract(self) -> Dict[str, Any]:
        """Async implementation of HU content extraction."""
        async with self as extractor:
            return await extractor.extract_and_save_all()

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize_scraper()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()

    async def initialize_scraper(self):
        """Initialize the Jira scraper."""
        self.scraper = JiraScraper()
        await self.scraper._setup_browser()
        logger.info("Jira scraper initialized")

    async def cleanup(self):
        """Clean up resources."""
        if self.scraper:
            await self.scraper.cleanup()

    async def extract_all_hu_content(self, batch_size: int = 10) -> List[Dict[str, Any]]:
        """
        Extract content from all configured HUs.

        Args:
            batch_size: Number of HUs to process in each batch

        Returns:
            List of extracted HU data
        """
        # Get all Jira issue keys from configuration
        issue_keys = self.hu_manager.get_jira_issue_keys()
        logger.info(f"Found {len(issue_keys)} HU issue keys to extract")

        if not issue_keys:
            logger.warning("No issue keys found in configuration")
            return []

        # Extract HU content in batches
        all_hu_data = []
        total_batches = (len(issue_keys) + batch_size - 1) // batch_size

        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(issue_keys))
            batch_keys = issue_keys[start_idx:end_idx]

            logger.info(f"Processing batch {batch_num + 1}/{total_batches} ({len(batch_keys)} issues)")

            try:
                if self.scraper is None:
                    raise RuntimeError("Scraper not initialized")

                batch_data = await self.scraper.get_multiple_issues_data(batch_keys)
                all_hu_data.extend(batch_data)

                # Log progress
                for hu_data in batch_data:
                    logger.info(f"Extracted: {hu_data.get('title', 'Unknown')}")

            except Exception as e:
                logger.error(f"Error processing batch {batch_num + 1}: {e}")
                # Continue with next batch

        logger.info(f"Successfully extracted {len(all_hu_data)} HU contents")
        return all_hu_data

    def save_hu_content(self, hu_data: List[Dict[str, Any]], output_dir: str = 'data/raw/hus') -> List[str]:
        """
        Save extracted HU content to JSON files.

        Args:
            hu_data: List of HU data dictionaries
            output_dir: Directory to save the files

        Returns:
            List of saved file paths
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        saved_files = []

        for hu in hu_data:
            # Use HU code as filename if available, otherwise use title
            hu_code = hu.get('issue_key', '').replace('-', '_')
            title = hu.get('title', 'untitled')

            if hu_code:
                filename = f"{hu_code}.json"
            else:
                # Clean title for filename
                filename = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip() or "untitled"
                filename = f"{filename}.json"

            filepath = output_path / filename

            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(hu, f, ensure_ascii=False, indent=2)

                saved_files.append(str(filepath))
                logger.info(f"Saved HU content: {filepath}")

            except Exception as e:
                logger.error(f"Error saving {filepath}: {e}")

        return saved_files

    def create_hu_content_mapping(self, hu_data: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Create mapping between HU codes and their content.

        Args:
            hu_data: List of HU data dictionaries

        Returns:
            Dictionary mapping HU codes to HU content
        """
        mapping = {}

        # Get HU code to issue key mapping
        hu_links = self.hu_manager.get_hu_links()
        issue_to_hu = {link.split('/')[-1]: code for code, link in hu_links.items()}

        for hu in hu_data:
            issue_key = hu.get('issue_key', '')
            if hu_code := issue_to_hu.get(issue_key):
                mapping[hu_code] = hu
            else:
                logger.warning(f"Could not map issue key {issue_key} to HU code")

        return mapping

    async def extract_and_save_all(self, output_dir: str = 'data/raw/hus', batch_size: int = 10) -> Dict[str, Any]:
        """
        Extract all HU content and save to files.

        Args:
            output_dir: Directory to save the files
            batch_size: Number of HUs to process in each batch

        Returns:
            Summary of the extraction process
        """
        logger.info("Starting HU content extraction process")

        # Extract all HU content
        hu_data = await self.extract_all_hu_content(batch_size=batch_size)

        if not hu_data:
            return {'success': False, 'message': 'No HU data extracted'}

        # Save to files
        saved_files = self.save_hu_content(hu_data, output_dir)

        # Create mapping for future use
        content_mapping = self.create_hu_content_mapping(hu_data)

        summary = {
            'success': True,
            'total_extracted': len(hu_data),
            'total_saved': len(saved_files),
            'output_directory': output_dir,
            'saved_files': saved_files,
            'content_mapping': content_mapping,
            'hu_codes_mapped': len(content_mapping)
        }

        logger.info(f"Extraction complete: {summary['total_extracted']} HUs extracted, {summary['total_saved']} files saved")
        return summary


async def main():
    """Main function for HU content extraction."""
    print("=== HU CONTENT EXTRACTOR ===")
    print("Extracting HU content from Jira using Excel configuration...")

    async with HUContentExtractor() as extractor:
        # Show configuration summary
        print(f"HU Prefix: {extractor.hu_manager.get_hu_prefix()}")
        print(f"Total HUs configured: {len(extractor.hu_manager.get_available_hu_codes())}")
        print(f"Jira issue keys: {len(extractor.hu_manager.get_jira_issue_keys())}")

        # Extract and save all HU content
        summary = await extractor.extract_and_save_all(batch_size=5)  # Smaller batches for testing

        if summary['success']:
            print("\n✅ EXTRACTION COMPLETE")
            print(f"   Total HUs extracted: {summary['total_extracted']}")
            print(f"   Files saved: {summary['total_saved']}")
            print(f"   Output directory: {summary['output_directory']}")
            print(f"   HU codes mapped: {summary['hu_codes_mapped']}")
        else:
            print(f"❌ EXTRACTION FAILED: {summary.get('message', 'Unknown error')}")


if __name__ == "__main__":
    asyncio.run(main())