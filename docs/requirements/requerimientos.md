# REQ-007: Analista SUNARP Automatizado

**Solicitante:** CTO - Alonso
**Responsable:** CTO Office
**Fecha:** 24 de febrero de 2026
**Prioridad:** ALTA
**Estado:** Borrador - Arquitectura diseñada, Sprint 1 pendiente
**Desarrollo:** Equipo AI (Claude + agentes) - Sesion separada de Claude Code

---

## 1. IDEA / NECESIDAD

> "Necesito automatizar la generacion de copias literales de partidas de SUNARP. Un analista
> humano tiene que entrar a dos portales web, navegar decenas de pantallas, descargar PDFs
> uno por uno, unirlos, y leer todo para identificar hipotecas y embargos. Eso lo puede
> hacer un agente IA automaticamente."

**Problema actual:**
- Proceso manual, repetitivo, propenso a errores
- Un analista tarda 30-60+ minutos por partida
- EcoPlaza necesita analizar partidas constantemente para sus operaciones inmobiliarias

**Solucion:** Un agente IA que toma un numero de partida, navega los portales de SUNARP automaticamente, descarga todos los documentos, los unifica en un solo PDF, y analiza cargas/gravamenes vigentes.

---

## 2. QUE ES EL ANALISTA SUNARP

Un sistema automatizado que:

1. **Hace login** en el extranet de SUNARP (resolviendo CAPTCHA con OCR)
2. **Busca** una partida por numero en la oficina registral indicada
3. **Extrae** todos los asientos (titulos) que componen la partida
4. **Descarga** cada asiento como PDF desde el portal SigueloPlus
5. **Unifica** todos los PDFs en una sola copia literal
6. **Analiza** el texto para identificar cargas y gravamenes vigentes
7. **Genera informe** con el resultado

### 2.1 INPUT
- Oficina registral (ej: Lima, Arequipa)
- Numero de partida
- Opcionalmente: area registral (default: "Propiedad Inmueble Predial")

### 2.2 OUTPUT
```
output/{numero_partida}/
├── asientos/              ← PDFs individuales descargados
│   ├── 2015-00001.pdf
│   ├── 2018-00042.pdf
│   └── ...
├── copia_literal.pdf      ← Documento unificado (la copia literal completa)
└── informe.txt            ← Analisis de cargas/gravamenes vigentes
```

---

## 3. COMO FUNCIONA: WEB → n8n → VPS → RESULTADO

### 3.1 Arquitectura

```
AWS                          Railway                              Supabase
├── Frontend (web app)       ├── n8n (orquestador)                ├── BD (PostgreSQL)
├── Backend Python           ├── sunarp-agent (Claude Code + PW)  ├── Storage (PDFs)
│                            │   (sin IP publica, red interna)    │
│   Backend llama a n8n ────→│   n8n llama al agente ────────────→│   Resultado se guarda
│                            │                                    │
│   Frontend consulta ──────────────────────────────────────────→│   Frontend lee resultado
```

- **El VPS (sunarp-agent) NO tiene IP publica.** Solo n8n le habla por red interna de Railway.
- **n8n es el unico punto de entrada.** El backend Python en AWS llama al webhook de n8n.
- **Los resultados van a Supabase.** El frontend los lee de ahi, no del VPS.

### 3.2 Flujo completo paso a paso

