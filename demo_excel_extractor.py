#!/usr/bin/env python3
"""
Excel Test Case Extractor Demo

This script demonstrates how to use the ExcelTestExtractor to extract
test cases and expected results from Excel files.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from excel_parser.excel_extractor import ExcelTestExtractor, extract_from_excel_file


def demo_basic_extraction():
    """Demonstrate basic extraction from an Excel file."""
    print("=== Excel Test Case Extractor Demo ===\n")

    # Example Excel file path (you would replace this with your actual file)
    excel_file = "path/to/your/test_cases.xlsx"

    if not Path(excel_file).exists():
        print(f"Excel file not found: {excel_file}")
        print("Please update the excel_file path in this script.")
        return

    try:
        # Create extractor instance
        extractor = ExcelTestExtractor(excel_file)

        # Show available worksheets
        worksheets = extractor.get_worksheet_names()
        print(f"Found worksheets: {worksheets}\n")

        # Extract test cases from all worksheets
        all_test_cases = extractor.extract_all_test_cases()

        # Display results
        for worksheet, test_cases in all_test_cases.items():
            print(f"Worksheet: {worksheet}")
            print(f"Number of test cases: {len(test_cases)}\n")

            # Show first few test cases as examples
            for i, tc in enumerate(test_cases[:3]):  # Show first 3
                print(f"  Test Case {i+1}:")
                print(f"    ID: {tc['test_case_id']}")
                print(f"    Description: {tc['description'][:100]}{'...' if len(tc['description']) > 100 else ''}")
                print(f"    Expected Result: {tc['expected_result'][:100]}{'...' if len(tc['expected_result']) > 100 else ''}")
                if tc['additional_data']:
                    print(f"    Additional Data: {tc['additional_data']}")
                print()

        # Save to JSON file
        output_file = extractor.extract_and_save()
        print(f"Test cases saved to: {output_file}")

    except Exception as e:
        print(f"Error during extraction: {e}")


def demo_convenience_function():
    """Demonstrate using the convenience function."""
    print("\n=== Convenience Function Demo ===\n")

    excel_file = "path/to/your/test_cases.xlsx"
    output_dir = "data/processed"

    if not Path(excel_file).exists():
        print(f"Excel file not found: {excel_file}")
        return

    try:
        output_file = extract_from_excel_file(excel_file, output_dir)
        print(f"Extraction completed. Results saved to: {output_file}")

        # Show a summary of what was extracted
        import json
        with open(output_file, 'r') as f:
            data = json.load(f)

        total_cases = sum(len(cases) for cases in data.values())
        print(f"Total test cases extracted: {total_cases}")
        print(f"Worksheets processed: {list(data.keys())}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Run the demos
    demo_basic_extraction()
    demo_convenience_function()