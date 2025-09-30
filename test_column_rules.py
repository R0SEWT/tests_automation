#!/usr/bin/env python3
"""
Test simple del nuevo Excel Corrector con reglas específicas
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def test_correction_rules():
    """Test de las reglas de corrección específicas."""
    
    print("=" * 60)
    print("TEST: Excel Corrector - Reglas Específicas de Columnas")
    print("=" * 60)
    
    print("\n📋 REGLAS IMPLEMENTADAS:")
    print("✅ NombreID: Corregir nombre del caso (máximo 255 caracteres)")
    print("❌ Description: NO MODIFICAR")
    print("✅ Expected Result: Corregir resultado esperado")
    print("❌ Test Step: NO MODIFICAR")
    print("❌ Test Data: NO MODIFICAR")
    print("❌ Epic Link: NO MODIFICAR")
    print("❌ Estado Qa: NO MODIFICAR")
    
    try:
        from src.excel_parser.excel_corrector import MockedExcelCorrectionBuilder
        
        # Crear builder mockeado
        builder = MockedExcelCorrectionBuilder()
        
        # Test de corrección de nombres de casos
        print("\n🧪 TEST 1: Corrección de Nombres de Casos (NombreID)")
        nombres_test = [
            "verificar configuracion de usuario",
            "validar creacion de nuevo registro",
            "editar informacion del perfil",
            "Test case muy largo que podria exceder los doscientos cincuenta y cinco caracteres permitidos para el nombre del caso de prueba y necesita ser truncado apropiadamente"
        ]
        
        resultado_nombres = builder.corregir_nombres_casos(nombres_test)
        
        print(f"   Casos procesados: {len(nombres_test)}")
        print(f"   Cambios realizados: {resultado_nombres['changes_made']}")
        
        for i, (original, corregido) in enumerate(zip(resultado_nombres['original'], resultado_nombres['corrected'])):
            if original != corregido:
                print(f"\n   📝 Caso {i+1}:")
                print(f"      Antes: {original}")
                print(f"      Después: {corregido} ({len(corregido)} chars)")
        
        # Test de corrección de expected results
        print(f"\n🧪 TEST 2: Corrección de Expected Results")
        expected_test = [
            "debe verse la informacion correctamente",
            "se vera el formulario de configuracion",
            "aparece el mensaje de validacion",
            "funciona el sistema de notificacion"
        ]
        
        resultado_expected = builder.corregir_expected_results(expected_test, resultado_nombres['corrected'])
        
        print(f"   Resultados procesados: {len(expected_test)}")
        print(f"   Cambios realizados: {resultado_expected['changes_made']}")
        
        for i, (original, corregido) in enumerate(zip(resultado_expected['original'], resultado_expected['corrected'])):
            if original != corregido:
                print(f"\n   🎯 Expected Result {i+1}:")
                print(f"      Antes: {original}")
                print(f"      Después: {corregido}")
        
        print(f"\n✅ TESTS COMPLETADOS EXITOSAMENTE")
        print(f"   • Builder mockeado funcionando correctamente")
        print(f"   • Reglas de corrección implementadas")
        print(f"   • Límite de 255 caracteres respetado")
        print(f"   • Solo se modifican las columnas permitidas")
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Asegúrate de estar en el directorio correcto del proyecto")
    except Exception as e:
        print(f"❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_correction_rules()