```
1. USUARIO: Click "Analizar partida 12345678 - Lima"
       │
       v
2. FRONTEND (AWS): POST /api/sunarp/analyze {oficina, partida}
       │
       v
3. BACKEND PYTHON (AWS):
       - Crea registro en Supabase: {id: "abc-123", status: "pending"}
       - Llama a n8n: POST https://tu-n8n.railway.app/webhook/sunarp-analyze
         Body: {analysis_id: "abc-123", oficina: "Lima", partida: "12345678"}
       - Responde al frontend: {analysis_id: "abc-123", status: "pending"}
       │
       v
4. n8n (Railway) recibe webhook:
       - Verifica que la peticion viene del backend (API key)
       - Actualiza Supabase: status = "processing"
       - Ejecuta comando en el servicio sunarp-agent (red interna Railway):
         claude -p "Analiza partida 12345678 de Lima..." --allowedTools "..."
       │
       v
5. CLAUDE CODE (sunarp-agent, Railway):
       - Abre Playwright, navega SUNARP
       - Login con CAPTCHA OCR
       - Busca partida, extrae titulos
       - Descarga PDFs de SigueloPlus
       - Unifica PDFs
       - Analiza cargas/gravamenes
       - Sube PDF a Supabase Storage
       - Retorna resultado JSON
       │
       v
6. n8n recibe resultado de Claude Code:
       - Actualiza Supabase: status = "completed", pdf_url, informe, cargas
       - (Opcional: notifica por WhatsApp al usuario)
       │
       v
7. FRONTEND (AWS):
       - Hace polling a Supabase cada 5 seg: GET sunarp_analyses where id = "abc-123"
       - Cuando status = "completed" → muestra resultado + boton descargar PDF
```

### 3.3 Progreso en tiempo real

El frontend consulta Supabase periodicamente (polling cada 5 segundos):

```
┌──────────────────────────────────────────────────────┐
│  Analisis de Partida #12345678 - Oficina Lima        │
│                                                      │
│  ✅ Solicitud recibida                               │
│  ✅ Procesando en SUNARP...                          │
│  🔄 En progreso (2:30 transcurridos)                │
│                                                      │
│  Tiempo estimado: 3-8 minutos                        │
│  (Depende de cuantos asientos tenga la partida)      │
└──────────────────────────────────────────────────────┘
```

Cuando termina:

```
┌──────────────────────────────────────────────────────┐
│  Analisis de Partida #12345678 - Oficina Lima     ✅ │
│                                                      │
│  Completado en 4:23                                  │
│  23 asientos procesados                              │
│                                                      │
│  📄 [Descargar Copia Literal (PDF)]                  │
│                                                      │
│  ─── Cargas y Gravamenes ───                         │
│  🔴 Hipoteca vigente - Banco de Credito (2019)       │
│  ✅ Embargo CANCELADO (2021)                         │
│  🔴 Servidumbre de paso vigente                      │
│                                                      │
│  2 cargas vigentes | 1 cancelada                     │
└──────────────────────────────────────────────────────┘
```

**Opcion avanzada (futuro):** Si se quiere progreso mas granular ("Descargando 18/23"), n8n puede usar Supabase Realtime para actualizar un campo `progress_detail` en la BD que el frontend escucha via suscripcion Realtime.

### 3.4 Componentes tecnicos

| Componente | Donde | Que hace | Expuesto a internet? |
|------------|-------|---------|---------------------|
| **Frontend** | AWS | Formulario + progress + resultados | Si |
| **Backend Python** | AWS | Valida peticion, crea registro en BD, llama a n8n | Si (API) |
| **n8n** | Railway | Orquesta: recibe webhook, ejecuta Claude Code, actualiza BD | Si (solo webhook URL) |
| **sunarp-agent** | Railway (servicio interno) | Claude Code + Playwright + proyecto SUNARP | **No** |
| **Supabase BD** | Supabase | Tabla sunarp_analyses (estado, resultado) | Si (via API auth) |
| **Supabase Storage** | Supabase | PDFs generados (bucket privado, signed URLs) | Si (URLs temporales) |

### 3.5 Workflow de n8n

```
[Webhook Trigger]
  → Recibe {analysis_id, oficina, partida} del backend Python
  → Valida API key

[Supabase Node]
  → UPDATE sunarp_analyses SET status = 'processing' WHERE id = analysis_id

[Execute Command / SSH Node]
  → Conecta al servicio sunarp-agent (red interna Railway)
  → Ejecuta:
    cd /home/ecoplaza/analista-sunarp && \
    claude -p "Analiza partida ${partida} de ${oficina}.
               Sigue CLAUDE.md. Retorna JSON con resultado." \
      --allowedTools "Read,Bash,Glob,Grep,mcp__playwright__*" \
      --output-format json \
      --max-turns 50 \
      --max-budget-usd 1.00
  → Captura stdout (resultado JSON)

[IF: exito?]
  → SI:
    [Supabase Node] UPDATE sunarp_analyses SET
      status = 'completed',
      pdf_url = resultado.pdf_url,
      informe = resultado.informe,
      cargas_encontradas = resultado.cargas,
      completed_at = NOW()

  → NO:
    [Supabase Node] UPDATE sunarp_analyses SET
      status = 'failed',
      error_message = error.message

[Fin del workflow]
```

