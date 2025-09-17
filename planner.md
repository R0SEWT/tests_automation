
## 🏁 Sprint 1 — Calidad y Estabilidad (prioridad máxima)

### Issue 1: Tests unitarios base (processor & builder) ≥80% [ HECHO]

**Objetivo:** Cobertura mínima del 80% en módulos `processor` y `builder` con `pytest`.
**Criterios de aceptación:**

* [ ] Tests happy-path y edge cases por función pública
* [ ] Mocks para llamadas a LLM
* [ ] `coverage.xml` generado (para badge/CI)
* [ ] `--cov-fail-under=80` en config
  **DoD:** CI pasa en verde, coverage ≥80%, sin regresión en master.
  **Labels:** `priority:high`, `type:feature`, `area:tests`
  **Estimación:** 5-7 días

---

### Issue 2: CI/CD con GitHub Actions (ruff + pytest + coverage)

**Objetivo:** Pipeline CI ejecuta lint (ruff), tests y publica coverage como artefacto.
**Criterios de aceptación:**

* [ ] Workflow en `.github/workflows/ci.yml`
* [ ] Ruff `check .` sin errores
* [ ] Pytest en modo headless (sin llamadas reales a LLM)
* [ ] Artefacto `coverage.xml` subido
  **DoD:** Badge de CI añadido al README.
  **Labels:** `priority:high`, `type:improvement`, `area:devops`
  **Estimación:** 3-5 días

---

### Issue 3: Logging estructurado + manejo de errores

**Objetivo:** Estandarizar logs y robustecer `try/except` alrededor de lotes y llamadas LLM.
**Criterios de aceptación:**

* [ ] Formato: ts, level, module, hu\_code, batch\_id, msg
* [ ] `try/except` con backoff/retentativas y mensajes claros
* [ ] Registro de diffs/feedback por lote
  **DoD:** README documenta niveles y ejemplos de log.
  **Labels:** `priority:medium`, `type:bug`, `area:observability`
  **Estimación:** 2-3 días

---

## 🔐 Sprint 2 — Seguridad y Resiliencia (alta prioridad)

### Issue 4: Validación de configuración y secretos (.env) — fail fast

**Objetivo:** Validar variables críticas al inicio (provider, API keys, batch sizes) y fallar con mensaje claro.
**Criterios de aceptación:**

* [ ] `config.py` valida presence/format de claves
* [ ] Errores levantan `ConfigError` con hints
  **DoD:** README con sección *Troubleshooting configuración*.
  **Labels:** `priority:high`, `type:feature`, `area:security`
  **Estimación:** 3-4 días

---

### Issue 5: Fallback de proveedor LLM (DeepSeek ↔ OpenAI)

**Objetivo:** Conmutar proveedor por bandera o indisponibilidad.
**Criterios de aceptación:**

* [ ] `builder` acepta `provider={deepseek|openai}`
* [ ] Retry con proveedor alterno ante 5xx/timeouts
* [ ] Logs reflejan proveedor usado por item
  **DoD:** README documenta resiliencia y ejemplo CLI.
  **Labels:** `priority:high`, `type:feature`, `area:resilience`
  **Estimación:** 5-7 días

---

## 🌐 Sprint 3 — API mínima (opcional, diferenciador)

### Issue 6: API mínima FastAPI `/process` (archivo/carpeta → JSON)

**Objetivo:** Exponer endpoint para subir archivo(s) y devolver texto normalizado + feedback.
**Criterios de aceptación:**

* [ ] `POST /process` con `multipart/form-data`
* [ ] Devuelve JSON con `items`, `diff`, `logs_ref`
* [ ] Ruta protegida por token simple (env)
  **DoD:** Ejemplo `curl` en README.
  **Labels:** `priority:medium`, `type:feature`, `area:api`
  **Estimación:** 7-10 días

---

## 📋 Backlog — Nice to have

* **Badges + métricas en README** (`priority:low`, `type:documentation`, `area:dx`, 1-2 días)
* **Auditoría de dependencias + pip-audit** (`priority:medium`, `area:security`, 4-6 días)
* **Parsers DOCX/PDF** (`priority:low`, `area:ingestion`, 5-8 días)
* **Dashboard de métricas (Streamlit/Notebook)** (`priority:low`, `area:observability`, 4-6 días)
* **Versionado semántico + releases** (`priority:low`, `area:release`, 2-3 días)
* **Guías de contribución + templates** (`priority:low`, `area:community`, 3-4 días)



Aspectos positivos
Hay una suite de pruebas amplia que cubre los módulos principales (main, builder, processor, config y utilidades) con escenarios de éxito y de error, lo que facilita detectar regresiones sin depender de llamadas reales al LLM.

Los módulos productivos están bien documentados y usan logging para trazar el flujo, algo clave cuando se orquesta procesamiento concurrente y dependencias externas.

El README y el planner ofrecen una visión clara de arquitectura, roadmap y backlog priorizado, lo que facilita coordinar esfuerzos futuros.

Problemas y oportunidades de mejora
process_flow invoca Processor.exp_corregidos dos veces: primero con los CPS originales y luego con los corregidos, descartando el primer resultado. Esto duplica las llamadas al LLM, incrementa coste/latencia y mezcla feedback parcial antes de guardarlo.

Tarea sugerida
Invocar exp_corregidos una sola vez con CPS corregidos

Iniciar tarea
El pipeline de expected results usa cps.splitlines()/exp.splitlines() sin limpiar vacíos, por lo que rechaza pares válidos si hay líneas en blanco, y además envía listas completas a Builder.corregir_expect_result, cuyo prompt espera un texto, de modo que hoy el modelo recibe representaciones con corchetes y comillas.

Tarea sugerida
Sanear batches de expected results y ajustar el prompt

Iniciar tarea
La configuración ignora la variable HU_CODE descrita en el README y fija el prefijo a USRNM, lo que impide adaptar el sistema a diferentes nomenclaturas sin tocar código.

Tarea sugerida
Leer HU_CODE desde configuración

Iniciar tarea
El fichero requirements.txt está poblado con paquetes de entornos Conda específicos (file:///croot/...), muchos sin relación con el proyecto, lo que dificulta replicar el entorno con pip y aumenta el riesgo de vulnerabilidades no controladas.

Tarea sugerida
Depurar y normalizar requirements.txt

Iniciar tarea
Funcionalidades pendientes
Quedan por abordar las iniciativas del roadmap (API web, soporte DOCX/PDF, base de datos, integraciones con herramientas de gestión, internacionalización, etc.), que todavía no tienen implementación en el código actual.

El planner ya prioriza sprints futuros (CI/CD con linting, logging estructurado, fallback de proveedor LLM, API mínima) y puede servir como guía para ampliar capacidades una vez estabilizados los bugs inmediatos.

Prioridades recomendadas
Corregir el flujo de expected results (doble llamada y sanitización de batches), porque impacta directamente en costes y calidad del texto devuelto por el LLM.

Ajustar la configuración (HU_CODE) para respetar parámetros de entorno y permitir escalar a distintos proyectos sin tocar código.

Limpiar requirements.txt para garantizar instalaciones reproducibles y seguras.

Una vez estabilizado lo anterior, retomar las tareas de observabilidad y resiliencia del planner (CI/CD, logging estructurado, fallback de proveedor) antes de atacar nuevas funcionalidades como la API.

