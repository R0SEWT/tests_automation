#!/usr/bin/env python3
"""
Script completo para probar el Excel Corrector con reglas específicas
"""

import sys
from pathlib import Path
import json

# Configurar Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def main():
    """Función principal para probar el corrector."""
    
    print("=" * 70)
    print("EXCEL CORRECTOR - PROCESAMIENTO CON REGLAS ESPECÍFICAS")
    print("=" * 70)
    
    print("\n📋 REGLAS DE CORRECCIÓN:")
    print("✅ NombreID: Corregir nombre del caso (máximo 255 caracteres)")
    print("❌ Description: NO MODIFICAR")
    print("✅ Expected Result: Corregir resultado esperado")
    print("❌ Test Step, Test Data, Epic Link, Estado Qa: NO MODIFICAR")
    
    # Buscar archivo Excel
    excel_file = Path("data/USERNAME.xlsx")
    
    if not excel_file.exists():
        print(f"\n❌ Archivo no encontrado: {excel_file}")
        print("💡 Asegúrate de tener el archivo USERNAME.xlsx en la carpeta data/")
        return
    
    print(f"\n📁 Procesando archivo: {excel_file}")
    print(f"📦 Tamaño: {excel_file.stat().st_size / 1024:.1f} KB")
    
    try:
        # Importar directamente desde el módulo
        from src.excel_parser.excel_corrector import ExcelCorrector
        
        # Crear corrector
        corrector = ExcelCorrector(str(excel_file), use_mock=True)
        
        print("\n🔄 Iniciando proceso de corrección...")
        
        # Procesar correcciones
        correction_results = corrector.process_corrections()
        
        # Mostrar resultados
        print(f"\n📊 RESULTADOS DEL PROCESAMIENTO:")
        print(f"   ✅ Estado: {'Exitoso' if correction_results['success'] else 'Con errores'}")
        print(f"   📄 Worksheets procesados: {correction_results['total_worksheets']}")
        print(f"   📝 Casos de prueba totales: {correction_results['total_test_cases']}")
        print(f"   ✏️  Correcciones aplicadas: {correction_results['total_corrections']}")
        
        # Detalles por worksheet
        print(f"\n📋 DETALLES POR WORKSHEET:")
        
        for worksheet_name, corrections in correction_results['corrections_by_worksheet'].items():
            print(f"\n   📄 {worksheet_name}:")
            print(f"      • Casos originales: {corrections['original_count']}")
            print(f"      • Nombres corregidos: {corrections.get('nombre_changes', 0)}")
            print(f"      • Expected Results corregidos: {corrections.get('expected_changes', 0)}")
            print(f"      • Total cambios: {corrections.get('total_changes', 0)}")
        
        # Generar archivo corregido
        print(f"\n💾 Generando archivo Excel corregido...")
        
        output_file = corrector.generate_corrected_excel(highlight_changes=True)
        
        print(f"✅ Archivo generado: {output_file}")
        
        # Información del archivo generado
        output_path = Path(output_file)
        if output_path.exists():
            print(f"📦 Tamaño archivo corregido: {output_path.stat().st_size / 1024:.1f} KB")
            print(f"🎯 Cambios resaltados en amarillo para fácil identificación")
        
        # Guardar resumen detallado
        summary_file = output_path.parent / f"{output_path.stem}_resumen_detallado.json"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(correction_results, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Resumen detallado: {summary_file}")
        
        # Mostrar ejemplos de correcciones
        print(f"\n🔍 EJEMPLOS DE CORRECCIONES APLICADAS:")
        
        examples_count = 0
        max_examples = 5
        
        for worksheet_name, corrections in correction_results['corrections_by_worksheet'].items():
            if examples_count >= max_examples:
                break
                
            corrected_cases = corrections.get('corrected_test_cases', [])
            
            for tc in corrected_cases[:3]:  # Máximo 3 por worksheet
                if examples_count >= max_examples:
                    break
                
                # Mostrar correcciones de NombreID
                if ('test_case_id_original' in tc and 
                    tc.get('test_case_id') != tc.get('test_case_id_original')):
                    
                    print(f"\n   📝 NombreID corregido ({worksheet_name}):")
                    print(f"      ANTES:   {tc['test_case_id_original']}")
                    print(f"      DESPUÉS: {tc['test_case_id']}")
                    examples_count += 1
                
                # Mostrar correcciones de Expected Result
                if ('expected_result_original' in tc and 
                    tc.get('expected_result') != tc.get('expected_result_original')):
                    
                    print(f"\n   🎯 Expected Result corregido ({worksheet_name}):")
                    print(f"      ANTES:   {tc['expected_result_original']}")
                    print(f"      DESPUÉS: {tc['expected_result']}")
                    examples_count += 1
        
        if examples_count == 0:
            print("   (No se encontraron correcciones para mostrar como ejemplo)")
        
        # Resumen final
        print(f"\n🎉 PROCESAMIENTO COMPLETADO EXITOSAMENTE")
        print(f"   📊 Estadísticas finales:")
        print(f"      • Archivo original: {excel_file}")
        print(f"      • Archivo corregido: {output_file}")
        print(f"      • Worksheets procesados: {correction_results['total_worksheets']}")
        print(f"      • Casos de prueba analizados: {correction_results['total_test_cases']}")
        print(f"      • Correcciones aplicadas: {correction_results['total_corrections']}")
        print(f"      • Tasa de corrección: {(correction_results['total_corrections'] / correction_results['total_test_cases'] * 100):.1f}%")
        
        print(f"\n💡 PRÓXIMOS PASOS:")
        print(f"   1. Abrir el archivo corregido: {output_file}")
        print(f"   2. Revisar las celdas resaltadas en amarillo")
        print(f"   3. Verificar que solo se modificaron NombreID y Expected Result")
        print(f"   4. Consultar el resumen detallado: {summary_file}")
        
    except ImportError as e:
        print(f"\n❌ Error de importación: {e}")
        print("💡 Verifica que todos los módulos estén correctamente instalados")
    except FileNotFoundError as e:
        print(f"\n❌ Archivo no encontrado: {e}")
        print("💡 Verifica la ruta del archivo Excel")
    except Exception as e:
        print(f"\n❌ Error durante el procesamiento: {e}")
        import traceback
        print("\n🔍 Detalles del error:")
        traceback.print_exc()
        

if __name__ == "__main__":
    main()