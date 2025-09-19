
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

### Issue 2: CI/CD con GitHub Actions (ruff + pytest + coverage) [ HECHO]

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


