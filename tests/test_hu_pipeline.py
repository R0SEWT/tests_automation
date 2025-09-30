#!/usr/bin/env python3
"""
Test HU Pipeline Integration

Tests the HU processing pipeline components individually and then together.
"""

import asyncio
import logging
import json
from pathlib import Path

from hu_pipeline import HUProcessingPipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_hu_pipeline():
    """Test the HU processing pipeline components."""
    print("=== TESTING HU PROCESSING PIPELINE ===")
    
    pipeline = HUProcessingPipeline()
    
    try:
        # Test 1: Configuration Analysis
        print("\n1. Testing Configuration Analysis...")
        config_analysis = pipeline.analyze_configuration()
        print(f"   ✅ Configuration analyzed: {config_analysis['total_hus']} HUs found")
        
        # Test 2: Test Case Extraction
        print("\n2. Testing Test Case Extraction...")
        test_cases = pipeline.extract_test_cases_from_excel()
        print(f"   ✅ Test cases extracted from {len(test_cases)} worksheets")
        
        total_test_cases = sum(len(cases) for cases in test_cases.values())
        print(f"   ✅ Total test cases: {total_test_cases}")
        
        # Show sample of extracted test cases
        if test_cases:
            sample_worksheet = list(test_cases.keys())[0]
            sample_cases = test_cases[sample_worksheet][:3]  # First 3 cases
            print(f"   Sample from '{sample_worksheet}':")
            for case in sample_cases:
                print(f"     - TC: {case['test_case_id'][:50]}...")
                print(f"       Desc: {case['description'][:50]}...")
                print(f"       Expected: {case['expected_result'][:50]}...")
        
        # Test 3: Prepare Correction Data (without Jira extraction)
        print("\n3. Testing Correction Data Preparation...")
        
        # Mock some HU content for testing
        pipeline.extracted_hu_content = [
            {
                'hu_code': 'USRNM001',
                'issue_key': 'PROJECT-123',
                'title': 'Test User Management HU',
                'description': 'As a user I want to manage my account settings so that I can customize my experience.'
            }
        ]
        
        correction_data = pipeline.prepare_correction_data()
        if correction_data:
            print(f"   ✅ Correction data prepared: {len(correction_data.get('correction_ready', []))} entries")
        else:
            print("   ⚠️  No correction data prepared (expected with mock data)")
        
        print("\n🎉 HU PIPELINE TEST COMPLETED SUCCESSFULLY")
        
        # Save test results
        test_results = {
            'config_analysis': config_analysis,
            'test_cases_summary': {
                'worksheets_processed': len(test_cases),
                'total_test_cases': total_test_cases,
                'worksheet_names': list(test_cases.keys())[:10]  # First 10 worksheet names
            },
            'correction_data_summary': {
                'entries_ready': len(correction_data.get('correction_ready', [])),
                'has_hu_content': len(pipeline.extracted_hu_content or []),
                'has_test_cases': len(pipeline.extracted_test_cases or {})
            }
        }
        
        # Save to file
        output_path = Path('data/processed/pipeline_test_results.json')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📁 Test results saved to: {output_path}")
        
        return test_results
        
    except Exception as e:
        logger.error(f"Pipeline test failed: {e}")
        print(f"❌ PIPELINE TEST FAILED: {e}")
        return None


async def main():
    """Main test function."""
    print("Starting HU Pipeline Integration Tests...")
    
    results = await test_hu_pipeline()
    
    if results:
        print("\n✅ ALL TESTS PASSED")
        print(f"   HUs configured: {results['config_analysis']['total_hus']}")
        print(f"   Worksheets processed: {results['test_cases_summary']['worksheets_processed']}")
        print(f"   Total test cases: {results['test_cases_summary']['total_test_cases']}")
    else:
        print("\n❌ TESTS FAILED")


if __name__ == "__main__":
    asyncio.run(main())