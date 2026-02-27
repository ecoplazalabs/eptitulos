# Sprint 1: Fundacion

**Objetivo:** Proyecto configurado, backend API funcional con todos los endpoints, schema en Supabase listo.
**Duracion estimada:** Dias 1-3

## Tareas

| # | Tarea | Tipo | Agente | Estado |
|---|-------|------|--------|--------|
| 1.1 | Inicializar frontend: Vite + React + TS + Tailwind v4 + pnpm | setup | frontend-dev | PENDIENTE |
| 1.2 | Inicializar backend: FastAPI + estructura de carpetas + pyproject.toml | setup | backend-dev | PENDIENTE |
| 1.3 | Configurar linters y testing: ESLint, Ruff, Vitest, pytest | setup | PM | PENDIENTE |
| 1.4 | Crear schema en Supabase: tabla + indices + RLS + bucket Storage | infra | backend-dev | PENDIENTE |
| 1.5 | Implementar config.py (pydantic-settings) | backend | backend-dev | PENDIENTE |
| 1.6 | Implementar supabase_client.py (singleton) | backend | backend-dev | PENDIENTE |
| 1.7 | Implementar analysis_repository.py (CRUD sunarp_analyses) | backend | backend-dev | PENDIENTE |
| 1.8 | Implementar analysis_service.py (logica de negocio) | backend | backend-dev | PENDIENTE |
| 1.9 | Implementar n8n_client.py (webhook call con API key) | backend | backend-dev | PENDIENTE |
| 1.10 | Implementar routers: analyze, analyses, analyses/{id}, pdf-url | backend | backend-dev | PENDIENTE |
| 1.11 | Implementar auth middleware (verificar JWT Supabase) | backend | backend-dev | PENDIENTE |
| 1.12 | Implementar health endpoint | backend | backend-dev | PENDIENTE |
| 1.13 | Implementar error_handler middleware | backend | backend-dev | PENDIENTE |
| 1.14 | Tests unitarios del backend (service + repository mocks) | test | qa-engineer | PENDIENTE |
| 1.15 | Crear .env.example para frontend y backend + .gitignore | docs | PM | PENDIENTE |

## Criterios de completitud
- [ ] `cd backend && uvicorn app.main:app --reload` levanta sin errores
- [ ] Todos los endpoints responden correctamente (probados con curl/httpx)
- [ ] Auth middleware verifica JWT y rechaza requests sin token
- [ ] Schema SQL ejecutado en Supabase sin errores
- [ ] Tests del backend pasan al 80%+ cobertura
- [ ] Frontend scaffolding listo (Vite + React + Tailwind funcionando)

## Dependencias
- Tarea 1.4 (schema Supabase) necesita credenciales de Supabase del usuario
- Tareas 1.7-1.10 dependen de 1.5 y 1.6
- Tarea 1.14 depende de 1.7-1.13
