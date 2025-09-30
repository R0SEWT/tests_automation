#!/usr/bin/env python3
"""
Demo del Excel Corrector con reglas específicas de columnas

Demuestra el sistema de corrección siguiendo las reglas:
- NombreID: Corregir nombre del caso de prueba (máximo 255 caracteres)
- Description: NO MODIFICAR
- Expected Result: Corregir resultado esperado
- Otras columnas: NO MODIFICAR
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from excel_parser.excel_corrector import generate_corrected_excel_file, ExcelCorrector
import json


def demo_column_rules():
    """Demostrar las reglas específicas de corrección por columnas."""
    
    print("=" * 60)
    print("DEMO: Excel Corrector con Reglas Específicas de Columnas")
    print("=" * 60)
    
    print("\n📋 REGLAS DE CORRECCIÓN:")
    print("✅ NombreID: Corregir nombre del caso (máximo 255 caracteres)")
    print("❌ Description: NO MODIFICAR")
    print("✅ Expected Result: Corregir resultado esperado")
    print("❌ Test Step: NO MODIFICAR (ubicación/condición previa)")
    print("❌ Test Data: NO MODIFICAR (donde se testea)")
    print("❌ Epic Link: NO MODIFICAR")
    print("❌ Estado Qa: NO MODIFICAR")
    
    # Buscar archivo Excel de ejemplo
    excel_files = list(Path("data").glob("*.xlsx"))
    
    if not excel_files:
        print("\n❌ No se encontraron archivos Excel en data/")
        print("💡 Coloca un archivo Excel en la carpeta data/ para probar")
        return
    
    excel_file = excel_files[0]
    print(f"\n📁 Archivo de prueba: {excel_file}")
    
    try:
        # Crear corrector
        corrector = ExcelCorrector(str(excel_file), use_mock=True)
        
        # Procesar correcciones
        print("\n🔄 Procesando correcciones...")
        correction_results = corrector.process_corrections()
        
        # Mostrar resultados
        print(f"\n📊 RESULTADOS:")
        print(f"   Total worksheets: {correction_results['total_worksheets']}")
        print(f"   Total casos de prueba: {correction_results['total_test_cases']}")
        print(f"   Total correcciones: {correction_results['total_corrections']}")
        
        # Mostrar detalles por worksheet
        print(f"\n📋 CORRECCIONES POR WORKSHEET:")
        for worksheet_name, corrections in correction_results['corrections_by_worksheet'].items():
            nombre_changes = corrections.get('nombre_changes', 0)
            expected_changes = corrections.get('expected_changes', 0)
            
            print(f"   📄 {worksheet_name}:")
            print(f"      • Casos procesados: {corrections['original_count']}")
            print(f"      • Nombres corregidos: {nombre_changes}")
            print(f"      • Expected Results corregidos: {expected_changes}")
            print(f"      • Total cambios: {corrections['total_changes']}")
        
        # Generar archivo corregido
        print(f"\n💾 Generando archivo corregido...")
        corrected_file = corrector.generate_corrected_excel(highlight_changes=True)
        
        print(f"✅ Archivo corregido generado: {corrected_file}")
        print(f"🎯 Cambios resaltados visualmente en amarillo")
        
        # Generar resumen JSON
        summary_file = Path(corrected_file).parent / f"{Path(corrected_file).stem}_resumen.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(correction_results, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Resumen guardado en: {summary_file}")
        
        # Mostrar ejemplos de correcciones
        if correction_results['total_corrections'] > 0:
            print(f"\n🔍 EJEMPLOS DE CORRECCIONES APLICADAS:")
            
            for worksheet_name, corrections in correction_results['corrections_by_worksheet'].items():
                corrected_cases = corrections['corrected_test_cases']
                
                examples_shown = 0
                for tc in corrected_cases:
                    if examples_shown >= 3:  # Limitar ejemplos
                        break
                    
                    # Mostrar correcciones de NombreID
                    if 'test_case_id_original' in tc:
                        if tc['test_case_id'] != tc['test_case_id_original']:
                            print(f"\n   📝 NombreID corregido:")
                            print(f"      Antes: {tc['test_case_id_original']}")
                            print(f"      Después: {tc['test_case_id']}")
                            examples_shown += 1
                    
                    # Mostrar correcciones de Expected Result
                    if 'expected_result_original' in tc:
                        if tc['expected_result'] != tc['expected_result_original']:
                            print(f"\n   🎯 Expected Result corregido:")
                            print(f"      Antes: {tc['expected_result_original']}")
                            print(f"      Después: {tc['expected_result']}")
                            examples_shown += 1
                
                if examples_shown > 0:
                    break
        
        print(f"\n🎉 DEMO COMPLETADO EXITOSAMENTE")
        
    except Exception as e:
        print(f"\n❌ Error durante el procesamiento: {e}")
        import traceback
        traceback.print_exc()


def demo_quick_correction(excel_file_path: str):
    """Demo rápido de corrección con función de conveniencia."""
    
    print(f"\n🚀 CORRECCIÓN RÁPIDA: {excel_file_path}")
    print("-" * 50)
    
    try:
        # Usar función de conveniencia
        corrected_file, results = generate_corrected_excel_file(
            excel_file_path,
            highlight_changes=True,
            use_mock=True
        )
        
        print(f"✅ Archivo original: {excel_file_path}")
        print(f"✅ Archivo corregido: {corrected_file}")
        print(f"📊 Total correcciones: {results['total_corrections']}")
        print(f"📋 Worksheets procesados: {results['total_worksheets']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Si se proporciona archivo específico
        excel_file = sys.argv[1]
        if Path(excel_file).exists():
            demo_quick_correction(excel_file)
        else:
            print(f"❌ Archivo no encontrado: {excel_file}")
    else:
        # Demo completo
        demo_column_rules()