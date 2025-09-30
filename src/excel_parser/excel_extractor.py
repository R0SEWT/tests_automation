"""
Excel Test Case Extractor

This module provides functionality to extract test cases and expected results
from Excel files organized by worksheets.
"""

import pandas as pd
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class ExcelTestExtractor:
    """
    Extracts test cases and expected results from Excel files.

    Supports multiple worksheets where each worksheet represents a test suite
    or category of test cases.
    """

    def __init__(self, file_path: str):
        """
        Initialize the extractor with an Excel file path.

        Args:
            file_path: Path to the Excel file to process
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Excel file not found: {file_path}")

        self.workbook = None
        self._load_workbook()

    def _load_workbook(self):
        """Load the Excel workbook using pandas ExcelFile for efficient access."""
        try:
            self.workbook = pd.ExcelFile(self.file_path)
            logger.info(f"Loaded Excel file: {self.file_path}")
            logger.info(f"Available worksheets: {self.workbook.sheet_names}")
        except Exception as e:
            logger.error(f"Failed to load Excel file: {e}")
            raise

    def get_worksheet_names(self) -> List[str]:
        """
        Get the names of all worksheets in the Excel file.

        Returns:
            List of worksheet names
        """
        if self.workbook is None:
            raise RuntimeError("Workbook not loaded")
        return self.workbook.sheet_names

    def extract_test_cases_from_worksheet(self, worksheet_name: str) -> List[Dict]:
        """
        Extract test cases from a specific worksheet.

        Assumes the worksheet has columns: TestCaseID, Description, ExpectedResult
        The first row is treated as headers.

        Args:
            worksheet_name: Name of the worksheet to extract from

        Returns:
            List of test case dictionaries
        """
        if self.workbook is None:
            raise RuntimeError("Workbook not loaded")

        try:
            # Read the worksheet
            df = pd.read_excel(self.workbook, sheet_name=worksheet_name)

            # Clean column names (remove extra spaces, standardize case)
            df.columns = df.columns.str.strip().str.title()

            # Look for test case columns (flexible naming)
            test_case_columns = self._identify_columns(df.columns.tolist())

            if not test_case_columns['id'] or not test_case_columns['description']:
                logger.warning(f"Required columns not found in worksheet '{worksheet_name}'. "
                             f"Available columns: {df.columns.tolist()}")
                return []

            test_cases = []

            for idx, row in df.iterrows():
                test_case = {
                    'worksheet': worksheet_name,
                    'row_number': idx + 2,  # +2 because pandas is 0-indexed and Excel starts at 1, plus header
                    'test_case_id': str(row[test_case_columns['id']]).strip() if pd.notna(row[test_case_columns['id']]) else f"TC_{idx+1}",
                    'description': str(row[test_case_columns['description']]).strip() if pd.notna(row[test_case_columns['description']]) else "",
                    'expected_result': str(row[test_case_columns['expected']]).strip() if test_case_columns['expected'] and pd.notna(row[test_case_columns['expected']]) else "",
                    'additional_data': {}
                }

                # Add any additional columns as extra data
                for col in df.columns:
                    if col not in [test_case_columns['id'], test_case_columns['description'], test_case_columns['expected']]:
                        if pd.notna(row[col]):
                            test_case['additional_data'][col] = str(row[col]).strip()

                test_cases.append(test_case)

            logger.info(f"Extracted {len(test_cases)} test cases from worksheet '{worksheet_name}'")
            return test_cases

        except Exception as e:
            logger.error(f"Failed to extract test cases from worksheet '{worksheet_name}': {e}")
            return []

    def _identify_columns(self, columns: List[str]) -> Dict[str, Optional[str]]:
        """
        Identify which columns contain test case ID, description, and expected results.

        Uses flexible matching to handle variations in column naming.
        Supports both English and Spanish column names.

        Supported patterns:
        - ID: testcaseid, test_case_id, tc_id, id, test id, case id, nombre, name, caso, test case
        - Description: description, desc, descripción, test description, case description, steps, test steps, pasos, test step
        - Expected Result: expectedresult, expected_result, expected, result, resultado esperado, expected result, outcome

        Args:
            columns: List of column names

        Returns:
            Dictionary mapping column types to column names
        """
        # Convert to lowercase for matching
        lower_columns = [col.lower() for col in columns]

        # Patterns to match for each column type
        id_patterns = ['testcaseid', 'test_case_id', 'tc_id', 'id', 'test id', 'case id', 'nombre', 'name', 'caso', 'test case']
        desc_patterns = ['description', 'desc', 'descripción', 'test description', 'case description', 'steps', 'test steps', 'pasos', 'test step']
        expected_patterns = ['expectedresult', 'expected_result', 'expected', 'result', 'resultado esperado', 'expected result', 'outcome']

        def find_column(patterns):
            for pattern in patterns:
                for i, col in enumerate(lower_columns):
                    if pattern in col:
                        return columns[i]
            return None

        return {
            'id': find_column(id_patterns),
            'description': find_column(desc_patterns),
            'expected': find_column(expected_patterns)
        }

    def extract_all_test_cases(self) -> Dict[str, List[Dict]]:
        """
        Extract test cases from all worksheets in the Excel file.

        Returns:
            Dictionary mapping worksheet names to lists of test cases
        """
        results = {}
        for worksheet_name in self.get_worksheet_names():
            test_cases = self.extract_test_cases_from_worksheet(worksheet_name)
            if test_cases:  # Only include worksheets that have test cases
                results[worksheet_name] = test_cases

        logger.info(f"Extracted test cases from {len(results)} worksheets")
        return results

    def save_to_json(self, output_path: str, data: Dict[str, List[Dict]]):
        """
        Save extracted test cases to a JSON file.

        Args:
            output_path: Path where to save the JSON file
            data: Test case data to save
        """
        import json

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved test cases to: {output_file}")

    def extract_and_save(self, output_dir: str = "data/processed") -> str:
        """
        Extract all test cases and save them to a JSON file.

        Args:
            output_dir: Directory to save the output file

        Returns:
            Path to the saved file
        """
        test_cases = self.extract_all_test_cases()

        # Create output filename based on input file
        output_filename = f"{self.file_path.stem}_test_cases.json"
        output_path = Path(output_dir) / output_filename

        self.save_to_json(str(output_path), test_cases)

        return str(output_path)


def extract_from_excel_file(file_path: str, output_dir: str = "data/processed") -> str:
    """
    Convenience function to extract test cases from an Excel file.

    Args:
        file_path: Path to the Excel file
        output_dir: Directory to save the extracted data

    Returns:
        Path to the saved JSON file
    """
    extractor = ExcelTestExtractor(file_path)
    return extractor.extract_and_save(output_dir)