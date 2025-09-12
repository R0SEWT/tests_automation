# Automatizador de Casos de Prueba

## Descripción

Este proyecto tiene como objetivo la **creación automatizada de casos de prueba** mediante dos vías principales:

1. **Importación desde Jira**: 
   - **Descripción**: Extrae casos de prueba existentes desde Jira utilizando Selenium o la API de Jira.
   - **Proceso**: Una vez importados, se utilizan modelos de lenguaje (LLM) para generar casos de prueba de calidad.
   - **Salida**: Genera un archivo Excel con los casos de prueba procesados.

2. **Generación desde Documentación**: 
   - **Descripción**: Analiza la documentación existente para generar nuevos casos de prueba.
   - **Proceso**: Utiliza modelos de lenguaje (LLM) para crear casos de prueba de alta calidad a partir de la documentación proporcionada.
   - **Salida**: Genera un archivo Excel con los casos de prueba generados.

## Características

- **Importación desde Jira**:
  - Conexión con Jira mediante Selenium o API.
  - Extracción y procesamiento de casos de prueba existentes.
  - Generación de casos de prueba mejorados utilizando LLM.
  - Exportación de resultados a Excel.

- **Generación desde Documentación**:
  - Lectura y análisis de documentación en formatos XML y otros.
  - Uso de modelos de lenguaje para crear casos de prueba detallados.
  - Exportación de resultados a Excel.

## Instalación

1. **Clonar el repositorio**:
    ```bash
    git clone https://github.com/tu_usuario/tests_automation.git
    cd tests_automation
    ```

2. **Crear y activar un entorno virtual con Conda**:
    ```bash
    conda create -n tests_automation python=3.9
    conda activate tests_automation
    ```

3. **Instalar las dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

## Uso

1. **Configurar Variables de Entorno**:
   - Crea un archivo `.env` en la carpeta `config/` con las credenciales necesarias para Jira y otros servicios.

2. **Ejecutar el Script Principal**:
    ```bash
    python src/main.py
    ```

3. **Resultados**:
   - Los archivos Excel generados se guardarán en la carpeta `output/`.

## Estructura del Proyecto

```bash
tests_automation/
├── config/
│   └── .env                # Variables de entorno, credenciales
├── data/
│   └── ...                 # Archivos XML, CSV o documentación importada
├── notebooks/
│   └── ...                 # Prototipos o análisis rápidos en Jupyter
├── output/
│   └── ...                 # Excels generados con los casos de prueba
├── src/
│   ├── jira_import/
│   │   ├── jira_selenium.py    # Lógica de Selenium (si corresponde)
│   │   └── jira_api.py         # Lógica de conexión a la API de Jira
│   ├── doc_parser/
│   │   └── doc_extract.py      # Lógica para leer la documentación
│   ├── llm/
│   │   └── generator.py        # Módulo con la lógica de generación vía LLM
│   └── main.py
└── requirements.txt