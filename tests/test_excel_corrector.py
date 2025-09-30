"""
Tests for Excel Corrector functionality.

This module tests the ExcelCorrector class and related functions for generating
corrected Excel files with mocked API calls.
"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import json
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.excel_parser.excel_corrector import (
    ExcelCorrector, 
    MockedExcelCorrectionBuilder, 
    generate_corrected_excel_file
)


@pytest.fixture
def sample_excel_file():
    """Create a temporary Excel file for testing."""
    # Sample test data
    sample_data = {
        'Test Case ID': [
            'USRNM01 - CP01',
            'USRNM01 - CP02',
            'USRNM01 - CP03'
        ],
        'Description': [
            'Como superadmin, En el formulario de creacion de una empresa',
            'Como superadmin, verificar que el modal aparecera',
            'Como BP, validar que se guardaran los datos'
        ],
        'Expected Result': [
            'Se añade un card que se encontrara debajo',
            'el modal aparecera con el texto esperado',
            'los datos se guardaran correctamente'
        ],
        'Test Step': [
            'Estar en el formulario',
            'Ejecutar acción',
            'Verificar resultado'
        ],
        'Epic Link': [
            'VLPER-89221',
            'VLPER-89221',
            'VLPER-89221'
        ]
    }
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
        df = pd.DataFrame(sample_data)
        
        with pd.ExcelWriter(tmp_file.name, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='USRNM01', index=False)
            df.to_excel(writer, sheet_name='USRNM02', index=False)
        
        return tmp_file.name


class TestMockedExcelCorrectionBuilder:
    """Test the mocked builder functionality."""
    
    def test_initialization(self):
        """Test builder initialization."""
        builder = MockedExcelCorrectionBuilder()
        assert builder.provider == "deepseek"
        assert hasattr(builder, 'correction_patterns')
    
    def test_corregir_ortografia(self):
        """Test mock orthography correction."""
        builder = MockedExcelCorrectionBuilder()
        
        hu = "Como usuario quiero hacer login"
        cps = ["Validar formulario de creacion", "Verificar que sera exitoso"]
        
        result = builder.corregir_ortografia(hu, cps)
        
        assert isinstance(result, str)
        assert len(result.split('\n')) >= len(cps)  # Should have at least one line per input
        assert 'OBS' in result  # Should contain observations
    
    def test_corregir_expect_result(self):
        """Test mock expected result correction."""
        builder = MockedExcelCorrectionBuilder()
        
        cps_with_exp = "USRNM01 Validar login | el sistema permitira acceso"
        
        result = builder.corregir_expect_result(cps_with_exp)
        
        assert isinstance(result, str)
        assert 'ExpRes' in result  # Should contain expected results
        assert 'OBS' in result  # Should contain observations
    
    def test_obtener_feedback(self):
        """Test feedback generation."""
        builder = MockedExcelCorrectionBuilder()
        
        obs = "OBS1: Corrección aplicada\nOBS2: Sin cambios"
        
        feedback = builder.obtener_feedback(obs)
        
        assert isinstance(feedback, str)
        assert 'correcciones' in feedback.lower()
        assert len(feedback) > 50  # Should be substantial feedback


class TestExcelCorrector:
    """Test the ExcelCorrector class."""
    
    def test_initialization(self, sample_excel_file):
        """Test corrector initialization."""
        corrector = ExcelCorrector(sample_excel_file, use_mock=True)
        
        assert corrector.original_file_path.exists()
        assert corrector.use_mock is True
        assert hasattr(corrector, 'builder')
        assert hasattr(corrector, 'extractor')
    
    def test_initialization_file_not_found(self):
        """Test initialization with non-existent file."""
        with pytest.raises(FileNotFoundError):
            ExcelCorrector('nonexistent_file.xlsx')
    
    def test_process_corrections(self, sample_excel_file):
        """Test the correction processing."""
        corrector = ExcelCorrector(sample_excel_file, use_mock=True)
        
        results = corrector.process_corrections()
        
        assert results['success'] is True
        assert 'total_worksheets' in results
        assert 'total_test_cases' in results
        assert 'total_corrections' in results
        assert 'corrections_by_worksheet' in results
        assert results['total_worksheets'] > 0
    
    def test_generate_corrected_excel(self, sample_excel_file):
        """Test generating corrected Excel file."""
        corrector = ExcelCorrector(sample_excel_file, use_mock=True)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "corrected.xlsx"
            
            corrected_file_path = corrector.generate_corrected_excel(
                str(output_path), 
                highlight_changes=True
            )
            
            assert Path(corrected_file_path).exists()
            assert corrected_file_path.endswith('.xlsx')
            
            # Check that summary file was also created
            summary_path = Path(temp_dir) / "corrected_summary.json"
            assert summary_path.exists()
            
            # Validate summary content
            with open(summary_path, 'r', encoding='utf-8') as f:
                summary = json.load(f)
                assert 'correction_summary' in summary
                assert 'worksheet_details' in summary
    
    def test_worksheet_corrections(self, sample_excel_file):
        """Test worksheet-level corrections."""
        corrector = ExcelCorrector(sample_excel_file, use_mock=True)
        
        # Get test cases from first worksheet
        all_test_cases = corrector.extractor.extract_all_test_cases()
        first_worksheet = list(all_test_cases.keys())[0]
        test_cases = all_test_cases[first_worksheet]
        
        worksheet_corrections = corrector._process_worksheet_corrections(
            first_worksheet, 
            test_cases
        )
        
        assert 'worksheet_name' in worksheet_corrections
        assert 'original_count' in worksheet_corrections
        assert 'corrected_test_cases' in worksheet_corrections
        assert 'corrections_applied' in worksheet_corrections
        assert worksheet_corrections['worksheet_name'] == first_worksheet
        assert len(worksheet_corrections['corrected_test_cases']) == len(test_cases)


class TestConvenienceFunction:
    """Test the convenience function for Excel correction."""
    
    def test_generate_corrected_excel_file(self, sample_excel_file):
        """Test the convenience function."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "convenient_corrected.xlsx"
            
            corrected_file_path, correction_results = generate_corrected_excel_file(
                original_file_path=sample_excel_file,
                output_path=str(output_path),
                highlight_changes=True,
                use_mock=True
            )
            
            assert Path(corrected_file_path).exists()
            assert isinstance(correction_results, dict)
            assert correction_results['success'] is True
            assert 'total_corrections' in correction_results
    
    def test_generate_with_default_output_path(self, sample_excel_file):
        """Test convenience function with default output path."""
        corrected_file_path, correction_results = generate_corrected_excel_file(
            original_file_path=sample_excel_file,
            output_path=None,  # Use default
            highlight_changes=False,
            use_mock=True
        )
        
        assert Path(corrected_file_path).exists()
        assert '_corregido.xlsx' in corrected_file_path
        assert correction_results['success'] is True
        
        # Clean up
        Path(corrected_file_path).unlink()
        # Also clean up summary file if exists
        summary_path = Path(corrected_file_path).parent / f"{Path(corrected_file_path).stem}_summary.json"
        if summary_path.exists():
            summary_path.unlink()


