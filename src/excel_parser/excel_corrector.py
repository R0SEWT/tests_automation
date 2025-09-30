"""
Excel Corrector - Generate corrected Excel files

Sistema específico para corregir archivos Excel siguiendo reglas de columnas:
- NombreID: Corregir nombre del caso de prueba (máximo 255 caracteres)
- Description: NO MODIFICAR
- Expected Result: Corregir resultado esperado (puede extender el nombre del caso)
- Test Step: NO MODIFICAR (ubicación o condición previa)
- Test Data: NO MODIFICAR (donde se testea)
- Epic Link: NO MODIFICAR
- Estado Qa: NO MODIFICAR
"""

import pandas as pd
import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill
from openpyxl.utils.dataframe import dataframe_to_rows
import json
import re

from ..core.utils import Logger
from .excel_extractor import ExcelTestExtractor

logger = Logger.setup_logger(__name__)


class MockedExcelCorrectionBuilder:
    """
    Sistema de corrección mockeado para Excel con reglas específicas de columnas.
    """
    
    def __init__(self, provider: str = "deepseek"):
        self.provider = provider
        self.logger = logging.getLogger(__name__)
        
        # Patrones de corrección para NombreID (nombres de casos de prueba)
        self.nombre_patterns = {
            'ortografia': [
                ('configuracion', 'configuración'),
                ('creacion', 'creación'),
                ('edicion', 'edición'),
                ('funcionalidad', 'funcionalidad'),
                ('superadmin', 'superadministrador'),
                ('validacion', 'validación'),
                ('verificacion', 'verificación'),
                ('autenticacion', 'autenticación'),
                ('notificacion', 'notificación'),
                ('actualizacion', 'actualización'),
            ],
            'mejoras': [
                ('validar', 'Validar'),
                ('verificar', 'Verificar'),
                ('crear', 'Crear'),
                ('editar', 'Editar'),
                ('eliminar', 'Eliminar'),
                ('mostrar', 'Mostrar'),
                ('guardar', 'Guardar'),
            ]
        }
        
        # Patrones de corrección para Expected Result
        self.expected_patterns = {
            'mejoras': [
                ('debe verse', 'debe visualizarse correctamente'),
                ('se vera', 'se visualizará de manera apropiada'),
                ('aparece', 'se muestra adecuadamente'),
                ('funciona', 'opera correctamente'),
                ('se guarda', 'se almacena exitosamente'),
                ('se actualiza', 'se modifica correctamente'),
                ('se muestra', 'se visualiza apropiadamente'),
                ('esta disponible', 'está disponible correctamente'),
            ],
            'ortografia': [
                ('configuracion', 'configuración'),
                ('creacion', 'creación'),
                ('edicion', 'edición'),
                ('validacion', 'validación'),
                ('notificacion', 'notificación'),
            ]
        }
    
    def corregir_nombres_casos(self, nombres: List[str]) -> Dict[str, Any]:
        """
        Corregir nombres de casos de prueba (NombreID).
        Máximo 255 caracteres, ortografía y formato mejorado.
        """
        corrected_names = []
        changes_made = 0
        
        for nombre in nombres:
            corrected = self._apply_name_corrections(nombre)
            
            # Limitar a 255 caracteres
            if len(corrected) > 255:
                corrected = corrected[:252] + "..."
            
            corrected_names.append(corrected)
            if corrected != nombre:
                changes_made += 1
        
        return {
            'original': nombres,
            'corrected': corrected_names,
            'changes_made': changes_made
        }
    
    def corregir_expected_results(self, expected_results: List[str], nombres_casos: List[str]) -> Dict[str, Any]:
        """
        Corregir resultados esperados.
        Puede extender basándose en el nombre del caso.
        """
        corrected_results = []
        changes_made = 0
        
        for i, expected in enumerate(expected_results):
            # Obtener contexto del nombre del caso si está disponible
            nombre_caso = nombres_casos[i] if i < len(nombres_casos) else ""
            
            corrected = self._apply_expected_corrections(expected, nombre_caso)
            corrected_results.append(corrected)
            
            if corrected != expected:
                changes_made += 1
        
        return {
            'original': expected_results,
            'corrected': corrected_results,
            'changes_made': changes_made
        }
    
    def _apply_name_corrections(self, name: str) -> str:
        """Aplicar correcciones específicas a nombres de casos."""
        corrected = name
        
        # Aplicar correcciones ortográficas
        for original, fixed in self.nombre_patterns['ortografia']:
            corrected = re.sub(r'\b' + re.escape(original) + r'\b', fixed, corrected, flags=re.IGNORECASE)
        
        # Aplicar mejoras de formato
        for original, improved in self.nombre_patterns['mejoras']:
            corrected = re.sub(r'\b' + re.escape(original) + r'\b', improved, corrected, flags=re.IGNORECASE)
        
        # Asegurar primera letra en mayúscula
        if corrected and corrected[0].islower():
            corrected = corrected[0].upper() + corrected[1:]
        
        return corrected.strip()
    
    def _apply_expected_corrections(self, expected: str, nombre_caso: str = "") -> str:
        """Aplicar correcciones a resultados esperados."""
        corrected = expected
        
        # Aplicar mejoras específicas
        for original, improved in self.expected_patterns['mejoras']:
            corrected = re.sub(r'\b' + re.escape(original) + r'\b', improved, corrected, flags=re.IGNORECASE)
        
        # Aplicar correcciones ortográficas
        for original, fixed in self.expected_patterns['ortografia']:
            corrected = re.sub(r'\b' + re.escape(original) + r'\b', fixed, corrected, flags=re.IGNORECASE)
        
        # Asegurar que termine con punto
        corrected = corrected.strip()
        if corrected and not corrected.endswith('.'):
            corrected += '.'
        
        return corrected


