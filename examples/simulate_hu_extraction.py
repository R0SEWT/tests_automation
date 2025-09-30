#!/usr/bin/env python3
"""
HU Content Extraction Simulator

Simulates HU content extraction for testing purposes without requiring
actual browser interaction. Useful for development and testing.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any

from src.hu_config_manager import HUConfigurationManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HUContentExtractionSimulator:
    """
    Simulates HU content extraction for testing and development.

    Creates mock HU data based on the Excel configuration without
    requiring actual Jira access or browser interaction.
    """

    def __init__(self, excel_path: str = 'data/USERNAME.xlsx'):
        self.excel_path = excel_path
        self.hu_manager = HUConfigurationManager(excel_path)

    def generate_mock_hu_data(self) -> List[Dict[str, Any]]:
        """
        Generate mock HU data based on Excel configuration.

        Returns:
            List of mock HU data dictionaries
        """
        hu_codes = self.hu_manager.get_available_hu_codes()
        jira_keys = self.hu_manager.get_jira_issue_keys()
        hu_links = self.hu_manager.get_hu_links()

        mock_data = []

        for i, (hu_code, jira_key) in enumerate(zip(hu_codes, jira_keys)):
            # Create mock HU data
            hu_data = {
                'issue_key': jira_key,
                'title': f'{hu_code} - Mock HU Title {i+1}',
                'description': f'This is mock content for {hu_code}. In a real scenario, this would contain the actual HU description extracted from Jira.',
                'status': 'Mock Status',
                'assignee': 'Mock Assignee',
                'created': '2025-01-01T00:00:00.000+0000',
                'updated': '2025-01-01T00:00:00.000+0000',
                'labels': ['mock', 'hu', hu_code.lower()],
                'url': hu_links.get(hu_code, ''),
                'hu_code': hu_code,
                'mock_data': True  # Flag to indicate this is mock data
            }

            mock_data.append(hu_data)

        logger.info(f"Generated {len(mock_data)} mock HU data entries")
        return mock_data

    def simulate_extraction_and_save(self, output_dir: str = 'data/raw/hus') -> Dict[str, Any]:
        """
        Simulate the complete extraction and saving process.

        Args:
            output_dir: Directory to save mock data

        Returns:
            Summary of the simulation
        """
        logger.info("Starting HU content extraction simulation")

        # Generate mock data
        mock_hu_data = self.generate_mock_hu_data()

        # Save to files (simulating the real process)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        saved_files = []

        for hu_data in mock_hu_data:
            hu_code = hu_data['hu_code']
            filename = f"{hu_code.replace('-', '_')}.json"
            filepath = output_path / filename

            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(hu_data, f, ensure_ascii=False, indent=2)

                saved_files.append(str(filepath))
                logger.info(f"Mock saved: {hu_code} -> {filepath}")

            except Exception as e:
                logger.error(f"Error saving mock data for {hu_code}: {e}")

        # Create content mapping
        content_mapping = {hu['hu_code']: hu for hu in mock_hu_data}

        summary = {
            'success': True,
            'total_simulated': len(mock_hu_data),
            'total_saved': len(saved_files),
            'output_directory': str(output_path),
            'saved_files': saved_files,
            'content_mapping': content_mapping,
            'hu_codes_mapped': len(content_mapping),
            'simulation_mode': True
        }

        logger.info(f"Simulation complete: {summary['total_simulated']} mock HUs processed")
        return summary


def main():
    """Main function for HU content extraction simulation."""
    print("=== HU CONTENT EXTRACTION SIMULATOR ===")
    print("Simulating HU content extraction without browser interaction...")

    simulator = HUContentExtractionSimulator()

    # Show configuration
    print(f"HU Prefix: {simulator.hu_manager.get_hu_prefix()}")
    print(f"Total HUs configured: {len(simulator.hu_manager.get_available_hu_codes())}")

    # Run simulation
    summary = simulator.simulate_extraction_and_save()

    if summary['success']:
        print("\n✅ SIMULATION COMPLETE")
        print(f"   Total HUs simulated: {summary['total_simulated']}")
        print(f"   Files saved: {summary['total_saved']}")
        print(f"   Output directory: {summary['output_directory']}")
        print(f"   HU codes mapped: {summary['hu_codes_mapped']}")

        # Show sample of saved files
        print("\nSample saved files:")
        for filepath in summary['saved_files'][:5]:
            print(f"   {filepath}")

        print("\n💡 This is mock data for testing. Run the real extractor with:")
        print("   python extract_hu_content.py")

    else:
        print(f"❌ SIMULATION FAILED")


if __name__ == "__main__":
    main()