### 3.6 Cola de procesamiento (n8n nativo)

Si llegan multiples peticiones simultaneas, n8n las maneja con su cola built-in:

- **Configuracion:** En el nodo Execute Command, setear `concurrency = 1` (procesa una a la vez)
- n8n encola automaticamente las demas
- Cada peticion espera su turno

Para escalar a procesamiento paralelo (futuro):
- Cambiar `concurrency = 2` o `concurrency = 3` en n8n
- Tener multiples replicas del servicio sunarp-agent en Railway
- Cada replica tiene su propio Claude Code + Playwright (contextos aislados, no se bloquean)

### 3.7 Schema BD (Supabase)

```sql
sunarp_analyses:
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid()
  requested_by      UUID REFERENCES users        -- Quien lo pidio
  oficina           TEXT NOT NULL                 -- "Lima", "Arequipa", etc.
  partida           TEXT NOT NULL                 -- Numero de partida
  area_registral    TEXT DEFAULT 'Propiedad Inmueble Predial'
  status            TEXT DEFAULT 'pending'        -- pending/processing/completed/failed
  total_asientos    INTEGER                       -- Cuantos asientos tiene la partida
  pdf_url           TEXT                          -- URL en Supabase Storage
  informe           TEXT                          -- Resultado del analisis de cargas
  cargas_encontradas JSONB DEFAULT '[]'           -- [{tipo: "Hipoteca", detalle: "...", vigente: true}]
  error_message     TEXT                          -- Si fallo, por que
  started_at        TIMESTAMPTZ
  completed_at      TIMESTAMPTZ
  duration_seconds  INTEGER
  claude_cost_usd   DECIMAL(6,4)                 -- Costo API de esta ejecucion
  created_at        TIMESTAMPTZ DEFAULT now()
```

---

## 4. PROCESO COMPLETO

### Fase 1: Login en Extranet SUNARP
1. Navegar a `https://sprl.sunarp.gob.pe/sprl/ingreso`
2. Ingresar usuario y contrasena (almacenados en .env, nunca hardcodeados)
3. La pagina muestra un CAPTCHA (imagen con texto distorsionado)
4. Capturar imagen del CAPTCHA
5. Procesar con Sharp (escala de grises → aumento de contraste → binarizacion → escala 2x)
6. Pasar por Tesseract.js (OCR) para extraer el texto
7. Escribir el texto del CAPTCHA en el campo y hacer login
8. Si falla (CAPTCHA mal leido), reintentar con backoff exponencial (hasta 3 veces)

### Fase 2: Busqueda de partida en Extranet
9. Seleccionar oficina registral (ej: Lima, Arequipa)
10. Seleccionar area registral = "Propiedad Inmueble Predial"
11. Seleccionar busqueda por Partida
12. Escribir numero de partida
13. Resolver otro CAPTCHA (mismo proceso OCR)
14. Click en Buscar
15. Click en icono de lupa (visualizar) en el recuadro de confirmacion
16. Se abre nueva ventana con todos los asientos de la partida

### Fase 3: Extraccion de titulos
17. Leer la lista de asientos del panel izquierdo
18. Empezar desde el asiento mas antiguo (abajo) hasta el mas reciente (arriba)
19. De cada asiento extraer "Titulo: 20XX-XXXXX" (ano y numero)
20. Generar lista ordenada de todos los titulos a descargar

