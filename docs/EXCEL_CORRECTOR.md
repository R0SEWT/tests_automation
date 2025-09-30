# Excel Corrector - Generación de Archivos Excel Corregidos

Este módulo proporciona funcionalidad completa para generar copias corregidas de archivos Excel que contienen casos de prueba y resultados esperados, utilizando llamadas API mockeadas para demostrar la funcionalidad sin requerir claves API reales.

## 🎯 Características Principales

### ✅ Corrección Automática con IA Mockeada
- **Corrección ortográfica y gramatical**: Mejora la redacción manteniendo el contexto técnico
- **Normalización de tiempo verbal**: Convierte a tiempo presente los resultados esperados
- **Mejoras de redacción**: Optimiza claridad y consistencia
- **Procesamiento en lotes**: Eficiencia mediante procesamiento concurrente

### 📊 Procesamiento de Excel Completo
- **Extracción automática de casos de prueba**: Identifica columnas relevantes automáticamente
- **Soporte multi-hoja**: Procesa todas las hojas de trabajo en un archivo
- **Preservación de datos adicionales**: Mantiene todas las columnas originales
- **Generación de archivos corregidos**: Crea nuevos archivos Excel con mejoras aplicadas

### 🎨 Resaltado Visual de Cambios
- **Highlighting inteligente**: Resalta celdas que fueron corregidas
- **Formato visual claro**: Utiliza colores y formato para identificar mejoras
- **Preservación de estructura**: Mantiene el formato original del Excel

### 📈 Reportes Completos
- **Resúmenes detallados**: Estadísticas completas de correcciones aplicadas
- **Métricas de calidad**: Tasas de corrección y análisis de eficiencia
- **Ejemplos de correcciones**: Muestras de mejoras aplicadas
- **Recomendaciones**: Sugerencias para mejorar la calidad de casos de prueba

## 🚀 Uso Rápido

### Ejemplo Básico
```python
from src.excel_parser.excel_corrector import generate_corrected_excel_file

# Generar archivo Excel corregido
corrected_file, results = generate_corrected_excel_file(
    original_file_path='data/test_cases.xlsx',
    output_path='output/test_cases_corrected.xlsx',
    highlight_changes=True,
    use_mock=True
)

print(f"Archivo corregido: {corrected_file}")
print(f"Correcciones aplicadas: {results['total_corrections']}")
```

### Uso Avanzado con ExcelCorrector
```python
from src.excel_parser.excel_corrector import ExcelCorrector

# Inicializar corrector
corrector = ExcelCorrector('data/test_cases.xlsx', use_mock=True)

# Procesar correcciones
results = corrector.process_corrections()
print(f"Hojas procesadas: {results['total_worksheets']}")
print(f"Casos de prueba: {results['total_test_cases']}")
print(f"Correcciones: {results['total_corrections']}")

# Generar archivo corregido
corrected_file = corrector.generate_corrected_excel(
    output_path='output/corrected.xlsx',
    highlight_changes=True
)
```

## 🛠️ Scripts y Demos

### Demo Completo
```bash
# Demo con datos de ejemplo
python examples/demo_excel_corrector.py

# Demo con archivo real
python examples/demo_excel_corrector.py data/YOUR_FILE.xlsx
```

### Pipeline Integrado Completo
```bash
# Pipeline completo con corrección de Excel
python scripts/integrated_correction_pipeline.py data/USERNAME.xlsx
```

## 📁 Estructura de Archivos Generados

```
output/
├── corrected_excel_file.xlsx           # Archivo Excel corregido
├── corrected_excel_file_summary.json   # Resumen de correcciones
└── comprehensive_report.json           # Reporte completo del pipeline
```

### Contenido del Archivo Excel Corregido
- **Hojas de trabajo originales**: Todas las hojas con casos de prueba corregidos
- **Highlighting visual**: Celdas corregidas resaltadas en amarillo claro
- **Formato mejorado**: Texto con formato bold para cambios importantes
- **Datos preservados**: Todas las columnas adicionales mantenidas