class TestCorrectionPatterns:
    """Test the correction pattern application."""
    
    def test_apply_corrections(self):
        """Test pattern-based corrections."""
        builder = MockedExcelCorrectionBuilder()
        
        test_text = "verificar que sera exitoso en la creacion"
        corrected = builder._apply_corrections(test_text)
        
        # Should apply corrections based on patterns
        assert 'creación' in corrected  # ortografia correction
    
    def test_ensure_present_tense(self):
        """Test present tense conversion."""
        builder = MockedExcelCorrectionBuilder()
        
        test_text = "el sistema será exitoso y estará disponible"
        corrected = builder._ensure_present_tense(test_text)
        
        assert 'es exitoso' in corrected
        assert 'está disponible' in corrected
    
    def test_capitalize_first_letter(self):
        """Test first letter capitalization."""
        builder = MockedExcelCorrectionBuilder()
        
        test_text = "el resultado esperado"
        corrected = builder._capitalize_first_letter(test_text)
        
        assert corrected.startswith('E')
        assert corrected == "El resultado esperado"


@pytest.mark.integration
class TestIntegrationWithRealFile:
    """Integration tests with actual project files."""
    
    def test_with_username_excel_file(self):
        """Test with the USERNAME.xlsx file if it exists."""
        username_file = Path("data/USERNAME.xlsx")
        
        if not username_file.exists():
            pytest.skip("USERNAME.xlsx file not found")
        
        # Test with a small subset to avoid long processing
        corrector = ExcelCorrector(str(username_file), use_mock=True)
        
        # Just test that it can process without errors
        results = corrector.process_corrections()
        
        assert results['success'] is True
        assert results['total_worksheets'] > 0
        assert results['total_test_cases'] > 0


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, '-v'])