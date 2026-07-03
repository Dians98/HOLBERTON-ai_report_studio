# AI Report Studio — Plan

## 1. Overall Objective

Create a full-stack web app that allows users to:

- Upload a CSV or JSON file.
- Generate a narrative report (via AI) from structured data.
- View and export the report in Markdown/HTML/PDF.

**Core Principle:** ✅ Python computes the facts (`stats.py`). ✅ AI writes the prose (`ai.py` + Gemini). ❌ AI never does arithmetic.

---

## 2. Technical Architecture

### 2.1. Backend (FastAPI — API only, no UI)

**Directory Structure**

```
backend/
├── main.py              # FastAPI routes + configuration
├── models.py            # Pydantic models (validation)
├── neon_client.py       # Neon PostgreSQL client (persistent storage)
├── supabase_client.py   # Supabase client — unused for now
├── stats.py             # Deterministic calculations (totals, averages, etc.)
├── ai.py                # Abstraction for AI API calls
├── config.py            # Environment variable loading
├── storage/
│   └── uploads/         # Local CSV/JSON files (temporary)
├── templates/           # Report templates (Markdown)
│   ├── weekly_digest.md
│   ├── executive_summary.md
│   └── incident_report.md
└── tests/               # Unit tests (pytest)
    ├── test_stats.py
    └── test_ai.py
```

**Data flow:**
- Files stored **locally** in `storage/uploads/` (no Supabase needed)
- Reports stored in **Neon PostgreSQL** (persistent across restarts)
- Backend is **API-only** — no HTML served, no static files

### 2.2. Frontend (Next.js + TypeScript)

**Directory Structure**

```
frontend/
├── app/
│   └── (main)/
│       ├── layout.tsx
│       ├── page.tsx         # Homepage (upload → template → report)
│       ├── report/
│       │   └── [id]/
│       │       └── page.tsx
│       └── history/
│           └── page.tsx
├── components/
│   ├── UploadForm.tsx
│   ├── TemplateSelector.tsx
│   ├── ReportViewer.tsx
│   └── ReportHistory.tsx
├── lib/
│   ├── api.ts              # Fetch wrapper
│   └── utils.ts
├── types/
│   └── api.d.ts
├── styles/
│   └── globals.css
└── package.json
```

**Architecture:**
- Frontend runs **independently** from backend
- In dev: Next.js proxies `/api/*` → `http://localhost:8000/api/*` (via `next.config.js`)
- In prod: deploy frontend on Vercel, backend on Render/Railway/Fly.io
- `NEXT_PUBLIC_API_URL` env var makes the proxy target configurable

---

## 3. Database Schema (Neon PostgreSQL)

```sql
-- Uploaded datasets
CREATE TABLE datasets (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,     -- Local path: storage/uploads/{id}_{filename}
    columns JSONB NOT NULL,               -- Detected columns
    created_at TIMESTAMP DEFAULT NOW()
);

-- Generated reports
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    dataset_id INTEGER REFERENCES datasets(id),
    template VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 4. API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/datasets` | Upload CSV/JSON → validate → store locally + Neon → return dataset_id |
| GET | `/datasets/{id}` | Return column names + data preview |
| POST | `/reports` | Generate report (`{"dataset_id", "template"}`) → save to Neon → report_id |
| GET | `/reports/{id}` | Return structured report from Neon |
| GET | `/reports/{id}/export` | Export as Markdown / HTML / PDF |
| GET | `/reports` | List all reports from Neon (history) |
| DELETE | `/reports/{id}` | Delete a report from Neon |

---

## 5. End-to-End Data Flow

```
User → Frontend: Upload CSV/JSON
         ↓ POST /api/datasets
Backend: Validate + save file locally (storage/uploads/)
         ↓ Save metadata to Neon (datasets table)
Backend: Return dataset_id + detected columns
         ↓
Frontend: Show preview + templates
         ↓ POST /api/reports {"dataset_id", "template"}
Backend: Read file → stats.py (compute metrics) → ai.py (generate prose)
         ↓ Save report to Neon (reports table)
Backend: Return report_id
         ↓
Frontend: Display report → User can export (MD/HTML/PDF)
```

---

## 6. Security

| Risk | Solution |
|------|----------|
| Exposed API Keys | Store keys in `.env` (ignored by Git) |
| Malicious Uploads | Validate MIME type (CSV/JSON) + limit file size (10 MB) |
| Code Execution | Never execute content from uploaded files |
| Leaked Errors | Clear user messages + server-side logging |
| Insecure Storage | Sanitize filenames |

---

## 7. Build Steps (Strict Order)

### Phase 1: Backend (MVP)

- [x] Scaffold backend (FastAPI + `/health` route)
- [x] File upload (`POST /datasets`) with validation
- [x] Data reading (`GET /datasets/{id}`) with preview
- [x] Report generation (`POST /reports`) with stats + AI
- [x] Report retrieval (`GET /reports/{id}`, `GET /reports`, `DELETE /reports/{id}`)
- [x] Export (`GET /reports/{id}/export`) as Markdown / HTML / PDF
- [x] Clean backend to API-only (remove frontend serving code)
- [x] Implement `neon_client.py` (connect to Neon, CRUD operations)
- [ ] Implement `config.py` (load environment variables)
- [ ] Update `main.py` to use Neon instead of in-memory dict
- [ ] Implement `stats.py` with real calculations + tests
- [ ] Implement `ai.py` with real AI provider + tests

### Phase 2: Frontend (MVP)

- [x] Scaffold Next.js with TailwindCSS
- [x] Configure API proxy (`NEXT_PUBLIC_API_URL`)
- [ ] Upload page with drag & drop + preview
- [ ] Template selector
- [ ] Report viewer with export buttons
- [ ] Report history page
- [ ] Global layout (sidebar, navbar)

### Phase 3: Finalization

- [ ] Write REVIEW.md (code audit)
- [ ] Write README.md (setup, usage)
- [ ] Demo recording

---

## 8. Recommended Toolchain

| Category | Tools |
|----------|-------|
| Backend | Python 3.12, FastAPI, Pydantic, psycopg2-binary, python-multipart | 
| Frontend | Next.js 14, TypeScript, TailwindCSS, react-dropzone | 
| Database | **Neon (PostgreSQL serverless)** | 
| AI | Google Gemini / DeepSeek / Mistral (configurable via .env) | 
| Export | `markdown` (for HTML), `weasyprint` (for PDF) |
| Testing | `pytest` (backend), `vitest` (frontend) |

---

## 9. Environment Variables

### Backend (`backend/.env`)

```env
# Neon (PostgreSQL)
NEON_DATABASE_URL=postgresql://user:password@ep-xxxx.us-east-2.aws.neon.tech/dbname

# AI Provider
AI_PROVIDER=deepseek
AI_API_KEY=sk-...
AI_BASE_URL=https://api.deepseek.com/v1
AI_MODEL=deepseek-chat
```

### Frontend (`frontend/.env.local`)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 10. Running the App

```powershell
# Terminal 1 — Backend
cd backend
python run_server.py

# Terminal 2 — Frontend
cd frontend
npm run dev
```

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs (Swagger): `http://localhost:8000/docs`