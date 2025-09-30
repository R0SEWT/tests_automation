"""
Excel Corrector - Generate corrected Excel files

This module provides functionality to create corrected copies of Excel files
with improvements applied to test cases and expected results using mocked API calls.
"""

import pandas as pd
import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
import json
import random
import re

from ..core.utils import Logger
from .excel_extractor import ExcelTestExtractor

logger = Logger.setup_logger(__name__)


class MockedExcelCorrectionBuilder:
    """
    Mocked version of the Builder class for Excel correction.
    
    Simulates API calls with realistic corrections to demonstrate functionality
    without requiring actual API keys or making real requests.
    """
    
    def __init__(self, provider: str = "deepseek"):
        self.provider = provider
        self.logger = logging.getLogger(__name__)
        
        # Common correction patterns to simulate realistic improvements
        self.correction_patterns = {
            'ortografia': [
                ('verificar', 'verificar'),
                ('validar', 'validar'),
                ('conforme', 'conforme'),
                ('desestimado', 'desestimado'),
                ('formulario', 'formulario'),
                ('administrador', 'administrador'),
                ('configuracion', 'configuración'),
                ('creacion', 'creación'),
                ('edicion', 'edición'),
                ('funcionalidad', 'funcionalidad'),
                ('superadmin', 'superadministrador'),
                ('colaborador', 'colaborador'),
                ('corporativo', 'corporativo'),
                ('obligatorio', 'obligatorio'),
            ],
            'gramatica': [
                ('debe verse', 'debe visualizarse'),
                ('se vera', 'se visualizará'),
                ('se muestra', 'se visualiza'),
                ('aparece', 'se muestra'),
                ('se encuentra', 'está ubicado'),
                ('tiene un', 'presenta un'),
                ('sera', 'será'),
                ('estara', 'estará'),
            ]
        }
    
    def corregir_ortografia(self, hu: str, cps: List[str]) -> str:
        """Mock correction of test cases with simulated improvements."""
        results = []
        
        for i, cp in enumerate(cps):
            # Simulate some corrections based on patterns
            corrected_cp = self._apply_corrections(cp)
            
            if corrected_cp != cp:
                obs = f"OBS{i+1}: Corrección ortográfica aplicada, {cp}"
                results.append(obs)
                results.append(corrected_cp)
            else:
                obs = f"OBS{i+1}: Sin cambios necesarios, {cp}"
                results.append(obs)
                results.append(cp)
        
        return "\n".join(results)
    
    def corregir_expect_result(self, cps_with_expectResult: str) -> str:
        """Mock correction of expected results with simulated improvements."""
        lines = cps_with_expectResult.strip().split('\n')
        results = []
        observations = []
        
        for i, line in enumerate(lines):
            if '|' in line:
                cp, exp_result = line.split('|', 1)
                exp_result = exp_result.strip()
                
                # Apply corrections to expected result
                corrected_exp = self._apply_corrections(exp_result)
                corrected_exp = self._ensure_present_tense(corrected_exp)
                corrected_exp = self._capitalize_first_letter(corrected_exp)
                
                results.append(f"ExpRes{i+1}: {corrected_exp}")
                
                if corrected_exp != exp_result:
                    observations.append(f"OBS: Mejorado resultado esperado - tiempo presente y ortografía")
                else:
                    observations.append(f"OBS: Sin cambios necesarios en resultado esperado")
        
        # Combine results and observations
        final_result = "\n".join(results) + "\n\n" + "\n".join(observations)
        return final_result
    
    def obtener_feedback(self, obs_for_cps: str) -> str:
        """Generate mock feedback based on observations."""
        lines = obs_for_cps.split('\n')
        corrections_count = len([l for l in lines if 'Corrección' in l or 'Mejorado' in l])
        no_changes_count = len([l for l in lines if 'Sin cambios' in l])
        
        feedback = f"""Resumen de correcciones aplicadas:
- Elementos procesados: {len(lines)}
- Correcciones aplicadas: {corrections_count}
- Sin cambios necesarios: {no_changes_count}

Tipos de mejoras realizadas:
- Correcciones ortográficas y acentuación
- Mejoras en redacción y claridad
- Normalización de tiempo verbal a presente
- Capitalización apropiada

Todas las correcciones mantienen el significado original y la funcionalidad técnica."""
        
        return feedback
    
    def _apply_corrections(self, text: str) -> str:
        """Apply mock corrections based on common patterns."""
        corrected = text
        
        # Apply orthographic corrections
        for original, corrected_word in self.correction_patterns['ortografia']:
            corrected = re.sub(r'\b' + re.escape(original) + r'\b', corrected_word, corrected, flags=re.IGNORECASE)
        
        # Apply grammar improvements
        for original, improved in self.correction_patterns['gramatica']:
            corrected = re.sub(r'\b' + re.escape(original) + r'\b', improved, corrected, flags=re.IGNORECASE)
        
        return corrected
    
    def _ensure_present_tense(self, text: str) -> str:
        """Convert common future/past tense verbs to present tense."""
        tense_corrections = {
            'será': 'es',
            'estará': 'está',
            'tendrá': 'tiene',
            'mostrará': 'muestra',
            'aparecerá': 'aparece',
            'se verá': 'se ve',
            'se encontrará': 'se encuentra',
            'permitirá': 'permite',
            'habilitará': 'habilita',
            'deshabilitará': 'deshabilita',
        }
        
        corrected = text
        for future, present in tense_corrections.items():
            corrected = re.sub(r'\b' + re.escape(future) + r'\b', present, corrected, flags=re.IGNORECASE)
        
        return corrected
    
    def _capitalize_first_letter(self, text: str) -> str:
        """Ensure first letter is capitalized."""
        if text:
            return text[0].upper() + text[1:] if len(text) > 1 else text.upper()
        return text


