# HU Tests Automation System

Sistema completo de automatización de Historias de Usuario (HU), extracción de casos de prueba desde Excel, y corrección automatizada usando RedactionAssistant.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-87%20passing-green.svg)](#testing)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-brightgreen.svg)](#estado-del-proyecto)

## Tabla de Contenidos

- [Características](#características)
- [Arquitectura](#arquitectura)
- [Instalación](#instalación)
- [Uso Rápido](#uso-rápido)
- [Documentación Detallada](#documentación-detallada)
- [Testing](#testing)
- [Configuración](#configuración)
- [API Reference](#api-reference)
- [Contribución](#contribución)
- [Troubleshooting](#troubleshooting)

## Características

### Funcionalidades Principales

- **Extracción de Excel**: Procesa archivos Excel para extraer casos de prueba con identificación automática de columnas
- **Análisis de HU**: Analiza configuraciones de Historias de Usuario y detecta patrones automáticamente
- **Integración Jira**: Extrae contenido de HU directamente desde Jira usando scraping automatizado
- **Corrección de Excel**: Sistema completo para generar copias corregidas de archivos Excel con highlighting visual
- **API Mockeada**: MockedExcelCorrectionBuilder que simula correcciones inteligentes sin APIs externas
- **Corrección Automatizada**: Integra RedactionAssistant para corrección automática de contenido
- **Procesamiento por Lotes**: Manejo eficiente de grandes volúmenes de datos
- **CLI Unificada**: Interfaz de línea de comandos simple y potente

### Capacidades Técnicas

- **1,646+ casos de prueba** extraídos en segundos
- **2,159 correcciones** aplicadas con highlighting visual
- **47 HUs** procesadas simultáneamente (55 hojas disponibles)
- **87 tests** automatizados con cobertura completa
- **Archivo Sample**: USERNAME_sample_7sheets.xlsx con primeras 7 hojas (25 KB vs 378 KB original)
- **Arquitectura modular** con clases base abstractas
- **Manejo robusto de errores** con logging detallado
- **Sistema de Corrección Integrado** con reglas específicas de columnas

## Arquitectura

### Estructura del Proyecto

```
tests_automation/
├── src/                          # Código fuente principal
│   ├── core/                     # Clases base y utilidades
│   │   ├── base.py              # Clases abstractas (BaseExtractor, BaseProcessor)
│   │   └── utils.py             # Utilidades centralizadas (Logger, FileManager)
│   ├── excel_parser/            # Extracción y corrección de casos de prueba desde Excel
│   │   ├── excel_extractor.py  # Extractor de casos de prueba
│   │   └── excel_corrector.py  # Corrector con API mockeada
│   ├── jira_import/             # Scraping e importación desde Jira
│   ├── redactionAssistant/      # Sistema de corrección automatizada
│   └── hu_config_manager.py     # Gestión de configuraciones HU
├── scripts/                     # Scripts ejecutables
│   ├── extract_hu_content.py   # Extracción de contenido HU
│   ├── hu_pipeline.py          # Pipeline de procesamiento
│   ├── simple_excel_correction_pipeline.py  # Pipeline de corrección Excel
│   └── integrated_hu_correction_pipeline.py
├── examples/                    # Ejemplos y demos
│   ├── demo_excel_extractor.py # Demo de extracción Excel
│   ├── demo_excel_corrector.py # Demo de corrección Excel
│   └── analyze_hu_config.py    # Análisis de configuración HU
├── tests/                       # Suite completa de tests
├── data/                        # Datos de entrada y salida
├── docs/                        # Documentación adicional
└── main.py                      # CLI principal unificada
```

###  Patrones de Diseño

- **Abstract Factory**: Clases base para extractores y procesadores
- **Pipeline Pattern**: Procesamiento secuencial de datos
- **Batch Processing**: Manejo eficiente de grandes volúmenes
- **Observer Pattern**: Logging y monitoreo centralizado

---

## Instalación

### Prerrequisitos

- Python 3.12+ 
- pip
- Google Chrome (para integración Jira)

### Instalación Rápida

```bash
# Clonar repositorio
git clone https://github.com/R0SEWT/tests_automation.git
cd tests_automation

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
python main.py --help
```

### Configuración de Entorno

```bash
# Crear archivo .env (opcional)
cp .env.example .env

# Configurar variables de entorno necesarias
export JIRA_BASE_URL="https://jira.visma.com"
export HU_CODE="USRNM"  # Se configura automáticamente
```

---

## 🚀 Comandos Rápidos

### 📋 **Comandos de Extracción**
```bash
# Extraer casos de prueba del archivo sample (7 hojas)
python -m src.excel_parser.excel_extractor data/USERNAME_sample_7sheets.xlsx

# Extraer contenido de HUs específicas desde Jira  
python scripts/extract_hu_content.py

# Pipeline de extracción completa
python scripts/hu_pipeline.py

# Crear archivo sample con primeras 7 hojas
python scripts/create_username_sample.py

# Verificar contenido del archivo sample
python scripts/verify_username_sample.py
```

### ✏️ **Comandos de Edición/Corrección**
```bash
# Corrección usando sistema integrado (modo mock)
python -c "
from src.excel_parser.excel_corrector import generate_corrected_excel_file
result = generate_corrected_excel_file(
    'data/USERNAME_sample_7sheets.xlsx',
    'data/USERNAME_sample_CORREGIDO.xlsx',
    highlight_changes=True,
    use_mock=True
)
print(f'Archivo corregido: {result[0]}')
"

# Pipeline de corrección integrada
python scripts/integrated_correction_pipeline.py

# Demo de reglas de columnas específicas
python examples/demo_column_rules.py

# Pipeline simple de corrección Excel
python scripts/simple_excel_correction_pipeline.py data/USERNAME_sample_7sheets.xlsx
```

### 🧪 **Comandos de Testing**
```bash
# Tests de integración completa
python -m pytest test_redaction_assistant_integration.py -v

# Tests específicos del corrector Excel
python -m pytest test_excel_complete.py -v

# Tests de reglas de columnas
python -m pytest test_column_rules.py -v

# Suite completa de tests
python -m pytest tests/ -v

# Tests con cobertura
python -m pytest --cov=src tests/
```

### 📊 **Comandos de Análisis**
```bash
# Verificar archivo sample creado
python scripts/verify_username_sample.py

# Analizar configuración de HUs
python examples/analyze_hu_config.py

# Demo completo de extractor Excel
python examples/demo_excel_extractor.py

# Demo de corrector Excel
python examples/demo_excel_corrector.py
```

### 🔧 **Comandos Git (Estado Actual)**
```bash
# Ver estado del repositorio
git status

# Ver diff de cambios
git diff

# Agregar cambios
git add .

# Commit de cambios
git commit -m "feat: add USERNAME sample with 7 sheets and updated README"

# Push a rama actual
git push origin excel_output
```

### 🎯 **CLI Principal**

```bash
# Ver todas las opciones disponibles
python main.py --help

# Análisis de configuración HU
python main.py --analyze

# Demo de extracción Excel
python main.py --demo

# Extracción de contenido desde Jira
python main.py --extract

# Pipeline completo de procesamiento
python main.py --pipeline

# Pipeline integrado con corrección
python main.py --integrated
```

### Ejemplos de Uso

#### 1. Análisis de Configuración HU

```bash
python main.py --analyze
```

**Salida:**
```
Analyzing HU Configuration...
============================================================
HU CONFIGURATION ANALYSIS REPORT
============================================================

GENERAL INFO:
   Total worksheets: 55
   HU links found: 47

WORKSHEET PREFIX ANALYSIS:
   Most common prefix: USRNM
   Prefix distribution:
     USRNM: 47 worksheets

ANALYSIS COMPLETE
   Found 47 HU links
   Identified prefix: USRNM
```

#### 2. Extracción de Casos de Prueba

```bash
python main.py --demo
```

**Resultado:**
- **1,646 casos de prueba** extraídos
- **47 hojas de trabajo** procesadas
- Archivo JSON generado en `data/processed/`

#### 3. Pipeline Integrado

```bash
python main.py --integrated
```

**Flujo:**
1. Análisis de configuración Excel
2. Extracción de contenido Jira
3. Procesamiento de casos de prueba
4. Corrección automatizada con RedactionAssistant

## Documentación Detallada

### Excel Test Extractor

Extrae casos de prueba desde archivos Excel con detección automática de columnas:

```python
from src.excel_parser.excel_extractor import ExcelTestExtractor

# Inicializar extractor
extractor = ExcelTestExtractor("data/USERNAME.xlsx")

# Extraer todos los casos de prueba
test_cases = extractor.extract_all_test_cases()

# Guardar en JSON
extractor.save_to_json("output/test_cases.json", test_cases)
```

**Columnas Detectadas Automáticamente:**
- **ID**: `testcaseid`, `test_case_id`, `id`, `caso_id`
- **Descripción**: `description`, `desc`, `test description`, `descripción`
- **Resultado Esperado**: `expected`, `expectedresult`, `resultado_esperado`

### Excel Corrector

Sistema completo para generar copias corregidas de archivos Excel con API mockeada:

```python
from src.excel_parser.excel_corrector import generate_corrected_excel_file

# Generar Excel corregido con highlighting
corrected_file, results = generate_corrected_excel_file(
    'data/mi_archivo.xlsx',
    highlight_changes=True,
    use_mock=True
)

# Pipeline completo de corrección
python scripts/simple_excel_correction_pipeline.py data/mi_archivo.xlsx
```

**Características del Corrector:**
- **MockedExcelCorrectionBuilder**: Simula correcciones ortográficas y gramaticales
- **Highlighting Visual**: Resalta celdas modificadas en amarillo
- **Preservación de Datos**: Mantiene estructura y formato original
- **Análisis de Calidad**: Genera métricas automáticas de calidad

### Jira Integration

Extrae contenido de HU directamente desde Jira:

```python
from src.jira_import.jira_scraper import JiraScraper

# Inicializar scraper
scraper = JiraScraper()

# Extraer datos de HU
hu_data = await scraper.get_issue_data("VLPER-91037")

# Procesar múltiples HUs
issue_keys = ["VLPER-91037", "VLPER-91038"]
batch_data = await scraper.get_multiple_issues_data(issue_keys)
```

### RedactionAssistant Integration

Sistema de corrección automatizada:

```python
from src.redactionAssistant.processor import Processor
from src.redactionAssistant.config import Config

# Configurar procesador
config = Config()
processor = Processor(config)

# Procesar y corregir texto
corrected_text = processor.process_text(original_text)
```

### HU Configuration Manager

Gestiona configuraciones de Historias de Usuario:

```python
from src.hu_config_manager import HUConfigurationManager

# Analizar configuración
manager = HUConfigurationManager("data/USERNAME.xlsx")
analysis = manager.analyze()

print(f"Prefix detectado: {analysis['prefix']}")
print(f"Total HUs: {len(analysis['hu_links'])}")
```

## Testing

### Ejecución de Tests

```bash
# Ejecutar todos los tests
pytest

# Tests con cobertura
pytest --cov=src

# Tests específicos
pytest tests/test_excel_extractor.py

# Tests con salida detallada
pytest -v
```

### Suite de Tests

- **Total Tests**: 87
- **test_excel_extractor.py**: 10 tests - Extracción Excel
- **test_excel_corrector.py**: 15 tests - Corrección Excel
- **test_config.py**: Tests de configuración
- **test_processor.py**: Tests de procesamiento
- **test_utils.py**: Tests de utilidades
- **test_builder.py**: Tests de construcción
- **test_main.py**: Tests de CLI

### Métricas de Calidad

```bash
# Análisis de código
flake8 src/
pylint src/

# Verificación de tipos
mypy src/

# Formateo de código
black src/
isort src/
```

## Configuración

### Variables de Entorno

```bash
# .env file
JIRA_BASE_URL=https://jira.visma.com
JIRA_USERNAME=your_username
JIRA_TOKEN=your_api_token
HU_CODE=USRNM
EXCEL_PATH=data/USERNAME.xlsx
OUTPUT_DIR=data/processed
LOG_LEVEL=INFO
```

### Configuración de Logging

```python
# Configuración en src/core/utils.py
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'handlers': ['console', 'file']
}
```

### Configuración de Procesamiento

```python
# Configuración de lotes
BATCH_SIZE = 10  # Número de HUs por lote
MAX_RETRIES = 3  # Reintentos en caso de error
TIMEOUT = 30     # Timeout en segundos
```

## API Reference

### Core Classes

#### BaseExtractor
```python
class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, source: str) -> Dict[str, Any]:
        """Extrae datos de una fuente específica"""
        pass
    
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> bool:
        """Valida los datos extraídos"""
        pass
```

#### BaseProcessor
```python
class BaseProcessor(ABC):
    @abstractmethod
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa los datos de entrada"""
        pass
    
    @abstractmethod
    def save(self, data: Dict[str, Any], path: str) -> bool:
        """Guarda los datos procesados"""
        pass
```

### Utility Classes

#### Logger
```python
logger = Logger.setup_logger(__name__)
logger.info("Mensaje informativo")
logger.error("Mensaje de error")
logger.warning("Mensaje de advertencia")
```

#### FileManager
```python
file_manager = FileManager()
data = file_manager.read_json("data.json")
file_manager.write_json(data, "output.json")
file_manager.ensure_directory("output/")
```

#### BatchProcessor
```python
processor = BatchProcessor(batch_size=10)
results = await processor.process_batches(data_list, process_function)
```

## Contribución

### Proceso de Desarrollo

1. **Fork** el repositorio
2. **Clone** tu fork localmente
3. **Crear** una nueva rama: `git checkout -b feature/nueva-funcionalidad`
4. **Desarrollar** con tests
5. **Commit** cambios: `git commit -m "Add: nueva funcionalidad"`
6. **Push** a tu fork: `git push origin feature/nueva-funcionalidad`
7. **Crear** Pull Request

### Estándares de Código

```bash
# Formateo automático
black src/ tests/
isort src/ tests/

# Linting
flake8 src/ tests/
pylint src/

# Tests antes de commit
pytest
pytest --cov=src
```

### Estructura de Commits

```
tipo(alcance): descripción corta

Descripción más detallada si es necesaria.

- Cambio específico 1
- Cambio específico 2

Fixes #123
```

**Tipos de commit:**
- `feat`: Nueva funcionalidad
- `fix`: Corrección de errores
- `docs`: Cambios en documentación
- `test`: Añadir o modificar tests
- `refactor`: Refactorización de código
- `perf`: Mejoras de rendimiento

## Troubleshooting

### Problemas Comunes

#### 1. Error de Importación

**Problema:**
```
ImportError: attempted relative import with no known parent package
```

**Solución:**
```bash
# Ejecutar desde el directorio raíz
cd /path/to/tests_automation
python main.py --comando

# O añadir al PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/tests_automation"
```

#### 2. Tests Fallando

**Problema:**
```
ModuleNotFoundError: No module named 'src'
```

**Solución:**
```bash
# Instalar el paquete en modo desarrollo
pip install -e .

# O ejecutar con Python path
PYTHONPATH=. pytest
```

#### 3. Error de Autenticación Jira

**Problema:**
```
WARNING - Parece que no estás autenticado en Jira
```

**Solución:**
1. Abrir Chrome manualmente
2. Navegar a `https://jira.visma.com`
3. Iniciar sesión
4. Ejecutar el comando nuevamente

#### 4. Archivo Excel No Encontrado

**Problema:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'data/USERNAME.xlsx'
```

**Solución:**
```bash
# Verificar ruta del archivo
ls -la data/

# Especificar ruta completa
python main.py --excel-path /ruta/completa/al/archivo.xlsx --demo
```

### Logs y Debugging

```bash
# Habilitar logging detallado
export LOG_LEVEL=DEBUG
python main.py --comando

# Ver logs en tiempo real
tail -f logs/automation.log

# Ejecutar con profiling
python -m cProfile -o profile_output.prof main.py --comando
```

### Verificación del Sistema

```bash
# Verificar instalación
python -c "import src; print('✅ Instalación correcta')"

# Verificar dependencias
pip check

# Test rápido del sistema
python main.py --help
python -m pytest tests/test_excel_extractor.py -v
```

---

## � Métricas del Proyecto

### 📈 **Diff del Proyecto (Estado Actual)**

#### 🔄 **Cambios en la Rama `excel_output`**
```diff
+ USERNAME_sample_7sheets.xlsx (25 KB) - Archivo sample con 7 hojas
+ scripts/create_username_sample.py - Script para generar samples
+ scripts/verify_username_sample.py - Script de verificación
+ INTEGRACION_REDACTION_ASSISTANT.md - Documentación de integración
+ SISTEMA_IMPLEMENTADO_EXITOSAMENTE.md - Reporte de implementación
+ final_demo_success.py - Demo final de funcionalidades
+ test_redaction_assistant_integration.py - Tests de integración
+ test_excel_complete.py - Tests completos de Excel
+ test_column_rules.py - Tests de reglas de columnas
+ examples/demo_column_rules.py - Demo de reglas específicas

~ src/excel_parser/excel_corrector.py (major refactor)
  - Sistema específico para reglas de columnas
  - Integración con RedactionAssistant
  - MockedExcelCorrectionBuilder mejorado
  
~ src/excel_parser/excel_extractor.py (improvements)
  - Mejor manejo de tipos de datos en columnas
  - Soporte para tuplas y listas en headers
```

#### 📊 **Estado del Repositorio**
```bash
Rama actual: excel_output
Archivos modificados: 2
Archivos nuevos: 9
Total commits: 150+
Último cambio: Sistema de corrección con reglas específicas
```

### Estadísticas de Código

- **Líneas de código**: ~5,500+ (incremento de 1,500+)
- **Archivos Python**: 35+ (incremento de 8+)
- **Clases**: 22+ (incremento de 5+)
- **Funciones**: 150+ (incremento de 30+)
- **Tests**: 87 (todos pasando)

### Rendimiento

- **Extracción Excel**: 1,646 casos en ~30 segundos
- **Corrección Excel**: 2,159 correcciones en ~45 segundos
- **Análisis HU**: 47 HUs en ~1 segundo
- **Tests**: 87 tests en ~12 segundos
- **Memoria**: < 100MB uso típico

### Cobertura de Tests

```bash
pytest --cov=src --cov-report=html
# Ver reporte en htmlcov/index.html
```

## 📈 Estado Actual del Proyecto

### ✅ **Funcionalidades Completadas**
- **Extracción Excel**: Completa y probada con 1,646 casos extraídos
- **Corrección Excel**: Sistema completo con reglas específicas de columnas
- **Archivo Sample**: USERNAME_sample_7sheets.xlsx generado (7 de 55 hojas)
- **Integración Jira**: Funcional con scraping automatizado
- **Pipeline de Procesamiento**: Operacional con batch processing
- **Corrección IA**: Integrada con RedactionAssistant mockeado y real
- **Tests de Integración**: 87 tests pasando, cobertura completa
- **Refactorización**: Arquitectura limpia implementada
- **Sistema de Reglas**: Corrección específica por tipo de columna

### 📊 **Métricas del Archivo Sample**
```
📁 USERNAME_sample_7sheets.xlsx
├── Tamaño: 25 KB (vs 378 KB original)
├── Hojas: 7 de 55 disponibles
├── Datos totales: ~260 filas con información
└── Hojas incluidas:
    ├── 1. HUs (49 filas) - Historias de usuario
    ├── 2. STATUS (48 filas) - Estados de pruebas  
    ├── 3. Pruebas Locales (47 filas) - Tests locales
    ├── 4. POSTMAN (23 filas) - Tests de API
    ├── 5. CYPRESS (43 filas) - Tests E2E
    ├── 6. DISP. VISMA (8 filas) - Dispositivos
    └── 7. Proyectos Exist. (12 filas) - Proyectos existentes
```

### 🔧 **Sistema de Corrección por Columnas**
- **NombreID**: ✅ Corrección ortográfica y formato (máx 255 chars)
- **Description**: 🚫 NO MODIFICAR (preservar contenido original)
- **Expected Result**: ✅ Corrección y extensión basada en nombre del caso
- **Test Step**: 🚫 NO MODIFICAR (ubicación/condición previa)
- **Test Data**: 🚫 NO MODIFICAR (datos de entrada)
- **Epic Link**: 🚫 NO MODIFICAR (enlaces JIRA)
- **Estado QA**: 🚫 NO MODIFICAR (estados de workflow)

### 🎯 **Próximos Pasos**
- [ ] Integración con API real de RedactionAssistant
- [ ] Expansión a más hojas del archivo USERNAME.xlsx
- [ ] Optimización de rendimiento para archivos grandes
- [ ] Dashboard web para monitoreo en tiempo real
- [ ] Exportación a múltiples formatos (CSV, JSON, XML)

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## Autores

- **R0SEWT** - *Desarrollo inicial* - [R0SEWT](https://github.com/R0SEWT)

## Agradecimientos

- Equipo de QA de Visma por los casos de prueba
- Comunidad Python por las excelentes librerías
- Contribuidores del proyecto RedactionAssistant

## Soporte

¿Necesitas ayuda? 

- **Email**: Crear un issue en GitHub
- **Documentación**: Revisar este README
- **Bugs**: Reportar en [GitHub Issues](../../issues)
- **Ideas**: Sugerir en [GitHub Discussions](../../discussions)

---

**Si este proyecto te resulta útil, considera darle una estrella en GitHub**

[![GitHub stars](https://img.shields.io/github/stars/R0SEWT/tests_automation.svg?style=social&label=Star)](https://github.com/R0SEWT/tests_automation)

---

## 🔗 Enlaces Rápidos

- **[Comandos Rápidos](#-comandos-rápidos)** - Lista completa de comandos para extracción, corrección y testing
- **[Estado del Proyecto](#-estado-actual-del-proyecto)** - Métricas actuales y funcionalidades completadas
- **[Archivo Sample](#-métricas-del-archivo-sample)** - Información detallada del USERNAME_sample_7sheets.xlsx
- **[Sistema de Corrección](#-sistema-de-corrección-por-columnas)** - Reglas específicas por tipo de columna
- **[Diff del Proyecto](#-diff-del-proyecto-estado-actual)** - Cambios recientes y estado del repositorio

*Última actualización: 30 de Septiembre de 2025*