### Fase 4: Descarga desde SigueloPlus
21. Para cada titulo de la lista:
    - Navegar a `https://sigueloplus.sunarp.gob.pe/siguelo/`
    - Seleccionar la misma oficina registral
    - Ingresar ano y numero del titulo
    - Click en Buscar
    - En resultado, bajar al panel "Detalle del seguimiento" (inferior derecha)
    - Buscar seccion "Asiento de inscripcion"
    - Click en icono del ojo → descarga el PDF del asiento
    - Guardar en `output/{numero_partida}/asientos/`
22. Repetir para todos los titulos

### Fase 5: Unificacion de PDFs
23. Tomar todos los PDFs descargados en orden cronologico
24. Unificar con pdf-merger-js en un solo archivo: `output/{numero_partida}/copia_literal.pdf`

### Fase 6: Analisis de cargas y gravamenes
25. Extraer texto de la copia literal con pdf-parse
26. Buscar patrones de cargas/gravamenes vigentes:
    - Hipoteca
    - Embargo
    - Anticresis
    - Usufructo
    - Servidumbre
    - Demanda
    - Carga tecnica
    - Bloqueo
    - Cancelacion (puede indicar que una carga fue levantada)
27. Generar informe: `output/{numero_partida}/informe.txt`

---

## 5. STACK TECNOLOGICO

| Componente | Tecnologia | Para que |
|------------|-----------|---------|
| Runtime | Node.js v22 LTS | Motor principal |
| Navegacion web | Playwright MCP | Controlar browser automaticamente |
| OCR (CAPTCHA) | Tesseract.js v5 (WASM) | Leer texto de imagenes CAPTCHA |
| Pre-procesamiento imagen | Sharp | Mejorar imagen antes del OCR |
| Union de PDFs | pdf-merger-js | Crear la copia literal |
| Extraccion de texto | pdf-parse | Leer contenido de PDFs para analisis |
| Logging | Winston | Registro de operaciones y errores |
| Reintentos | p-retry | Backoff exponencial ante fallos |
| Config | dotenv | Variables de entorno |
| **Orquestador** | **n8n** | **Recibe webhooks, ejecuta Claude Code, maneja cola** |
| **Storage** | **Supabase Storage** | **Almacenar PDFs generados (bucket privado)** |
| **BD** | **Supabase (PostgreSQL)** | **Registrar cada analisis (historial)** |
| **Web App** | **Python (backend) + frontend** | **Interfaz de usuario en AWS (proyecto separado)** |

---

## 6. INFRAESTRUCTURA: RAILWAY (MISMO PROYECTO QUE n8n)

### 6.1 Mapa completo de infraestructura

```
AWS                                Railway                            Supabase
├── SUNARP Web App (NUEVA)         ├── Servicio: n8n (ya existe)      ├── BD PostgreSQL
│   ├── Frontend                   ├── Servicio: sunarp-agent (NEW)   ├── Storage (PDFs)
│   └── Backend Python             │   ├── Claude Code                │
│   (proyecto separado,            │   ├── Playwright + Chromium      │
│    NO es Command Center)         │   ├── Proyecto SUNARP (GitHub)   │
│                                  │   └── Sin dominio publico        │
│                                  │                                  │
│                                  └── Red interna Railway            │
│                                      (n8n ↔ sunarp-agent)           │
```

**IMPORTANTE:** La SUNARP Web App es un proyecto APARTE del Command Center.
Son aplicaciones diferentes con repos diferentes.

### 6.2 Servicio sunarp-agent en Railway

Es un **servicio Docker** dentro del mismo proyecto Railway donde esta n8n. Railway maneja el container.

```dockerfile
# Dockerfile del servicio sunarp-agent
FROM node:22-bookworm

# Playwright + Chromium
RUN npx playwright install --with-deps chromium

# Claude Code
RUN npm install -g @anthropic-ai/claude-code

# OCR para CAPTCHA
RUN apt-get install -y tesseract-ocr

# Proyecto SUNARP (se clona del repo)
WORKDIR /home/ecoplaza/analista-sunarp
COPY . .
RUN npm install

# Variables de entorno (se configuran en Railway dashboard):
# ANTHROPIC_API_KEY, SUNARP_EXTRANET_USER, SUNARP_EXTRANET_PASS
```