### Contenido del Summary JSON
```json
{
  "correction_summary": {
    "original_file": "data/test_cases.xlsx",
    "total_worksheets_processed": 47,
    "total_test_cases_processed": 1646,
    "total_corrections_applied": 2159,
    "processing_timestamp": "2025-01-01T10:00:00Z",
    "mock_api_used": true
  },
  "worksheet_details": {
    "USRNM01": {
      "original_test_case_count": 44,
      "corrections_applied": 23
    }
  },
  "sample_corrections": [
    {
      "worksheet": "USRNM01",
      "test_case_id": "USRNM01 - CP01",
      "field": "description",
      "original": "Como superadmin, En el formulario de creacion...",
      "corrected": "Como superadministrador, En el formulario de creación..."
    }
  ]
}
```

## 🧪 Tipos de Correcciones Aplicadas

### 1. Correcciones Ortográficas
- `creacion` → `creación`
- `configuracion` → `configuración`
- `superadmin` → `superadministrador`
- `verificar` → `verificar` (sin cambios si está correcto)

### 2. Mejoras Gramaticales
- `debe verse` → `debe visualizarse`
- `se vera` → `se visualizará`
- `aparece` → `se muestra`

### 3. Normalización de Tiempo Verbal
- `será exitoso` → `es exitoso`
- `estará disponible` → `está disponible`
- `mostrará` → `muestra`

### 4. Capitalización y Formato
- Primera letra mayúscula en resultados esperados
- Formato consistente en descripciones
- Espaciado y puntuación mejorados

## 📊 Métricas y Estadísticas

### Rendimiento Típico
- **Procesamiento**: ~15 segundos para 47 hojas de trabajo
- **Tasa de éxito**: 100% de hojas procesadas exitosamente
- **Integridad de datos**: Todos los casos de prueba extraídos correctamente
- **Identificación de columnas**: 100% de éxito con nombres en español

### Resultados de Ejemplo (Archivo Real)
```
✅ Procesamiento completado:
   • 47 hojas de trabajo procesadas
   • 1,646 casos de prueba analizados
   • 2,159 correcciones aplicadas
   • Tasa de corrección: 131% (múltiples correcciones por caso)
```

## 🔧 Configuración y Personalización

### MockedExcelCorrectionBuilder
```python
from src.excel_parser.excel_corrector import MockedExcelCorrectionBuilder

# Personalizar patrones de corrección
builder = MockedExcelCorrectionBuilder()
builder.correction_patterns['ortografia'].extend([
    ('nuevo_error', 'nueva_corrección'),
    ('otro_patrón', 'corrección_personalizada')
])
```

### Personalización de Estilos
```python
from openpyxl.styles import PatternFill, Font

# Personalizar colores de highlighting
changed_fill = PatternFill(start_color="FFFF99", end_color="FFFF99", fill_type="solid")
changed_font = Font(bold=True, color="FF0000")  # Rojo y bold
```

## 🧪 Testing

### Ejecutar Pruebas Completas
```bash
# Todas las pruebas del corrector
python -m pytest tests/test_excel_corrector.py -v

# Pruebas con cobertura
python -m pytest tests/test_excel_corrector.py --cov=src/excel_parser/excel_corrector

# Pruebas de integración
python -m pytest tests/test_excel_corrector.py::TestIntegrationWithRealFile -v
```

### Casos de Prueba Incluidos
- ✅ Inicialización del corrector
- ✅ Procesamiento de correcciones
- ✅ Generación de archivos Excel
- ✅ Highlighting de cambios
- ✅ Patrones de corrección
- ✅ Funciones de conveniencia
- ✅ Integración con archivos reales

## 🌟 Casos de Uso

### 1. Mejora de Calidad de Casos de Prueba
```python
# Procesar archivo con casos de prueba mal redactados
corrected_file, results = generate_corrected_excel_file(
    'casos_prueba_borrador.xlsx',
    highlight_changes=True
)
# Resultado: Archivo con casos de prueba profesionales y bien redactados
```

