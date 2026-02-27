# EP Titulos - SUNARP Web App + Infra

## Comandos
- Frontend Dev: `cd frontend && pnpm dev`
- Frontend Build: `cd frontend && pnpm build`
- Frontend Test: `cd frontend && pnpm test`
- Frontend Lint: `cd frontend && pnpm lint`
- Backend Dev: `cd backend && uvicorn app.main:app --reload`
- Backend Test: `cd backend && pytest`
- Backend Lint: `cd backend && ruff check .`

## Stack
- Frontend: React + Vite + TypeScript (pnpm)
- Backend: Python + FastAPI
- DB: Supabase (PostgreSQL)
- Storage: Supabase Storage (PDFs)
- Orquestador: n8n (Railway)
- Agente SUNARP: Claude Code + Playwright (Railway, servicio interno)
- Deploy: AWS

## Convenciones
- Frontend: componentes funcionales, hooks, Tailwind CSS
- Backend: FastAPI con async, Pydantic para validacion, SQLAlchemy/Supabase client
- API responses: { data, error, status }
- Variables de entorno en .env (nunca hardcodear secrets)
- Polling al frontend cada 5s para status de analisis

## Contexto
- Requerimientos: docs/requirements/requerimientos.md
- Arquitectura actual: memory/architecture.md
- Decisiones: memory/decisions.md

## Agentes
Globales (disponibles via ~/.claude/agents/):
| Agente | Modelo | Cuando usar |
|--------|--------|-------------|
| architect | opus | Decisiones tecnicas, evaluacion tecnologia |
| frontend-dev | sonnet | Implementar UI, componentes, paginas |
| backend-dev | sonnet | Implementar API, DB, logica de negocio |
| infra-dev | sonnet | n8n workflows, Railway config, Supabase setup, AWS deploy |
| qa-engineer | sonnet | Tests, verificacion, cobertura |
| code-reviewer | sonnet | Review pre-merge, seguridad |

## Rules
- Globales (~/.claude/rules/): security.md, code-style.md
- Proyecto (.claude/rules/): testing.md, frontend.md, backend.md
