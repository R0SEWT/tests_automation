"""
Tests for Excel Test Case Extractor
"""

import pytest
import pandas as pd
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.excel_parser.excel_extractor import ExcelTestExtractor


class TestExcelTestExtractor:
    """Test cases for the ExcelTestExtractor class."""

    @pytest.fixture
    def sample_excel_data(self):
        """Create sample Excel data for testing."""
        data = {
            'TestCaseID': ['TC_001', 'TC_002', 'TC_003'],
            'Description': ['Test login functionality', 'Test logout', 'Test password reset'],
            'ExpectedResult': ['User logged in successfully', 'User logged out', 'Password reset email sent']
        }
        return pd.DataFrame(data)

    @pytest.fixture
    def temp_excel_file(self, sample_excel_data):
        """Create a temporary Excel file for testing."""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            sample_excel_data.to_excel(tmp.name, index=False)
            yield tmp.name
        Path(tmp.name).unlink(missing_ok=True)

    def test_init_with_valid_file(self, temp_excel_file):
        """Test initialization with a valid Excel file."""
        extractor = ExcelTestExtractor(temp_excel_file)
        assert extractor.file_path == Path(temp_excel_file)
        assert extractor.workbook is not None

    def test_init_with_invalid_file(self):
        """Test initialization with a non-existent file."""
        with pytest.raises(FileNotFoundError):
            ExcelTestExtractor("non_existent_file.xlsx")

    def test_get_worksheet_names(self, temp_excel_file):
        """Test getting worksheet names."""
        extractor = ExcelTestExtractor(temp_excel_file)
        worksheets = extractor.get_worksheet_names()
        assert len(worksheets) == 1
        assert worksheets[0] == 'Sheet1'

    def test_extract_test_cases_from_worksheet(self, temp_excel_file):
        """Test extracting test cases from a worksheet."""
        extractor = ExcelTestExtractor(temp_excel_file)
        test_cases = extractor.extract_test_cases_from_worksheet('Sheet1')

        assert len(test_cases) == 3
        assert test_cases[0]['test_case_id'] == 'TC_001'
        assert test_cases[0]['description'] == 'Test login functionality'
        assert test_cases[0]['expected_result'] == 'User logged in successfully'
        assert test_cases[0]['worksheet'] == 'Sheet1'

    def test_identify_columns(self):
        """Test column identification logic."""
        extractor = ExcelTestExtractor.__new__(ExcelTestExtractor)  # Create without __init__

        # Test standard column names
        columns = ['TestCaseID', 'Description', 'ExpectedResult']
        result = extractor._identify_columns(columns)
        assert result['id'] == 'TestCaseID'
        assert result['description'] == 'Description'
        assert result['expected'] == 'ExpectedResult'

        # Test flexible column names
        columns = ['TC ID', 'Test Desc', 'Expected Outcome']
        result = extractor._identify_columns(columns)
        assert result['id'] == 'TC ID'
        assert result['description'] == 'Test Desc'
        assert result['expected'] == 'Expected Outcome'

    def test_extract_all_test_cases(self, temp_excel_file):
        """Test extracting all test cases from the workbook."""
        extractor = ExcelTestExtractor(temp_excel_file)
        all_test_cases = extractor.extract_all_test_cases()

        assert 'Sheet1' in all_test_cases
        assert len(all_test_cases['Sheet1']) == 3

    def test_save_to_json(self, temp_excel_file):
        """Test saving extracted data to JSON."""
        extractor = ExcelTestExtractor(temp_excel_file)
        test_cases = extractor.extract_all_test_cases()

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            extractor.save_to_json(tmp.name, test_cases)

            # Verify the file was created and contains valid JSON
            with open(tmp.name, 'r') as f:
                data = json.load(f)
                assert 'Sheet1' in data
                assert len(data['Sheet1']) == 3

            Path(tmp.name).unlink(missing_ok=True)

    def test_extract_and_save(self, temp_excel_file):
        """Test the complete extract and save workflow."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            extractor = ExcelTestExtractor(temp_excel_file)
            output_path = extractor.extract_and_save(tmp_dir)

            assert Path(output_path).exists()

            with open(output_path, 'r') as f:
                data = json.load(f)
                assert 'Sheet1' in data
                assert len(data['Sheet1']) == 3

    def test_missing_required_columns(self):
        """Test handling of worksheets with missing required columns."""
        # Create Excel file with only description column
        data = {'Description': ['Test case 1', 'Test case 2']}
        df = pd.DataFrame(data)

        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            df.to_excel(tmp.name, index=False)

            extractor = ExcelTestExtractor(tmp.name)
            test_cases = extractor.extract_test_cases_from_worksheet('Sheet1')

            # Should return empty list when required columns are missing
            assert test_cases == []

            Path(tmp.name).unlink(missing_ok=True)

    def test_extract_from_excel_file(self, temp_excel_file):
        """Test the convenience function."""
        from src.excel_parser.excel_extractor import extract_from_excel_file

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = extract_from_excel_file(temp_excel_file, tmp_dir)

            assert Path(output_path).exists()

            with open(output_path, 'r') as f:
                data = json.load(f)
                assert 'Sheet1' in data