class ExcelCorrector:
    """
    Corrector principal de archivos Excel con reglas específicas de columnas.
    Integrado con RedactionAssistant para correcciones reales.
    """
    
    def __init__(self, excel_file_path: str, use_mock: bool = True, api_key: Optional[str] = None):
        self.original_file_path = Path(excel_file_path)
        self.use_mock = use_mock
        self.api_key = api_key
        self.logger = Logger.setup_logger(__name__)
        
        # Inicializar extractor
        self.extractor = ExcelTestExtractor(str(self.original_file_path))
        
        # Inicializar builder (mockeado o real)
        if use_mock:
            self.builder = MockedExcelCorrectionBuilder()
            self.logger.info("Usando builder mockeado para correcciones")
        else:
            # Integrar con RedactionAssistant real
            try:
                from ..redactionAssistant.config import Config
                from ..redactionAssistant.processor import Processor
                
                config = Config()
                if api_key:
                    self.processor = Processor(config, api_key)
                    self.builder = None  # Usaremos processor directamente
                    self.logger.info("Usando RedactionAssistant real con API key proporcionada")
                else:
                    self.logger.warning("No se proporcionó API key, usando modo mockeado")
                    self.builder = MockedExcelCorrectionBuilder()
                    self.use_mock = True
            except Exception as e:
                self.logger.warning("Error al inicializar RedactionAssistant: %s. Usando modo mockeado", e)
                self.builder = MockedExcelCorrectionBuilder()
                self.use_mock = True
    
    def process_corrections(self) -> Dict[str, Any]:
        """
        Procesar correcciones siguiendo las reglas específicas de columnas.
        """
        self.logger.info("Iniciando corrección de archivo Excel: %s", self.original_file_path)
        
        # Extraer todos los casos de prueba
        all_test_cases = self.extractor.extract_all_test_cases()
        
        # Procesar correcciones por worksheet
        corrections = {}
        total_test_cases = 0
        total_corrections = 0
        
        for worksheet_name, test_cases in all_test_cases.items():
            self.logger.info("Procesando worksheet: %s", worksheet_name)
            
            worksheet_corrections = self._process_worksheet_corrections(worksheet_name, test_cases)
            corrections[worksheet_name] = worksheet_corrections
            
            total_test_cases += len(test_cases)
            total_corrections += worksheet_corrections.get('total_changes', 0)
        
        result = {
            'success': True,
            'original_file': str(self.original_file_path),
            'total_worksheets': len(all_test_cases),
            'total_test_cases': total_test_cases,
            'total_corrections': total_corrections,
            'corrections_by_worksheet': corrections,
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        self.logger.info("Proceso de corrección completado. Total correcciones: %d", total_corrections)
        return result
    
    def _process_worksheet_corrections(self, worksheet_name: str, test_cases: List[Dict]) -> Dict[str, Any]:
        """Procesar correcciones para un worksheet específico."""
        
        # Extraer datos según las reglas de columnas
        nombres_casos = []
        descriptions = []
        expected_results = []
        
        for tc in test_cases:
            # Solo corregir NombreID y Expected Result
            nombres_casos.append(tc.get('test_case_id', ''))  # NombreID
            descriptions.append(tc.get('description', ''))    # NO MODIFICAR
            expected_results.append(tc.get('expected_result', ''))  # CORREGIR
        
        # Aplicar correcciones usando el sistema apropiado
        if self.use_mock:
            # Usar builder mockeado
            nombre_corrections = self.builder.corregir_nombres_casos(nombres_casos)
            expected_corrections = self.builder.corregir_expected_results(
                expected_results, 
                nombre_corrections['corrected']
            )
        else:
            # Usar RedactionAssistant real
            nombre_corrections, expected_corrections = self._process_with_redaction_assistant(
                worksheet_name, nombres_casos, expected_results
            )
        
        # Crear casos de prueba corregidos
        corrected_test_cases = []
        for i, tc in enumerate(test_cases):
            corrected_tc = tc.copy()
            
            # Aplicar correcciones solo a las columnas permitidas
            if i < len(nombre_corrections['corrected']):
                corrected_tc['test_case_id'] = nombre_corrections['corrected'][i]
                corrected_tc['test_case_id_original'] = tc.get('test_case_id', '')
            
            if i < len(expected_corrections['corrected']):
                corrected_tc['expected_result'] = expected_corrections['corrected'][i]
                corrected_tc['expected_result_original'] = tc.get('expected_result', '')
            
            corrected_test_cases.append(corrected_tc)
        
        total_changes = nombre_corrections['changes_made'] + expected_corrections['changes_made']
        
        return {
            'worksheet_name': worksheet_name,
            'original_count': len(test_cases),
            'corrected_test_cases': corrected_test_cases,
            'nombre_changes': nombre_corrections['changes_made'] if isinstance(nombre_corrections, dict) else nombre_corrections[1],
            'expected_changes': expected_corrections['changes_made'] if isinstance(expected_corrections, dict) else expected_corrections[1],
            'total_changes': total_changes
        }
    
    def _process_with_redaction_assistant(self, worksheet_name: str, nombres_casos: List[str], expected_results: List[str]) -> Tuple[Any, Any]:
        """
        Procesar correcciones usando RedactionAssistant real.
        
        Args:
            worksheet_name: Nombre del worksheet
            nombres_casos: Lista de nombres de casos de prueba
            expected_results: Lista de resultados esperados
            
        Returns:
            Tuple con correcciones de nombres y expected results
        """
        try:
            # Crear contexto de HU basado en el worksheet
            hu_context = f"Como usuario del sistema, quiero probar las funcionalidades relacionadas con {worksheet_name}"
            
            # Preparar casos de prueba para RedactionAssistant
            cps_text = "\n".join(nombres_casos)
            exp_text = "\n".join(expected_results)
            
            # Usar RedactionAssistant para corregir nombres (casos de prueba)
            cps_corregidos, cps_feedback = self.processor.cps_corregidas(hu_context, cps_text)
            
            # Usar RedactionAssistant para corregir expected results
            exp_corregidos, exp_feedback = self.processor.exp_corregidos(hu_context, cps_corregidos, exp_text)
            
            # Procesar resultados para formato compatible
            cps_corregidos_list = [line.strip() for line in cps_corregidos.splitlines() if line.strip()]
            exp_corregidos_list = [line.strip() for line in exp_corregidos.splitlines() if line.strip()]
            
            # Calcular cambios realizados
            nombre_changes = sum(1 for orig, corr in zip(nombres_casos, cps_corregidos_list) if orig != corr)
            expected_changes = sum(1 for orig, corr in zip(expected_results, exp_corregidos_list) if orig != corr)
            
            # Formato compatible con el sistema
            nombre_corrections = {
                'original': nombres_casos,
                'corrected': cps_corregidos_list,
                'changes_made': nombre_changes,
                'feedback': cps_feedback
            }
            
            expected_corrections = {
                'original': expected_results,
                'corrected': exp_corregidos_list,
                'changes_made': expected_changes,
                'feedback': exp_feedback
            }
            
            self.logger.info("RedactionAssistant procesó %s: %d nombres corregidos, %d expected results corregidos", 
                           worksheet_name, nombre_changes, expected_changes)
            
            return nombre_corrections, expected_corrections
            
        except Exception as e:
            self.logger.error("Error usando RedactionAssistant para %s: %s", worksheet_name, e)
            # Fallback a versión mockeada
            mock_builder = MockedExcelCorrectionBuilder()
            nombre_corrections = mock_builder.corregir_nombres_casos(nombres_casos)
            expected_corrections = mock_builder.corregir_expected_results(expected_results, nombres_casos)
            return nombre_corrections, expected_corrections
    
    def generate_corrected_excel(self, output_path: Optional[str] = None, highlight_changes: bool = True) -> str:
        """
        Generar archivo Excel corregido con highlighting de cambios.
        """
        # Procesar correcciones
        correction_results = self.process_corrections()
        
        # Determinar ruta de salida
        if output_path is None:
            output_path = self.original_file_path.parent / f"{self.original_file_path.stem}_CORREGIDO.xlsx"
        else:
            output_path = Path(output_path)
        
        # Crear directorio si no existe
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Abrir archivo original
        workbook = openpyxl.load_workbook(str(self.original_file_path))
        
        # Aplicar correcciones y highlighting
        for worksheet_name, corrections in correction_results['corrections_by_worksheet'].items():
            if worksheet_name in workbook.sheetnames:
                worksheet = workbook[worksheet_name]
                self._apply_corrections_to_worksheet(worksheet, corrections, highlight_changes)
        
        # Guardar archivo corregido
        workbook.save(str(output_path))
        
        self.logger.info("Archivo Excel corregido guardado en: %s", output_path)
        return str(output_path)
    
    def _apply_corrections_to_worksheet(self, worksheet, corrections: Dict[str, Any], highlight_changes: bool):
        """Aplicar correcciones a un worksheet específico."""
        
        # Obtener información de columnas
        column_info = self.extractor._identify_columns(worksheet)
        if not column_info:
            return
        
        # Definir estilos para highlighting
        if highlight_changes:
            changed_fill = PatternFill(start_color="FFFF99", end_color="FFFF99", fill_type="solid")  # Amarillo
            changed_font = Font(bold=True)
        
        # Aplicar correcciones a cada fila
        corrected_test_cases = corrections['corrected_test_cases']
        
        for i, corrected_tc in enumerate(corrected_test_cases):
            row_num = column_info['data_start_row'] + i
            
            # Verificar si la fila existe
            if row_num > worksheet.max_row:
                continue
            
            # Corregir NombreID si cambió
            if 'test_case_id_original' in corrected_tc:
                if corrected_tc['test_case_id'] != corrected_tc['test_case_id_original']:
                    cell = worksheet.cell(row=row_num, column=column_info['id_column'])
                    cell.value = corrected_tc['test_case_id']
                    
                    if highlight_changes:
                        cell.fill = changed_fill
                        cell.font = changed_font
            
            # Corregir Expected Result si cambió
            if 'expected_result_original' in corrected_tc:
                if corrected_tc['expected_result'] != corrected_tc['expected_result_original']:
                    cell = worksheet.cell(row=row_num, column=column_info['expected_result_column'])
                    cell.value = corrected_tc['expected_result']
                    
                    if highlight_changes:
                        cell.fill = changed_fill
                        cell.font = changed_font


def generate_corrected_excel_file(excel_file_path: str, 
                                 output_path: Optional[str] = None,
                                 highlight_changes: bool = True,
                                 use_mock: bool = True,
                                 api_key: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
    """
    Función de conveniencia para generar archivo Excel corregido.
    
    Args:
        excel_file_path: Ruta al archivo Excel original
        output_path: Ruta de salida (opcional)
        highlight_changes: Si resaltar cambios visualmente
        use_mock: Si usar corrector mockeado (True) o RedactionAssistant real (False)
        api_key: API key para RedactionAssistant (requerida si use_mock=False)
    
    Returns:
        Tuple con (ruta_archivo_corregido, resultados_corrección)
    """
    corrector = ExcelCorrector(excel_file_path, use_mock=use_mock, api_key=api_key)
    
    # Procesar correcciones
    correction_results = corrector.process_corrections()
    
    # Generar archivo corregido
    corrected_file_path = corrector.generate_corrected_excel(output_path, highlight_changes)
    
    return corrected_file_path, correction_results