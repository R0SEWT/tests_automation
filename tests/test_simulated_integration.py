#!/usr/bin/env python3
"""
Simulate Integrated HU Correction Pipeline

Simulates the complete integrated pipeline without Jira extraction.
Uses mock data to test the RedactionAssistant integration.
"""

import asyncio
import logging
import json
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from integrated_hu_correction_pipeline import IntegratedHUCorrectionPipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SimulatedIntegratedPipeline(IntegratedHUCorrectionPipeline):
    """Simulated version of the integrated pipeline that uses mock HU content."""
    
    async def run_hu_extraction_pipeline(self, batch_size: int = 3) -> dict:
        """Override to use mock data instead of Jira extraction."""
        logger.info("🚀 Starting SIMULATED HU extraction pipeline")
        
        # Step 1: Analyze configuration (real)
        config_analysis = self.hu_pipeline.analyze_configuration()
        
        # Step 2: Extract test cases from Excel (real)
        test_cases = self.hu_pipeline.extract_test_cases_from_excel()
        
        # Step 3: Mock HU content (simulated)
        logger.info("📝 Creating mock HU content for testing...")
        
        # Create mock HU content for the first few HUs
        mock_hu_content = []
        hu_codes = list(self.hu_pipeline.hu_manager.get_available_hu_codes())[:5]  # First 5 HUs for testing
        
        for i, hu_code in enumerate(hu_codes):
            mock_hu = {
                'hu_code': hu_code,
                'issue_key': f'PROJECT-{1000 + i}',
                'title': f'Mock User Story {hu_code}',
                'description': f'Como usuario del sistema, quiero poder realizar la funcionalidad {hu_code} para mejorar mi experiencia de uso. Esta historia incluye validaciones, navegación y gestión de datos.'
            }
            mock_hu_content.append(mock_hu)
        
        self.hu_pipeline.extracted_hu_content = mock_hu_content
        logger.info(f"✅ Created mock content for {len(mock_hu_content)} HUs")
        
        # Step 4: Prepare correction data
        correction_data = self.hu_pipeline.prepare_correction_data()
        
        # Mock pipeline results
        pipeline_results = {
            'pipeline_completed': True,
            'config_analysis': config_analysis,
            'hu_content_extracted': len(mock_hu_content),
            'test_cases_extracted': len(test_cases),
            'correction_entries_ready': len(correction_data.get('correction_ready', [])),
            'correction_data': correction_data
        }
        
        logger.info("🎉 SIMULATED HU PROCESSING PIPELINE COMPLETED")
        logger.info(f"   Configuration analyzed: {config_analysis['total_hus']} HUs")
        logger.info(f"   Mock HU content created: {len(mock_hu_content)}")
        logger.info(f"   Test cases extracted: {len(test_cases)} worksheets")
        logger.info(f"   Correction entries ready: {len(correction_data.get('correction_ready', []))}")
        
        return pipeline_results


async def main():
    """Main function for the simulated integrated HU correction pipeline."""
    print("=== SIMULATED INTEGRATED HU CORRECTION PIPELINE ===")
    print("Testing complete workflow with mock data: Excel config → Mock HUs → Test cases → (Correction simulation)")

    pipeline = SimulatedIntegratedPipeline()

    try:
        # Run the simulated pipeline without RedactionAssistant (to avoid API requirements)
        print("\n1. Running HU extraction pipeline with mock data...")
        extraction_results = await pipeline.run_hu_extraction_pipeline(batch_size=2)
        
        if extraction_results['pipeline_completed']:
            print("\n✅ EXTRACTION PIPELINE COMPLETED SUCCESSFULLY")
            print(f"   HUs configured: {extraction_results['config_analysis']['total_hus']}")
            print(f"   Mock HU content: {extraction_results['hu_content_extracted']}")
            print(f"   Test case worksheets: {extraction_results['test_cases_extracted']}")
            print(f"   Correction entries ready: {extraction_results['correction_entries_ready']}")
            
            # Display sample data for verification
            print("\n📋 Sample correction data:")
            correction_ready = extraction_results['correction_data'].get('correction_ready', [])
            for i, entry in enumerate(correction_ready[:2]):  # Show first 2 entries
                print(f"   Entry {i+1}:")
                print(f"     HU Code: {entry['hu_code']}")
                print(f"     HU Title: {entry['hu_content']['title']}")
                print(f"     Test Cases: {len(entry['test_cases'])}")
                if entry['test_cases']:
                    sample_tc = entry['test_cases'][0]
                    print(f"     Sample TC: {sample_tc['test_case_id'][:30]}...")
                    print(f"     Sample Expected: {sample_tc['expected_result'][:50]}...")
            
            # Save results for inspection
            output_path = Path('data/processed/simulated_integration_results.json')
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(extraction_results, f, ensure_ascii=False, indent=2)
            
            print(f"\n📁 Results saved to: {output_path}")
            
            # Test data formatting for RedactionAssistant
            print("\n2. Testing data formatting for RedactionAssistant...")
            hus_str, test_cases_str, expected_str = pipeline._format_for_redaction_assistant(extraction_results['correction_data'])
            
            print(f"   Formatted HUs: {len(hus_str.splitlines())} lines")
            print(f"   Formatted Test Cases: {len(test_cases_str.splitlines())} lines")
            print(f"   Formatted Expected Results: {len(expected_str.splitlines())} lines")
            
            # Show samples
            print("\n📝 Sample formatted data:")
            print("   HU Sample:")
            hu_lines = hus_str.splitlines()
            if hu_lines:
                print(f"     {hu_lines[0][:100]}...")
            
            print("   Test Case Sample:")
            tc_lines = test_cases_str.splitlines()
            if tc_lines:
                print(f"     {tc_lines[0][:100]}...")
            
            print("   Expected Result Sample:")
            exp_lines = expected_str.splitlines()
            if exp_lines:
                print(f"     {exp_lines[0][:100]}...")

        else:
            print("❌ EXTRACTION PIPELINE FAILED")

    except Exception as e:
        logger.error(f"Simulated pipeline failed: {e}")
        print(f"❌ PIPELINE ERROR: {e}")


if __name__ == "__main__":
    asyncio.run(main())