**Variables de entorno** (se configuran en Railway, nunca en el codigo):
- `ANTHROPIC_API_KEY` - Para Claude Code
- `SUNARP_EXTRANET_USER` - Login SUNARP
- `SUNARP_EXTRANET_PASS` - Password SUNARP
- `SUPABASE_URL` - Para subir PDFs
- `SUPABASE_SERVICE_ROLE_KEY` - Acceso a Storage + BD

### 6.3 Comunicacion interna Railway

n8n y sunarp-agent estan en el mismo proyecto Railway. Se hablan por red interna:

```
n8n accede al agente como: http://sunarp-agent.railway.internal:3001
Esto NO sale a internet. Es red privada de Railway.
```

### 6.4 Specs del servicio

| Spec | Valor | Nota |
|------|-------|------|
| RAM | 4-8 GB | Playwright + PDFs pesados |
| CPU | 2 vCPU | Suficiente |
| Disco | Railway maneja | PDFs temporales, se suben a Supabase y se borran |
| Replicas | 1 (inicio), 2-3 (escala) | Railway escala con un click |

### 6.3 Secrets de SUNARP

Van encriptados en el repo via git-crypt (mismo mecanismo que REQ-006):

```
# En .env (encriptado en GitHub, visible en PC y VPS):
SUNARP_EXTRANET_USER=usuario_sunarp
SUNARP_EXTRANET_PASS=password_sunarp
```

### 6.4 Almacenamiento de PDFs

Los PDFs se generan en el VPS temporalmente y se suben a **Supabase Storage** (bucket privado) para que el frontend web los sirva al usuario.

```
VPS genera PDF → sube a Supabase Storage → guarda URL en BD → frontend muestra link de descarga
```

- **Bucket:** `sunarp-documents` (privado, acceso via signed URLs con expiracion)
- **Estructura:** `{user_id}/{partida}/{timestamp}/copia_literal.pdf`
- **Limpieza:** PDFs temporales en el VPS se borran despues de subir a Storage
- **Signed URLs:** El frontend genera URLs temporales (1 hora) para descarga, no expone URLs permanentes

---

## 7. ESTADO ACTUAL DEL PROYECTO

| Aspecto | Estado |
|---------|--------|
| Arquitectura | Disenada y documentada ✅ |
| Decisiones tecnicas | 10 decisiones tomadas ✅ |
| Reglas de codigo/testing/seguridad | Definidas ✅ |
| Codigo | **No implementado** - Sprint 1 pendiente |
| Sprint 1 planificado | Setup + login + CAPTCHA (12 tareas) |

### 7.1 Riesgos identificados

| Riesgo | Impacto | Mitigacion |
|--------|---------|-----------|
| **CAPTCHA cambia** | OCR deja de funcionar | Monitorear tasa de exito, tener fallback (CAPTCHA solving service externo) |
| **SUNARP cambia la UI** | Selectores de Playwright se rompen | Tests de humo diarios, alertas si falla |
| **Rate limiting de SUNARP** | Bloquean la IP | Delays entre requests, respetar tiempos, no abusar |
| **Sesion expira a mitad de proceso** | Descarga incompleta | Checkpoint system: guardar progreso, retomar desde donde quedo |
| **PDFs corruptos** | Copia literal incompleta | Validacion post-descarga de cada PDF |

---

## 8. SESIONES DE CLAUDE CODE Y RESPONSABILIDADES

2 sesiones de Claude Code. El CTO solo da credenciales.

