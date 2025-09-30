"""
Excel Test Case Extractor

This module provides functionality to extract test cases and expected results
from Excel files organized by worksheets.
"""

import pandas as pd
import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

from ..core.base import BaseExtractor, ExtractionError
from ..core.utils import TextProcessor, Logger, FileManager

logger = Logger.setup_logger(__name__)


class ExcelTestExtractor(BaseExtractor):
    """
    Extractor for test cases from Excel files.
    
    This class reads Excel files and extracts test cases from specified worksheets.
    It can handle multiple worksheets and attempts to identify test case columns
    automatically based on common naming patterns.
    """
    
    COLUMN_PATTERNS = {
        'id': [
            'testcaseid', 'test_case_id', 'test case id', 'id', 'case_id', 
            'caseid', 'tc_id', 'tcid', 'test id', 'test_id', 'caso', 'caso_id'
        ],
        'description': [
            'description', 'desc', 'test description', 'test_description',
            'case description', 'case_description', 'scenario', 'test case',
            'test_case', 'descripción', 'descripcion', 'prueba', 'detalle'
        ],
        'expected': [
            'expected', 'expectedresult', 'expected_result', 'expected result',
            'result', 'esperado', 'resultado_esperado', 'resultado esperado',
            'outcome', 'expected_outcome', 'expected outcome'
        ]
    }

    def __init__(self, file_path: str):
        """
        Initialize the ExcelTestExtractor.

        Args:
            file_path: Path to the Excel file to extract from
        """
        super().__init__(file_path)
        self.workbook = None
        self._file_path = Path(file_path)
        # Load the workbook automatically
        self.load_workbook()

    @property
    def file_path(self) -> Path:
        """Get the file path."""
        return self._file_path

    def extract(self) -> Dict[str, Any]:
        """
        Extract all test cases from the Excel file.
        
        Implementation of the abstract method from BaseExtractor.
        
        Returns:
            Dictionary containing extracted test cases and metadata
        """
        if not self.load_workbook():
            return {'success': False, 'error': 'Failed to load workbook', 'test_cases': []}
        
        try:
            all_test_cases = self.extract_all_test_cases()
            # Flatten the test cases from all worksheets
            flattened_test_cases = []
            for worksheet_test_cases in all_test_cases.values():
                flattened_test_cases.extend(worksheet_test_cases)
            
            return {
                'success': True,
                'file_path': str(self.file_path),
                'total_test_cases': len(flattened_test_cases),
                'test_cases': flattened_test_cases,
                'worksheets_processed': len(all_test_cases)
            }
        except Exception as e:
            self.logger.error(f"Failed to extract test cases: {e}")
            return {'success': False, 'error': str(e), 'test_cases': []}

    def load_workbook(self) -> bool:
        """
        Load the Excel workbook from file.

        Returns:
            True if successful, False otherwise
        """
        try:
            import openpyxl
            self.workbook = openpyxl.load_workbook(str(self.file_path))
            self.logger.info(f"Loaded workbook: {self.file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load workbook: {e}")
            return False

    def get_worksheet_names(self) -> List[str]:
        """
        Get list of available worksheet names in the workbook.

        Returns:
            List of worksheet names
        """
        if self.workbook is None:
            self.logger.warning("Workbook not loaded")
            return []
        
        try:
            # Use openpyxl to get sheet names
            return list(self.workbook.sheetnames)
        except Exception as e:
            self.logger.error(f"Failed to get sheet names: {e}")
            return []

    def extract_test_cases_from_worksheet(self, worksheet_name: str) -> List[Dict]:
        """
        Extract test cases from a specific worksheet.

        Args:
            worksheet_name: Name of the worksheet to extract from

        Returns:
            List of test case dictionaries
        """
        if self.workbook is None:
            raise RuntimeError("Workbook not loaded")

        try:
            # Read the worksheet
            df = self._read_worksheet(worksheet_name)
            if df is None:
                return []

            # Identify columns
            test_case_columns = self._identify_columns(df.columns.tolist())
            
            if not self._validate_required_columns(test_case_columns, worksheet_name):
                return []

            # Extract test cases
            test_cases = []
            for row_idx, (idx, row) in enumerate(df.iterrows()):
                test_case = self._create_test_case_dict(
                    worksheet_name, row_idx, row, test_case_columns, df.columns.tolist()
                )
                test_cases.append(test_case)

            self.logger.info(f"Extracted {len(test_cases)} test cases from worksheet '{worksheet_name}'")
            return test_cases

        except Exception as e:
            self.logger.error(f"Failed to extract test cases from worksheet '{worksheet_name}': {e}")
            return []

    def _read_worksheet(self, worksheet_name: str) -> Optional[pd.DataFrame]:
        """Read and preprocess a worksheet."""
        try:
            df = pd.read_excel(str(self.file_path), sheet_name=worksheet_name)
            # Clean column names (remove extra spaces, standardize case)
            df.columns = df.columns.str.strip().str.title()
            return df
        except Exception as e:
            self.logger.error(f"Failed to read worksheet '{worksheet_name}': {e}")
            return None

    def _validate_required_columns(self, test_case_columns: Dict[str, Optional[str]], worksheet_name: str) -> bool:
        """Validate that required columns are present."""
        if not test_case_columns['id'] or not test_case_columns['description']:
            self.logger.warning(
                f"Required columns not found in worksheet '{worksheet_name}'. "
                f"Available columns: {list(test_case_columns.keys())}"
            )
            return False
        return True

    def _create_test_case_dict(
        self, 
        worksheet_name: str, 
        idx: int, 
        row: pd.Series, 
        test_case_columns: Dict[str, Optional[str]], 
        all_columns: List[str]
    ) -> Dict:
        """Create a test case dictionary from a row."""
        # Extract basic fields
        test_case_id = self._extract_cell_value(row, test_case_columns['id'], f"TC_{idx+1}")
        description = self._extract_cell_value(row, test_case_columns['description'], "")
        expected_result = self._extract_cell_value(row, test_case_columns['expected'], "")

        test_case = {
            'worksheet': worksheet_name,
            'row_number': idx + 2,  # +2 for pandas 0-index + header
            'test_case_id': test_case_id,
            'description': description,
            'expected_result': expected_result,
            'additional_data': {}
        }

        # Add additional columns
        excluded_columns = {test_case_columns['id'], test_case_columns['description'], test_case_columns['expected']}
        for col in all_columns:
            if col not in excluded_columns and pd.notna(row[col]):
                test_case['additional_data'][col] = str(row[col]).strip()

        return test_case

    def _extract_cell_value(self, row: pd.Series, column_name: Optional[str], default: str = "") -> str:
        """Extract and clean cell value."""
        if not column_name or column_name not in row.index or pd.isna(row[column_name]):
            return default
        return str(row[column_name]).strip()

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
        # Convert to lowercase for matching, handling various data types
        lower_columns = []
        for col in columns:
            if isinstance(col, (tuple, list)):
                # Si es una tupla o lista, tomar el primer elemento
                col_str = str(col[0]) if col and col[0] is not None else ""
            elif col is not None:
                col_str = str(col)
            else:
                col_str = ""
            lower_columns.append(col_str.lower())

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