class ExcelCorrector:
    """
    Creates corrected copies of Excel files with improved test cases and expected results.
    
    This class processes Excel files containing test cases, applies corrections using
    mocked API calls, and generates new Excel files with improvements highlighted.
    """
    
    def __init__(self, original_file_path: str, use_mock: bool = True):
        """
        Initialize the ExcelCorrector.
        
        Args:
            original_file_path: Path to the original Excel file
            use_mock: Whether to use mocked API calls (default: True)
        """
        self.original_file_path = Path(original_file_path)
        self.use_mock = use_mock
        self.logger = logger
        
        if not self.original_file_path.exists():
            raise FileNotFoundError(f"Original Excel file not found: {original_file_path}")
        
        # Initialize extractor for reading data
        self.extractor = ExcelTestExtractor(str(self.original_file_path))
        
        # Initialize correction builder
        if use_mock:
            self.builder = MockedExcelCorrectionBuilder()
        else:
            # Would use real builder here if API key available
            raise NotImplementedError("Real API calls not implemented in this demo")
    
    def process_corrections(self) -> Dict[str, Any]:
        """
        Process corrections for all worksheets in the Excel file.
        
        Returns:
            Dictionary containing correction results and metadata
        """
        self.logger.info("Starting correction process for Excel file: %s", self.original_file_path)
        
        # Extract all test cases
        all_test_cases = self.extractor.extract_all_test_cases()
        
        # Process corrections for each worksheet
        corrections = {}
        total_test_cases = 0
        total_corrections = 0
        
        for worksheet_name, test_cases in all_test_cases.items():
            self.logger.info("Processing corrections for worksheet: %s", worksheet_name)
            
            worksheet_corrections = self._process_worksheet_corrections(worksheet_name, test_cases)
            corrections[worksheet_name] = worksheet_corrections
            
            total_test_cases += len(test_cases)
            total_corrections += worksheet_corrections.get('corrections_applied', 0)
        
        result = {
            'success': True,
            'original_file': str(self.original_file_path),
            'total_worksheets': len(all_test_cases),
            'total_test_cases': total_test_cases,
            'total_corrections': total_corrections,
            'corrections_by_worksheet': corrections,
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        self.logger.info("Correction process completed. Total corrections: %d", total_corrections)
        return result
    
    def _process_worksheet_corrections(self, worksheet_name: str, test_cases: List[Dict]) -> Dict[str, Any]:
        """Process corrections for a single worksheet."""
        corrections_applied = 0
        corrected_test_cases = []
        
        # Mock HU (Historia de Usuario) for context
        mock_hu = f"Como usuario del sistema, quiero realizar las funcionalidades de {worksheet_name}"
        
        # Process test cases in batches
        batch_size = 10
        for i in range(0, len(test_cases), batch_size):
            batch = test_cases[i:i + batch_size]
            
            # Extract test case IDs and descriptions for correction
            test_case_ids = [tc.get('test_case_id', '') for tc in batch]
            descriptions = [tc.get('description', '') for tc in batch]
            expected_results = [tc.get('expected_result', '') for tc in batch]
            
            # Mock correction of test case descriptions
            if test_case_ids:
                corrected_descriptions = self._correct_descriptions(mock_hu, test_case_ids, descriptions)
                corrected_expected = self._correct_expected_results(test_case_ids, descriptions, expected_results)
            else:
                corrected_descriptions = descriptions
                corrected_expected = expected_results
            
            # Create corrected test cases
            for j, tc in enumerate(batch):
                corrected_tc = tc.copy()
                
                # Apply corrections if available
                if j < len(corrected_descriptions):
                    corrected_tc['description_original'] = tc.get('description', '')
                    corrected_tc['description'] = corrected_descriptions[j]
                    if corrected_descriptions[j] != tc.get('description', ''):
                        corrections_applied += 1
                
                if j < len(corrected_expected):
                    corrected_tc['expected_result_original'] = tc.get('expected_result', '')
                    corrected_tc['expected_result'] = corrected_expected[j]
                    if corrected_expected[j] != tc.get('expected_result', ''):
                        corrections_applied += 1
                
                corrected_test_cases.append(corrected_tc)
        
        return {
            'worksheet_name': worksheet_name,
            'original_count': len(test_cases),
            'corrected_test_cases': corrected_test_cases,
            'corrections_applied': corrections_applied
        }
    
    def _correct_descriptions(self, hu: str, test_case_ids: List[str], descriptions: List[str]) -> List[str]:
        """Apply corrections to test case descriptions."""
        # Combine IDs and descriptions for context
        combined = [f"{tc_id} - {desc}" for tc_id, desc in zip(test_case_ids, descriptions)]
        
        if not combined:
            return descriptions
        
        # Get corrections from mocked builder
        correction_result = self.builder.corregir_ortografia(hu, combined)
        
        # Parse the correction result
        corrected_descriptions = []
        lines = correction_result.split('\n')
        
        # Extract corrected test cases (skip OBS lines)
        for line in lines:
            if not line.startswith('OBS') and line.strip():
                # Extract the description part after the test case ID
                if ' - ' in line:
                    _, desc_part = line.split(' - ', 1)
                    corrected_descriptions.append(desc_part.strip())
                else:
                    corrected_descriptions.append(line.strip())
        
        # Ensure we have the same number of corrections as inputs
        while len(corrected_descriptions) < len(descriptions):
            corrected_descriptions.append(descriptions[len(corrected_descriptions)])
        
        return corrected_descriptions[:len(descriptions)]
    
    def _correct_expected_results(self, test_case_ids: List[str], descriptions: List[str], expected_results: List[str]) -> List[str]:
        """Apply corrections to expected results."""
        # Combine test cases and expected results
        combined_pairs = []
        for tc_id, desc, exp in zip(test_case_ids, descriptions, expected_results):
            combined_pairs.append(f"{tc_id} - {desc} | {exp}")
        
        if not combined_pairs:
            return expected_results
        
        # Get corrections from mocked builder
        correction_result = self.builder.corregir_expect_result('\n'.join(combined_pairs))
        
        # Parse expected results
        corrected_expected = []
        lines = correction_result.split('\n')
        
        for line in lines:
            if line.startswith('ExpRes'):
                # Extract the expected result after the colon
                if ':' in line:
                    _, exp_part = line.split(':', 1)
                    corrected_expected.append(exp_part.strip())
        
        # Check for mismatch in number of corrections and inputs
        if len(corrected_expected) != len(expected_results):
            logging.warning(
                "Mismatch between number of corrected expected results (%d) and input expected results (%d).",
                len(corrected_expected), len(expected_results)
            )
        return corrected_expected[:len(expected_results)]
    
    def generate_corrected_excel(self, output_path: Optional[str] = None, highlight_changes: bool = True) -> str:
        """
        Generate a corrected Excel file with improvements applied.
        
        Args:
            output_path: Path for the output file. If None, generates based on original filename
            highlight_changes: Whether to highlight corrected cells
            
        Returns:
            Path to the generated corrected Excel file
        """
        # Process all corrections
        correction_results = self.process_corrections()

        if not correction_results['success']:
            error_details = []
            if 'errors' in correction_results and correction_results['errors']:
                error_details.append(f"Errors: {correction_results['errors']}")
            if 'worksheet_names' in correction_results and correction_results['worksheet_names']:
                error_details.append(f"Worksheets: {correction_results['worksheet_names']}")
            error_message = "Failed to process corrections"
            if error_details:
                error_message += " - " + "; ".join(error_details)
            raise RuntimeError(error_message)

        # Determine output path
        if output_path is None:
            output_path = self.original_file_path.parent / f"{self.original_file_path.stem}_corregido.xlsx"
        else:
            output_path = Path(output_path)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("Generating corrected Excel file: %s", output_path)
        
        # Create new workbook
        corrected_workbook = openpyxl.Workbook()
        
        # Remove default sheet
        if 'Sheet' in corrected_workbook.sheetnames:
            corrected_workbook.remove(corrected_workbook['Sheet'])
        
        # Define styles for highlighting changes
        if highlight_changes:
            changed_fill = PatternFill(start_color="FFFF99", end_color="FFFF99", fill_type="solid")  # Light yellow
            changed_font = Font(bold=True)
        
        # Process each worksheet
        for worksheet_name, worksheet_data in correction_results['corrections_by_worksheet'].items():
            # Create worksheet
            ws = corrected_workbook.create_sheet(title=worksheet_name)
            
            # Get corrected test cases
            corrected_test_cases = worksheet_data['corrected_test_cases']
            
            if not corrected_test_cases:
                continue
            
            # Create DataFrame for this worksheet
            df_data = []
            for tc in corrected_test_cases:
                row_data = {
                    'Test Case ID': tc.get('test_case_id', ''),
                    'Description': tc.get('description', ''),
                    'Expected Result': tc.get('expected_result', ''),
                }
                
                # Add additional data columns
                for key, value in tc.get('additional_data', {}).items():
                    row_data[key] = value
                
                df_data.append(row_data)
            
            df = pd.DataFrame(df_data)
            
            # Write DataFrame to worksheet
            for r in dataframe_to_rows(df, index=False, header=True):
                ws.append(r)
            
            # Apply formatting and highlighting
            if highlight_changes:
                self._apply_highlighting(ws, corrected_test_cases, changed_fill, changed_font)
        
        # Save the corrected workbook
        corrected_workbook.save(str(output_path))
        self.logger.info("Corrected Excel file saved successfully: %s", output_path)
        
        # Generate summary report
        self._generate_correction_summary(correction_results, output_path.parent / f"{output_path.stem}_summary.json")
        
        return str(output_path)
    
    def _apply_highlighting(self, worksheet, corrected_test_cases: List[Dict], changed_fill, changed_font):
        """Apply highlighting to cells that were corrected."""
        # Find column indices for description and expected result
        header_row = 1
        desc_col = None
        exp_col = None
        
        for col_idx, cell in enumerate(worksheet[header_row], 1):
            if cell.value and 'description' in str(cell.value).lower():
                desc_col = col_idx
            elif cell.value and ('expected' in str(cell.value).lower() or 'result' in str(cell.value).lower()):
                exp_col = col_idx
        
        # Apply highlighting to changed cells
        for row_idx, tc in enumerate(corrected_test_cases, 2):  # Start from row 2 (after header)
            # Check if description was changed
            if (desc_col and 
                tc.get('description_original') and 
                tc.get('description') != tc.get('description_original')):
                cell = worksheet.cell(row=row_idx, column=desc_col)
                cell.fill = changed_fill
                cell.font = changed_font
            
            # Check if expected result was changed
            if (exp_col and 
                tc.get('expected_result_original') and 
                tc.get('expected_result') != tc.get('expected_result_original')):
                cell = worksheet.cell(row=row_idx, column=exp_col)
                cell.fill = changed_fill
                cell.font = changed_font
    
    def _generate_correction_summary(self, correction_results: Dict[str, Any], summary_path: Path):
        """Generate a summary report of all corrections applied."""
        summary = {
            'correction_summary': {
                'original_file': correction_results['original_file'],
                'total_worksheets_processed': correction_results['total_worksheets'],
                'total_test_cases_processed': correction_results['total_test_cases'],
                'total_corrections_applied': correction_results['total_corrections'],
                'processing_timestamp': correction_results['timestamp'],
                'mock_api_used': self.use_mock
            },
            'worksheet_details': {},
            'sample_corrections': []
        }
        
        # Add worksheet-level details
        for worksheet_name, worksheet_data in correction_results['corrections_by_worksheet'].items():
            summary['worksheet_details'][worksheet_name] = {
                'original_test_case_count': worksheet_data['original_count'],
                'corrections_applied': worksheet_data['corrections_applied']
            }
            
            # Add sample corrections from this worksheet
            for tc in worksheet_data['corrected_test_cases'][:3]:  # First 3 as samples
                if tc.get('description_original') and tc.get('description') != tc.get('description_original'):
                    summary['sample_corrections'].append({
                        'worksheet': worksheet_name,
                        'test_case_id': tc.get('test_case_id', ''),
                        'field': 'description',
                        'original': tc.get('description_original', ''),
                        'corrected': tc.get('description', '')
                    })
                
                if tc.get('expected_result_original') and tc.get('expected_result') != tc.get('expected_result_original'):
                    summary['sample_corrections'].append({
                        'worksheet': worksheet_name,
                        'test_case_id': tc.get('test_case_id', ''),
                        'field': 'expected_result',
                        'original': tc.get('expected_result_original', ''),
                        'corrected': tc.get('expected_result', '')
                    })
        
        # Save summary
        try:
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
        except (OSError, IOError) as e:
            logging.error(f"Failed to write summary to {summary_path}: {e}")
        self.logger.info("Correction summary saved: %s", summary_path)


def generate_corrected_excel_file(
    original_file_path: str, 
    output_path: Optional[str] = None, 
    highlight_changes: bool = True,
    use_mock: bool = True
) -> Tuple[str, Dict[str, Any]]:
    """
    Convenience function to generate a corrected Excel file.
    
    Args:
        original_file_path: Path to the original Excel file
        output_path: Path for the corrected file (optional)
        highlight_changes: Whether to highlight corrected cells
        use_mock: Whether to use mocked API calls
        
    Returns:
        Tuple of (corrected_file_path, correction_summary)
    """
    corrector = ExcelCorrector(original_file_path, use_mock=use_mock)
    
    # Generate corrected file
    corrected_file_path = corrector.generate_corrected_excel(output_path, highlight_changes)
    
    # Get correction summary
    correction_results = corrector.process_corrections()
    
    return corrected_file_path, correction_results