```
┌──────────────────────────────────────────────────────────────────┐
│                  CTO (Alonso) - Orquesta todo                    │
│            Da credenciales, aprueba, no toca codigo              │
├─────────────────────────┬────────────────────────────────────────┤
│                         │                                        │
│  SESION 1               │  SESION 2                              │
│  "Analista SUNARP"      │  "SUNARP Web + Infra"                  │
│  (ya existe, APARTE)    │  (nueva, hace todo lo demas)           │
│                         │                                        │
│  Construye el motor:    │  Construye:                            │
│  - Login SUNARP         │  - Web app (frontend + backend Python) │
│  - CAPTCHA OCR          │  - Tabla + bucket en Supabase          │
│  - Busqueda partida     │  - Deploy a AWS                        │
│  - Descarga PDFs        │                                        │
│  - Unificacion          │  Configura infraestructura:            │
│  - Analisis gravamenes  │  - Workflow en n8n (via API/Playwright)│
│  - Dockerfile Railway   │  - Servicio sunarp-agent en Railway    │
│                         │  - Variables de entorno en Railway     │
│  Repo: GitHub           │  - Conexion n8n ↔ sunarp-agent        │
│  Deploy: Railway        │  - Cola de procesamiento               │
│  (via Dockerfile)       │                                        │
│                         │  Repo: GitHub                          │
│                         │  Deploy: AWS (web) + Railway (infra)   │
└─────────────────────────┴────────────────────────────────────────┘
```

### Sesion 1: Analista SUNARP Core (ya existe, aparte)
**Que hace:** Construye el motor que navega SUNARP, descarga documentos, y genera el analisis.
**Que entrega:** Un proyecto Node.js con Dockerfile que puede correr en Railway como servicio.
**No toca:** Ni la web, ni n8n, ni Railway config. Solo el core.
**El CTO le dice:** "Completa el core y agrega un Dockerfile para Railway."

### Sesion 2: SUNARP Web + Infra (nueva, hace todo lo demas)
**Que hace:** Construye la app web Y configura toda la infraestructura (n8n, Railway, Supabase).
**Por que una sola sesion:** Necesita ver el panorama completo para que web, n8n, y Railway encajen.

**Lo que construye:**
- App web: frontend + backend Python → deploy a AWS
- Tabla `sunarp_analyses` + bucket `sunarp-documents` en Supabase
- Formulario, polling, resultados, historial, permisos

**Lo que configura (con credenciales del CTO):**
- Workflow en n8n (via API REST de n8n o Playwright MCP navegando el dashboard)
- Servicio sunarp-agent en Railway (desde el repo GitHub de la Sesion 1)
- Variables de entorno en Railway (ANTHROPIC_API_KEY, SUNARP creds, Supabase creds)
- Cola de procesamiento en n8n (concurrency=1)
- Conexion interna Railway entre n8n y sunarp-agent

**Credenciales que el CTO proporciona a esta sesion:**
```
# n8n (para crear el workflow)
N8N_URL=https://tu-n8n.railway.app
N8N_USER=admin
N8N_PASS=xxxxx

# Railway (para crear servicio y configurar variables)
RAILWAY_TOKEN=xxxxx

# Anthropic (para que Claude Code funcione en Railway - se paga por uso, no suscripcion)
ANTHROPIC_API_KEY=sk-ant-xxxxx

# SUNARP (para configurar como variable en Railway)
SUNARP_EXTRANET_USER=xxxxx
SUNARP_EXTRANET_PASS=xxxxx

# Supabase (para crear tabla/bucket y configurar en Railway)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJxxxxx

# AWS (para deploy de la web app)
AWS_ACCESS_KEY_ID=xxxxx
AWS_SECRET_ACCESS_KEY=xxxxx
```

---

## 9. FASES DE DESARROLLO

> **NOTA:** El equipo de desarrollo es Claude Code (agentes IA). Tiempos para desarrollo con IA.
> El CTO solo da credenciales y aprueba. No toca codigo ni configura nada manualmente.

### Sprint 1: Core SUNARP - Login + Busqueda + Extraccion (Dias 1-3)
*Sesion 1: SUNARP Core*
- Setup del proyecto Node.js (ya en progreso)
- Configuracion de Playwright
- Login automatico en extranet SUNARP con CAPTCHA OCR (Sharp + Tesseract.js)
- Busqueda de partida por numero
- Extraccion de lista de titulos
- Manejo de reintentos con backoff
- **Entregable:** Dado un numero de partida, obtener login + lista completa de titulos

