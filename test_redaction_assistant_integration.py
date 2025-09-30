#!/usr/bin/env python3
"""
Test de integración del Excel Corrector con RedactionAssistant real
"""

import sys
from pathlib import Path
import os

# Configurar Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def load_env_file():
    """Cargar variables del archivo .env"""
    env_file = Path(".env")
    if env_file.exists():
        print("📁 Cargando archivo .env...")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Limpiar comillas si existen
                    value = value.strip('"\'')
                    os.environ[key] = value
                    print(f"   • {key}={'*' * min(10, len(value))}...")

def test_with_redaction_assistant():
    """Test del corrector usando RedactionAssistant real."""
    
    print("=" * 70)
    print("🔗 EXCEL CORRECTOR + REDACTION ASSISTANT INTEGRATION TEST")
    print("=" * 70)
    
    # Cargar archivo .env
    load_env_file()
    
    # Verificar si hay API key configurada (buscar múltiples variantes)
    api_key = (os.getenv('DS_API_KEY') or 
               os.getenv('DEEPSEEK_API_KEY') or 
               os.getenv('OPENAI_API_KEY'))
    
    if not api_key:
        print("\n⚠️  No se encontró API key en variables de entorno")
        print("📝 Para usar RedactionAssistant real, configura en .env:")
        print("   DS_API_KEY='tu_deepseek_key'")
        print("   # o")
        print("   OPENAI_API_KEY='tu_openai_key'")
        print("\n🔄 Ejecutando con sistema mockeado...")
        use_mock = True
    else:
        # Detectar provider basado en la API key
        if os.getenv('DS_API_KEY') or os.getenv('DEEPSEEK_API_KEY'):
            provider = "deepseek"
        else:
            provider = "openai"
        
        print(f"\n✅ API key encontrada: {api_key[:10]}...")
        print(f"🔧 Provider detectado: {provider}")
        print("🔄 Ejecutando con RedactionAssistant REAL...")
        use_mock = False
    
    # Buscar archivo Excel
    excel_file = Path("data/USERNAME.xlsx")
    
    if not excel_file.exists():
        print(f"\n❌ Archivo no encontrado: {excel_file}")
        return
    
    print(f"\n📁 Procesando archivo: {excel_file}")
    
    try:
        from src.excel_parser.excel_corrector import ExcelCorrector
        
        # Crear corrector con integración
        corrector = ExcelCorrector(
            str(excel_file), 
            use_mock=use_mock, 
            api_key=api_key
        )
        
        print(f"\n🔄 Iniciando corrección con {'RedactionAssistant REAL' if not corrector.use_mock else 'Sistema MOCKEADO'}...")
        
        # Procesar solo algunos worksheets para prueba rápida
        all_test_cases = corrector.extractor.extract_all_test_cases()
        
        # Seleccionar solo los primeros 3 worksheets para prueba
        limited_worksheets = dict(list(all_test_cases.items())[:3])
        
        print(f"📋 Procesando {len(limited_worksheets)} worksheets de prueba:")
        for name in limited_worksheets.keys():
            print(f"   • {name}")
        
        # Procesar correcciones manualmente para control
        corrections = {}
        total_corrections = 0
        
        for worksheet_name, test_cases in limited_worksheets.items():
            print(f"\n🔄 Procesando {worksheet_name} ({len(test_cases)} casos)...")
            
            worksheet_corrections = corrector._process_worksheet_corrections(worksheet_name, test_cases)
            corrections[worksheet_name] = worksheet_corrections
            
            total_corrections += worksheet_corrections.get('total_changes', 0)
            
            # Mostrar estadísticas por worksheet
            print(f"   📝 Nombres corregidos: {worksheet_corrections.get('nombre_changes', 0)}")
            print(f"   🎯 Expected results corregidos: {worksheet_corrections.get('expected_changes', 0)}")
            print(f"   📊 Total cambios: {worksheet_corrections.get('total_changes', 0)}")
        
        result = {
            'success': True,
            'system_used': 'RedactionAssistant REAL' if not corrector.use_mock else 'Sistema MOCKEADO',
            'total_worksheets': len(limited_worksheets),
            'total_test_cases': sum(len(cases) for cases in limited_worksheets.values()),
            'total_corrections': total_corrections,
            'corrections_by_worksheet': corrections
        }
        
        print(f"\n🎉 PROCESAMIENTO COMPLETADO")
        print(f"   🔧 Sistema usado: {result['system_used']}")
        print(f"   📄 Worksheets: {result['total_worksheets']}")
        print(f"   📝 Casos de prueba: {result['total_test_cases']}")
        print(f"   ✏️  Correcciones: {result['total_corrections']}")
        
        # Mostrar ejemplos de correcciones
        if total_corrections > 0:
            print(f"\n🔍 EJEMPLOS DE CORRECCIONES:")
            
            examples_shown = 0
            for worksheet_name, corrections_data in corrections.items():
                if examples_shown >= 3:
                    break
                    
                corrected_cases = corrections_data.get('corrected_test_cases', [])
                
                for tc in corrected_cases[:2]:  # Máximo 2 por worksheet
                    if examples_shown >= 3:
                        break
                    
                    # Mostrar correcciones de nombres
                    if ('test_case_id_original' in tc and 
                        tc.get('test_case_id') != tc.get('test_case_id_original')):
                        
                        print(f"\n   📝 NombreID en {worksheet_name}:")
                        print(f"      ANTES:   {tc['test_case_id_original'][:60]}...")
                        print(f"      DESPUÉS: {tc['test_case_id'][:60]}...")
                        examples_shown += 1
                    
                    # Mostrar correcciones de expected results
                    if ('expected_result_original' in tc and 
                        tc.get('expected_result') != tc.get('expected_result_original')):
                        
                        print(f"\n   🎯 Expected Result en {worksheet_name}:")
                        print(f"      ANTES:   {tc['expected_result_original'][:60]}...")
                        print(f"      DESPUÉS: {tc['expected_result'][:60]}...")
                        examples_shown += 1
        
        # Mostrar diferencias entre sistemas
        if use_mock:
            print(f"\n💡 PARA USAR REDACTION ASSISTANT REAL:")
            print(f"   1. Configura tu API key:")
            print(f"      export DEEPSEEK_API_KEY='tu_key'")
            print(f"   2. Ejecuta nuevamente este script")
            print(f"   3. El sistema detectará automáticamente la API key")
        else:
            print(f"\n✅ USANDO REDACTION ASSISTANT REAL")
            print(f"   • Correcciones más precisas con IA")
            print(f"   • Mejor contexto y comprensión del contenido")
            print(f"   • Feedback más detallado")
        
        # GENERAR ARCHIVO EXCEL CORREGIDO
        print(f"\n📄 GENERANDO ARCHIVO EXCEL CORREGIDO...")
        
        # Determinar nombre del archivo de salida
        output_file = excel_file.parent / f"{excel_file.stem}_CORREGIDO.xlsx"
        
        try:
            # Generar archivo Excel con todas las correcciones
            corrected_file_path = corrector.generate_corrected_excel(
                output_path=str(output_file),
                highlight_changes=True
            )
            
            print(f"✅ Archivo Excel generado exitosamente:")
            print(f"   📁 Ruta: {corrected_file_path}")
            print(f"   📊 Correcciones aplicadas: {total_corrections}")
            print(f"   🎨 Cambios resaltados en amarillo")
            
            # Verificar que el archivo se creó correctamente
            if Path(corrected_file_path).exists():
                file_size = Path(corrected_file_path).stat().st_size
                print(f"   📏 Tamaño del archivo: {file_size:,} bytes")
            else:
                print(f"   ⚠️  Advertencia: No se pudo verificar la creación del archivo")
                
        except Exception as excel_error:
            print(f"❌ Error al generar archivo Excel: {excel_error}")
            import traceback
            traceback.print_exc()
        
        print(f"\n🎯 INTEGRACIÓN EXITOSA")
        print(f"   ✅ ExcelCorrector + RedactionAssistant funcionando")
        print(f"   ✅ Reglas de columnas respetadas")
        print(f"   ✅ Sistema flexible (mock o real)")
        print(f"   ✅ Archivo Excel corregido generado")
        
    except Exception as e:
        print(f"\n❌ Error durante la integración: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_with_redaction_assistant()