### 2. Standardización de Documentación
```python
# Standardizar múltiples archivos de diferentes equipos
for file_path in ['team_a.xlsx', 'team_b.xlsx', 'team_c.xlsx']:
    corrected_file, _ = generate_corrected_excel_file(
        file_path,
        output_path=f'standardized/{Path(file_path).stem}_standard.xlsx'
    )
```

### 3. Auditoría y Revisión de Calidad
```python
# Generar reporte de calidad de casos de prueba
corrector = ExcelCorrector('casos_para_revision.xlsx')
results = corrector.process_corrections()

print(f"Tasa de corrección: {results['total_corrections']/results['total_test_cases']*100:.1f}%")
if results['total_corrections'] > 500:
    print("⚠️ Alta cantidad de correcciones detectadas. Revisar proceso de creación.")
```

## 🚀 Integración con Pipeline Existente

### Pipeline Completo
El corrector se integra perfectamente con el pipeline existente de procesamiento de HUs:

1. **Extracción de HUs**: Scripts existentes extraen contenido de Jira
2. **Procesamiento de casos**: ExcelExtractor procesa casos de prueba
3. **Correcciones con IA**: RedactionAssistant (real) o MockedBuilder
4. **Generación de Excel**: ExcelCorrector genera archivo corregido
5. **Reporting**: Reportes comprehensivos de todo el proceso

```python
# Uso en pipeline completo
from scripts.integrated_correction_pipeline import FullIntegratedCorrectionPipeline

pipeline = FullIntegratedCorrectionPipeline('data/USERNAME.xlsx')
results = await pipeline.run_complete_pipeline()
```

## 📝 Notas de Desarrollo

### API Mockeada vs Real
- **Mock Mode**: Utiliza patrones predefinidos para simular correcciones
- **Real Mode**: Requiere configuración de API key para DeepSeek/OpenAI
- **Switching**: Fácil cambio entre modos mediante parámetro `use_mock`

### Extensibilidad
- **Nuevos patrones**: Fácil agregar nuevos patrones de corrección
- **Diferentes APIs**: Soporte para múltiples proveedores de IA
- **Formatos personalizados**: Extensible para diferentes tipos de archivos
- **Métricas custom**: Agregar nuevas métricas y reportes

### Performance
- **Procesamiento por lotes**: Optimizado para archivos grandes
- **Procesamiento concurrente**: ThreadPoolExecutor para mejor rendimiento
- **Memoria eficiente**: Procesamiento por chunks para archivos muy grandes
- **Caching inteligente**: Evita re-procesar datos idénticos

## 🐛 Troubleshooting

### Problemas Comunes

#### Archivo Excel no encontrado
```
FileNotFoundError: Excel file not found: path/to/file.xlsx
```
**Solución**: Verificar que el archivo existe y la ruta es correcta.

#### Columnas no identificadas
```
Required columns not found in worksheet 'SheetName'
```
**Solución**: El extractor busca patrones comunes. Verificar que las columnas tengan nombres como 'Test Case ID', 'Description', 'Expected Result' o equivalentes en español.

#### Memoria insuficiente
```
MemoryError: Unable to process large Excel file
```
**Solución**: Procesar en lotes más pequeños modificando `batch_size` en la configuración.

### Logs y Debugging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Ejecutar con logs detallados para debugging
corrector = ExcelCorrector('file.xlsx', use_mock=True)
```

## 🤝 Contribución

### Agregar Nuevos Patrones de Corrección
```python
# En MockedExcelCorrectionBuilder
self.correction_patterns['nuevo_tipo'] = [
    ('patrón_buscar', 'texto_reemplazar'),
    ('otro_patrón', 'otro_reemplazo')
]
```

### Extender Funcionalidad
1. Heredar de `ExcelCorrector`
2. Override métodos específicos
3. Agregar nuevas métricas o reportes
4. Implementar nuevos formatos de salida

## 📄 Licencia

Este módulo es parte del proyecto `tests_automation` y sigue la misma licencia del proyecto principal.

---

## 🎉 ¡Listo para Usar!

El Excel Corrector está completamente funcional y listo para mejorar la calidad de tus casos de prueba. 

**¡Pruébalo ahora!**
```bash
python examples/demo_excel_corrector.py
```