### Sprint 2: Descarga + Unificacion + Analisis + Dockerfile (Dias 4-6)
*Sesion 1: SUNARP Core*
- Descarga de PDFs desde SigueloPlus por cada titulo
- Almacenamiento organizado
- Merge de PDFs en copia literal (pdf-merger-js)
- Extraccion de texto (pdf-parse)
- Analisis de cargas y gravamenes
- Generacion de informe
- Crear Dockerfile para Railway (Node.js + Playwright + Chromium + Tesseract + Claude Code)
- Push a GitHub
- **Entregable:** Proceso completo end-to-end + Dockerfile listo para deploy

### Sprint 3: Infraestructura n8n + Railway (Dias 7-9)
*Sesion 2: SUNARP Web + Infra*
- CTO proporciona credenciales (n8n, Railway, Anthropic, SUNARP, Supabase)
- Crear servicio sunarp-agent en Railway desde el repo de GitHub
- Configurar variables de entorno en Railway
- Crear workflow en n8n:
  - Nodo webhook (recibe peticiones del backend)
  - Nodo Supabase (actualiza status a "processing")
  - Nodo Execute Command (ejecuta claude -p en el servicio Railway)
  - Nodo Supabase (guarda resultado: status completed, pdf_url, informe)
- Configurar cola: concurrency=1
- Probar flujo completo: webhook → Claude Code procesa → resultado en Supabase
- **Entregable:** Infraestructura completa funcionando, lista para recibir peticiones

### Sprint 4: Web App frontend + backend (Dias 10-12)
*Sesion 2: SUNARP Web + Infra (misma sesion que Sprint 3)*
- Crear proyecto web (frontend + backend Python)
- Tabla `sunarp_analyses` en Supabase + bucket Storage `sunarp-documents`
- Backend: endpoint POST /api/sunarp/analyze → llama webhook n8n → retorna analysis_id
- Backend: endpoint GET /api/sunarp/analyses → historial de Supabase
- Frontend: pagina con formulario (oficina registral + partida)
- Frontend: polling a Supabase cada 5 seg hasta status=completed
- Frontend: vista de resultado (descargar PDF + informe de cargas formateado)
- Frontend: historial de analisis realizados
- Permisos: solo usuarios autorizados
- Deploy a AWS
- **Entregable:** App web funcional donde usuario solicita y ve analisis

### Sprint 5: Hardening + UX (Dias 13-14)
*Ambas sesiones*
- Manejo robusto de errores (CAPTCHA fallido, SUNARP caida, timeout)
- Reintentos automaticos en n8n con notificacion al usuario
- Limpieza automatica de PDFs temporales en el servicio Railway
- Metricas: tasa de exito, tiempo promedio, costo por analisis
- **Entregable:** Producto robusto y listo para produccion

**Tiempo total estimado: 12-14 dias de desarrollo con IA**
**Trabajo manual del CTO: proporcionar credenciales (~10 minutos)**

### Escalamiento futuro (cuando se necesite paralelismo)

| Nivel | Que cambiar | Quien lo hace |
|-------|------------|--------------|
| 1→2 analisis simultaneos | Concurrency=2 en n8n | Sesion 2 (n8n config) |
| 2→5 analisis simultaneos | Replicas=3 en Railway | Sesion 2 (Railway config) |
| 5+ con cuentas SUNARP distintas | Agregar cuentas SUNARP como variables | CTO da credenciales adicionales |

---

## 10. COSTOS (CORREGIDOS - incluye modelo IA real)

> **IMPORTANTE:** Claude Code en Railway usa la API de Anthropic (se paga por tokens consumidos).
> El proceso SUNARP usa Playwright MCP que consume muchos tokens por las capturas de pantalla
> (snapshots) de cada pagina web. Esto hace que el costo por partida sea mayor a lo esperado.

### Precios API Anthropic (verificados febrero 2026)

| Modelo | Input | Output |
|--------|-------|--------|
| Opus 4.6 | $5/MTok | $25/MTok |
| Sonnet 4.6 (recomendado) | $3/MTok | $15/MTok |
| Haiku 4.5 | $1/MTok | $5/MTok |

