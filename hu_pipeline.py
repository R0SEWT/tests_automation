#!/usr/bin/env python3
"""
HU Processing Pipeline

Complete pipeline for HU processing: from Excel configuration to content extraction
and preparation for automated correction using RedactionAssistant.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import json

from src.hu_config_manager import HUConfigurationManager
from src.excel_parser.excel_extractor import ExcelTestExtractor
from src.core.base import PipelineError
from src.core.utils import FileManager, BatchProcessor, Logger

logger = Logger.setup_logger(__name__)


class HUProcessingPipeline:
    """
    Complete pipeline for HU processing from Excel to correction-ready data.

    Orchestrates the entire workflow:
    1. Analyze Excel configuration
    2. Extract HU content from Jira
    3. Extract test cases from Excel worksheets
    4. Prepare data for RedactionAssistant
    """

    def __init__(self, excel_path: str = 'data/USERNAME.xlsx'):
        """
        Initialize the HU processing pipeline.

        Args:
            excel_path: Path to the Excel file containing HU configuration
        """
        self.excel_path = excel_path
        self.logger = logger
        self.hu_manager = HUConfigurationManager(excel_path)
        self.extracted_hu_content: Optional[List[Dict[str, Any]]] = None
        self.extracted_test_cases: Optional[Dict[str, List[Dict]]] = None

    def run(self, input_data: Any = None, batch_size: int = 5) -> Dict[str, Any]:
        """
        Run the complete HU processing pipeline.

        Args:
            input_data: Not used for this pipeline
            batch_size: Number of HUs to process in each batch

        Returns:
            Complete pipeline results
        """
        try:
            # Run the async pipeline in a sync wrapper
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an event loop, create a new task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.run_full_pipeline(batch_size))
                    return future.result()
            else:
                return asyncio.run(self.run_full_pipeline(batch_size))
        except Exception as e:
            self.logger.error(f"Pipeline execution failed: {e}")
            raise PipelineError(f"HU processing pipeline failed: {e}")

    def analyze_configuration(self) -> Dict[str, Any]:
        """
        Analyze the HU configuration from Excel.

        Returns:
            Configuration analysis results
        """
        logger.info("=== ANALYZING HU CONFIGURATION ===")

        analysis = {
            'hu_prefix': self.hu_manager.get_hu_prefix(),
            'total_hus': len(self.hu_manager.get_available_hu_codes()),
            'jira_issue_keys': self.hu_manager.get_jira_issue_keys(),
            'worksheet_mapping': self.hu_manager.get_worksheet_mapping(),
            'validation_warnings': self.hu_manager.validate_configuration()
        }

        logger.info(f"HU Prefix: {analysis['hu_prefix']}")
        logger.info(f"Total HUs configured: {analysis['total_hus']}")
        logger.info(f"Jira issue keys: {len(analysis['jira_issue_keys'])}")

        if analysis['validation_warnings']:
            logger.warning(f"Validation warnings: {len(analysis['validation_warnings'])}")
            for warning in analysis['validation_warnings']:
                logger.warning(f"  ⚠️  {warning}")
        else:
            logger.info("✅ Configuration validation passed")

        return analysis

    async def extract_hu_content(self, batch_size: int = 5) -> List[Dict[str, Any]]:
        """
        Extract HU content from Jira using the configuration.

        Args:
            batch_size: Number of HUs to process in each batch

        Returns:
            List of extracted HU content
        """
        logger.info("=== EXTRACTING HU CONTENT FROM JIRA ===")

        # Import here to avoid circular imports and make it optional
        from extract_hu_content import HUContentExtractor

        async with HUContentExtractor(self.excel_path) as extractor:
            summary = await extractor.extract_and_save_all(batch_size=batch_size)

            if summary['success']:
                logger.info(f"✅ Successfully extracted {summary['total_extracted']} HU contents")
                self.extracted_hu_content = [summary['content_mapping'][hu_code]
                                           for hu_code in self.hu_manager.get_available_hu_codes()
                                           if hu_code in summary['content_mapping']]
                return self.extracted_hu_content
            else:
                logger.error(f"❌ HU content extraction failed: {summary.get('message')}")
                return []

    def extract_test_cases_from_excel(self) -> Dict[str, List[Dict]]:
        """
        Extract test cases from Excel worksheets.

        Returns:
            Dictionary mapping worksheet names to test case lists
        """
        logger.info("=== EXTRACTING TEST CASES FROM EXCEL WORKSHEETS ===")

        worksheet_mapping = self.hu_manager.get_worksheet_mapping()
        test_cases = {}

        for hu_code, worksheet_name in worksheet_mapping.items():
            try:
                logger.info(f"Extracting test cases from worksheet: {worksheet_name}")

                # Create a temporary Excel extractor for this specific worksheet
                # Note: This is a simplified approach. In production, you might want to
                # extract all worksheets at once for efficiency
                extractor = ExcelTestExtractor(self.excel_path)
                if worksheet_test_cases := extractor.extract_test_cases_from_worksheet(worksheet_name):
                    test_cases[worksheet_name] = worksheet_test_cases
                    logger.info(f"  Found {len(worksheet_test_cases)} test cases in {worksheet_name}")
                else:
                    logger.warning(f"  No test cases found in {worksheet_name}")

            except Exception as e:
                logger.error(f"Error extracting test cases from {worksheet_name}: {e}")

        self.extracted_test_cases = test_cases
        logger.info(f"✅ Extracted test cases from {len(test_cases)} worksheets")
        return test_cases

    def prepare_correction_data(self) -> Dict[str, Any]:
        """
        Prepare data for RedactionAssistant correction.

        Returns:
            Structured data ready for automated correction
        """
        logger.info("=== PREPARING CORRECTION DATA ===")

        if not self.extracted_hu_content:
            logger.warning("No HU content available. Run extract_hu_content() first.")
            return {}

        if not self.extracted_test_cases:
            logger.warning("No test cases available. Run extract_test_cases_from_excel() first.")
            return {}

        # Create HU code to content mapping
        hu_content_map = {hu['hu_code']: hu for hu in self.extracted_hu_content}

        # Prepare correction-ready data
        correction_data = {
            'hu_prefix': self.hu_manager.get_hu_prefix(),
            'total_hus': len(self.extracted_hu_content),
            'hu_content': hu_content_map,
            'test_cases': self.extracted_test_cases,
            'worksheet_mapping': self.hu_manager.get_worksheet_mapping(),
            'correction_ready': []
        }

        # Create correction-ready entries
        for hu_code, worksheet_name in self.hu_manager.get_worksheet_mapping().items():
            if hu_code in hu_content_map and worksheet_name in self.extracted_test_cases:
                hu_content = hu_content_map[hu_code]
                test_cases = self.extracted_test_cases[worksheet_name]

                correction_entry = {
                    'hu_code': hu_code,
                    'worksheet': worksheet_name,
                    'hu_content': hu_content,
                    'test_cases': test_cases,
                    'jira_issue_key': hu_content.get('issue_key'),
                    'hu_title': hu_content.get('title'),
                    'hu_description': hu_content.get('description')
                }

                correction_data['correction_ready'].append(correction_entry)

        logger.info(f"✅ Prepared {len(correction_data['correction_ready'])} HU entries for correction")
        return correction_data

    async def run_full_pipeline(self, batch_size: int = 5) -> Dict[str, Any]:
        """
        Run the complete HU processing pipeline.

        Args:
            batch_size: Number of HUs to process in each batch

        Returns:
            Complete pipeline results
        """
        logger.info("🚀 STARTING HU PROCESSING PIPELINE")

        # Step 1: Analyze configuration
        config_analysis = self.analyze_configuration()

        # Step 2: Extract HU content from Jira
        hu_content = await self.extract_hu_content(batch_size=batch_size)

        # Step 3: Extract test cases from Excel
        test_cases = self.extract_test_cases_from_excel()

        # Step 4: Prepare correction data
        correction_data = self.prepare_correction_data()

        pipeline_results = {
            'pipeline_completed': True,
            'config_analysis': config_analysis,
            'hu_content_extracted': len(hu_content),
            'test_cases_extracted': len(test_cases),
            'correction_entries_ready': len(correction_data.get('correction_ready', [])),
            'correction_data': correction_data
        }

        logger.info("🎉 HU PROCESSING PIPELINE COMPLETED")
        logger.info(f"   Configuration analyzed: {config_analysis['total_hus']} HUs")
        logger.info(f"   HU content extracted: {len(hu_content)}")
        logger.info(f"   Test cases extracted: {len(test_cases)} worksheets")
        logger.info(f"   Correction entries ready: {len(correction_data.get('correction_ready', []))}")

        return pipeline_results

    def save_pipeline_results(self, results: Dict[str, Any], output_dir: str = 'data/processed') -> str:
        """
        Save pipeline results to JSON file.

        Args:
            results: Pipeline results to save
            output_dir: Directory to save the results

        Returns:
            Path to the saved file
        """
        import json

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        output_file = output_path / 'hu_pipeline_results.json'

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        logger.info(f"Pipeline results saved to: {output_file}")
        return str(output_file)


async def main():
    """Main function for HU processing pipeline."""
    print("=== HU PROCESSING PIPELINE ===")
    print("Complete workflow: Excel config → Jira extraction → Test cases → Correction ready")

    pipeline = HUProcessingPipeline()

    try:
        # Run the full pipeline
        results = await pipeline.run_full_pipeline(batch_size=3)  # Small batches for testing

        if results['pipeline_completed']:
            print("\n✅ PIPELINE COMPLETED SUCCESSFULLY")
            print(f"   HUs configured: {results['config_analysis']['total_hus']}")
            print(f"   HU content extracted: {results['hu_content_extracted']}")
            print(f"   Test cases extracted: {results['test_cases_extracted']} worksheets")
            print(f"   Correction entries ready: {results['correction_entries_ready']}")

            # Save results
            results_file = pipeline.save_pipeline_results(results)
            print(f"   Results saved to: {results_file}")

        else:
            print("❌ PIPELINE FAILED")

    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        print(f"❌ PIPELINE ERROR: {e}")


if __name__ == "__main__":
    asyncio.run(main())