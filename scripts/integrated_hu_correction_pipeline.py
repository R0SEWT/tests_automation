#!/usr/bin/env python3
"""
Integrated HU Correction Pipeline

Complete integration of HU processing with RedactionAssistant for automated correction.
Combines Excel configuration, Jira extraction, test case extraction, and automated correction.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from hu_pipeline import HUProcessingPipeline
from src.redactionAssistant.config import Config
from src.redactionAssistant.processor import Processor
from src.redactionAssistant.utils import save_data

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class IntegratedHUCorrectionPipeline:
    """
    Complete integrated pipeline for HU correction.
    
    Workflow:
    1. Extract HU configuration from Excel
    2. Extract HU content from Jira
    3. Extract test cases from Excel worksheets
    4. Process corrections using RedactionAssistant
    5. Generate corrected outputs
    """

    def __init__(self, excel_path: str = 'data/USERNAME.xlsx'):
        """
        Initialize the integrated pipeline.

        Args:
            excel_path: Path to the Excel file containing HU configuration
        """
        self.excel_path = excel_path
        self.hu_pipeline = HUProcessingPipeline(excel_path)
        self.config = Config()
        self.processor = None
        self.pipeline_results: Optional[Dict[str, Any]] = None

    def _format_for_redaction_assistant(self, correction_data: Dict[str, Any]) -> tuple[str, str, str]:
        """
        Format pipeline data for RedactionAssistant processing.

        Args:
            correction_data: Data from HU processing pipeline

        Returns:
            Tuple of (HUS, test_cases, expected_results) formatted as strings for RedactionAssistant
        """
        logger.info("Formatting data for RedactionAssistant")

        hu_texts = []
        test_case_texts = []
        expected_result_texts = []

        for entry in correction_data.get('correction_ready', []):
            hu_code = entry['hu_code']
            hu_content = entry['hu_content']
            worksheet_test_cases = entry['test_cases']

            # Format HU content
            hu_description = hu_content.get('description', '')
            if hu_title := hu_content.get('title'):
                hu_text = f"{hu_title}\n\n{hu_description}"
            else:
                hu_text = hu_description

            # Combine all HUs into one context string
            hu_texts.append(f"[{hu_code}] {hu_text}")

            # Format test cases and expected results
            for i, test_case in enumerate(worksheet_test_cases):
                tc_id = test_case.get('test_case_id', f'TC_{i+1}')
                description = test_case.get('description', '')
                expected = test_case.get('expected_result', '')

                # Format test case description with HU code
                test_case_text = f"{hu_code}-{tc_id} {description}"
                test_case_texts.append(test_case_text)

                # Format expected result with HU code
                expected_text = f"{hu_code}-{tc_id} {expected}"
                expected_result_texts.append(expected_text)

        # Convert to strings as expected by RedactionAssistant
        hus_str = "\n".join(hu_texts)
        test_cases_str = "\n".join(test_case_texts)
        expected_results_str = "\n".join(expected_result_texts)

        logger.info(f"Formatted for RedactionAssistant: {len(hu_texts)} HUs, {len(test_case_texts)} test cases, {len(expected_result_texts)} expected results")
        return hus_str, test_cases_str, expected_results_str

    async def run_hu_extraction_pipeline(self, batch_size: int = 3) -> Dict[str, Any]:
        """
        Run the HU extraction pipeline.

        Args:
            batch_size: Number of HUs to process in each batch

        Returns:
            Pipeline results
        """
        logger.info("🚀 Starting HU extraction pipeline")
        self.pipeline_results = await self.hu_pipeline.run_full_pipeline(batch_size=batch_size)
        return self.pipeline_results

    def initialize_redaction_assistant(self) -> None:
        """Initialize RedactionAssistant processor."""
        logger.info("Initializing RedactionAssistant")
        
        # Check if API key is available
        if not hasattr(self.config, 'API_KEY') or not self.config.API_KEY:
            logger.warning("No API key found for RedactionAssistant. Some features may not work.")
            # You can set a mock API key or handle this case differently
            api_key = "mock-api-key"
        else:
            api_key = self.config.API_KEY

        self.processor = Processor(self.config, api_key)

    def process_corrections(self) -> Dict[str, Any]:
        """
        Process corrections using RedactionAssistant.

        Returns:
            Correction results
        """
        if not self.pipeline_results:
            raise RuntimeError("Pipeline results not available. Run HU extraction pipeline first.")

        if not self.processor:
            self.initialize_redaction_assistant()

        logger.info("🔧 Processing corrections with RedactionAssistant")

        correction_data = self.pipeline_results['correction_data']
        
        # Format data for RedactionAssistant
        hus_str, test_cases_str, expected_results_str = self._format_for_redaction_assistant(correction_data)

        if not hus_str or not test_cases_str:
            logger.warning("No data to process for corrections")
            return {'success': False, 'message': 'No data available for correction'}

        try:
            # Process corrections using RedactionAssistant
            logger.info("Correcting test cases...")
            corrected_test_cases, tc_feedback = self.processor.cps_corregidas(hus_str, test_cases_str)

            logger.info("Correcting expected results...")
            corrected_expected, exp_feedback = self.processor.exp_corregidos(hus_str, corrected_test_cases, expected_results_str)

            # Combine feedback
            feedback_parts = [part for part in (tc_feedback, exp_feedback) if part]
            combined_feedback = "\n\n".join(feedback_parts)

            # Count lines for stats
            original_tc_count = len([line for line in test_cases_str.splitlines() if line.strip()])
            original_exp_count = len([line for line in expected_results_str.splitlines() if line.strip()])
            corrected_tc_count = len([line for line in corrected_test_cases.splitlines() if line.strip()])
            corrected_exp_count = len([line for line in corrected_expected.splitlines() if line.strip()])

            correction_results = {
                'success': True,
                'original_hus': hus_str,
                'original_test_cases': test_cases_str,
                'original_expected_results': expected_results_str,
                'corrected_test_cases': corrected_test_cases,
                'corrected_expected_results': corrected_expected,
                'feedback': combined_feedback,
                'stats': {
                    'total_hus': len([line for line in hus_str.splitlines() if line.strip()]),
                    'total_test_cases': original_tc_count,
                    'total_expected_results': original_exp_count,
                    'corrected_test_cases': corrected_tc_count,
                    'corrected_expected_results': corrected_exp_count
                }
            }

            logger.info(f"✅ Corrections completed: {corrected_tc_count} test cases, {corrected_exp_count} expected results")
            return correction_results

        except Exception as e:
            logger.error(f"Error during correction processing: {e}")
            return {'success': False, 'message': str(e)}

    def save_correction_results(self, correction_results: Dict[str, Any], output_dir: str = 'data/processed') -> Dict[str, str]:
        """
        Save correction results to files.

        Args:
            correction_results: Results from correction processing
            output_dir: Directory to save the results

        Returns:
            Dictionary with paths to saved files
        """
        logger.info("💾 Saving correction results")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        saved_files = {}

        try:
            # Save using RedactionAssistant format
            corrected_test_cases = correction_results.get('corrected_test_cases', '')
            corrected_expected = correction_results.get('corrected_expected_results', '')
            feedback = correction_results.get('feedback', '')

            # Define output paths
            tc_path = output_path / 'corrected_test_cases.txt'
            exp_path = output_path / 'corrected_expected_results.txt'
            feedback_path = output_path / 'correction_feedback.txt'

            # Save using RedactionAssistant's save function
            save_data(corrected_test_cases, corrected_expected, feedback, 
                     str(tc_path), str(exp_path), str(feedback_path))

            saved_files.update({
                'test_cases': str(tc_path),
                'expected_results': str(exp_path),
                'feedback': str(feedback_path)
            })

            # Also save complete results as JSON
            json_path = output_path / 'complete_correction_results.json'
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(correction_results, f, ensure_ascii=False, indent=2)
            saved_files['complete_results'] = str(json_path)

            # Save pipeline results
            if self.pipeline_results:
                pipeline_path = output_path / 'pipeline_results.json'
                with open(pipeline_path, 'w', encoding='utf-8') as f:
                    json.dump(self.pipeline_results, f, ensure_ascii=False, indent=2)
                saved_files['pipeline_results'] = str(pipeline_path)

            logger.info(f"✅ Correction results saved to {len(saved_files)} files")
            return saved_files

        except Exception as e:
            logger.error(f"Error saving correction results: {e}")
            return {}

    async def run_complete_pipeline(self, batch_size: int = 3, output_dir: str = 'data/processed') -> Dict[str, Any]:
        """
        Run the complete integrated pipeline.

        Args:
            batch_size: Number of HUs to process in each batch
            output_dir: Directory to save the results

        Returns:
            Complete pipeline results
        """
        logger.info("🚀 STARTING COMPLETE INTEGRATED HU CORRECTION PIPELINE")

        try:
            # Step 1: Run HU extraction pipeline
            pipeline_results = await self.run_hu_extraction_pipeline(batch_size=batch_size)

            if not pipeline_results.get('pipeline_completed'):
                return {'success': False, 'message': 'HU extraction pipeline failed'}

            # Step 2: Process corrections
            correction_results = self.process_corrections()

            if not correction_results.get('success'):
                return {'success': False, 'message': f"Correction processing failed: {correction_results.get('message')}"}

            # Step 3: Save results
            saved_files = self.save_correction_results(correction_results, output_dir)

            # Complete results summary
            complete_results = {
                'success': True,
                'pipeline_completed': True,
                'extraction_results': pipeline_results,
                'correction_results': correction_results,
                'saved_files': saved_files,
                'summary': {
                    'total_hus_configured': pipeline_results['config_analysis']['total_hus'],
                    'hu_content_extracted': pipeline_results['hu_content_extracted'],
                    'test_cases_worksheets': pipeline_results['test_cases_extracted'],
                    'correction_entries_processed': pipeline_results['correction_entries_ready'],
                    'corrected_test_cases': len([line for line in correction_results.get('corrected_test_cases', '').splitlines() if line.strip()]),
                    'corrected_expected_results': len([line for line in correction_results.get('corrected_expected_results', '').splitlines() if line.strip()]),
                    'output_files': len(saved_files)
                }
            }

            logger.info("🎉 COMPLETE INTEGRATED PIPELINE FINISHED SUCCESSFULLY")
            logger.info(f"   HUs configured: {complete_results['summary']['total_hus_configured']}")
            logger.info(f"   HU content extracted: {complete_results['summary']['hu_content_extracted']}")
            logger.info(f"   Test case worksheets: {complete_results['summary']['test_cases_worksheets']}")
            logger.info(f"   Corrected test cases: {complete_results['summary']['corrected_test_cases']}")
            logger.info(f"   Corrected expected results: {complete_results['summary']['corrected_expected_results']}")
            logger.info(f"   Output files generated: {complete_results['summary']['output_files']}")

            return complete_results

        except Exception as e:
            logger.error(f"Complete pipeline failed: {e}")
            return {'success': False, 'message': str(e)}


async def main():
    """Main function for the integrated HU correction pipeline."""
    print("=== INTEGRATED HU CORRECTION PIPELINE ===")
    print("Complete workflow: Excel config → Jira extraction → Test cases → RedactionAssistant correction")

    pipeline = IntegratedHUCorrectionPipeline()

    try:
        # Run the complete pipeline
        results = await pipeline.run_complete_pipeline(batch_size=2)  # Small batches for testing

        if results['success']:
            print("\n✅ INTEGRATED PIPELINE COMPLETED SUCCESSFULLY")
            print(f"   HUs configured: {results['summary']['total_hus_configured']}")
            print(f"   HU content extracted: {results['summary']['hu_content_extracted']}")
            print(f"   Test case worksheets: {results['summary']['test_cases_worksheets']}")
            print(f"   Corrected test cases: {results['summary']['corrected_test_cases']}")
            print(f"   Corrected expected results: {results['summary']['corrected_expected_results']}")
            print(f"   Output files: {results['summary']['output_files']}")
            
            print("\n📁 Generated files:")
            for file_type, file_path in results['saved_files'].items():
                print(f"   {file_type}: {file_path}")

        else:
            print(f"❌ INTEGRATED PIPELINE FAILED: {results.get('message', 'Unknown error')}")

    except Exception as e:
        logger.error(f"Integrated pipeline execution failed: {e}")
        print(f"❌ PIPELINE ERROR: {e}")


if __name__ == "__main__":
    asyncio.run(main())