### Costo por partida segun modelo

| Modelo | Costo/partida (20 asientos) | Para que usarlo |
|--------|---------------------------|-----------------|
| **Sonnet 4.6 (recomendado)** | **~$3-6** | Navegacion web + analisis. Suficiente para Playwright. |
| Sonnet + Haiku mix | ~$2-3.50 | Haiku para explorar, Sonnet para ejecutar. |
| Opus 4.6 | ~$8-13 | Innecesario para navegacion web. Solo para analisis complejos. |

**Modelo recomendado:** `--model sonnet` para todo el proceso. Opus no justifica el sobrecosto para navegacion web mecanica.

### Costo mensual total

| Concepto | 10 partidas/mes | 50 partidas/mes | 100 partidas/mes |
|----------|----------------|-----------------|------------------|
| Claude API (Sonnet) | $30-60 | $150-300 | $300-600 |
| Railway (sunarp-agent) | $10-25 | $10-25 | $20-40 |
| Supabase Storage | $0 | $0-5 | $5-10 |
| n8n | $0 | $0 | $0 |
| **Total** | **$40-85** | **$160-330** | **$325-650** |

### Filosofia: Siempre Playwright MCP, nunca CLI

Playwright MCP consume mas tokens (~114,000 por tarea) porque envia snapshots de la pagina en cada paso. **Esto es intencional y correcto.** El agente debe ver la pagina real y reaccionar como un humano. Los portales web cambian sin aviso (layouts, selectores, textos). Con MCP el agente se adapta. Con CLI se rompe.

**Todos los sistemas de EcoPlaza que naveguen webs externas deben usar MCP.** Es un principio de arquitectura, no una optimizacion pendiente.

**La optimizacion de costos viene de:**
- Usar Sonnet (no Opus) para navegacion web
- Limitar `--max-turns` y `--max-budget-usd` por ejecucion
- Mejorar el CLAUDE.md para que el agente sea eficiente en sus pasos
- No optimizar tokens, optimizar calidad de instrucciones

### Ahorro vs analista humano

| | Agente IA (Sonnet, MCP) | Analista humano |
|---|---|---|
| Costo/partida | ~$3-6 | $5-15 |
| Tiempo/partida | 5-8 min | 30-60+ min |
| Disponibilidad | 24/7 | Horario laboral |
| Se adapta a cambios en la web | Si (ve la pagina real) | Si |
| 50 partidas/mes | **$160-330** | **$250-750** |

**El ahorro real no es solo el dinero.** Es tiempo (6-10x mas rapido), disponibilidad (24/7), y escalabilidad (multiples partidas en paralelo).

---

## 10. VISION: RAILWAY COMO PLATAFORMA DE AGENTES IA

Con REQ-006 + REQ-007, Railway se convierte en la plataforma de agentes IA de EcoPlaza:

```
Railway - Plataforma de Agentes IA EcoPlaza
├── Servicio: n8n (orquestador central)
│   └── Recibe webhooks, distribuye trabajo, maneja colas
│
├── Servicio: soporte-agent (REQ-006)
│   └── WhatsApp → n8n → Claude Code → diagnostica/resuelve
│
├── Servicio: sunarp-agent (REQ-007)
│   └── Web → n8n → Claude Code + Playwright → copia literal + informe
│
├── [Futuro] Otros servicios-agente...
│   ├── cobranzas-agent
│   ├── leads-agent
│   └── ...
│
└── Cada agente es un servicio Docker independiente
    - Se escala con replicas
    - Sin IP publica (solo n8n les habla)
    - Variables de entorno en Railway dashboard
```

---

*REQ-007 v5.0 | 25 de febrero de 2026*
*2 sesiones de Claude Code: (1) SUNARP Core [ya existe], (2) SUNARP Web + Infra [nueva]*
*Investigacion de costos: docs/research/2026-02-25-analisis-costo-api-anthropic-agente-sunarp-playwright.md*
*Infra: AWS (web app) + Railway (n8n + sunarp-agent) + Supabase (BD + Storage)*
