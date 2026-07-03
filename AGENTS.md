# Agent Guidelines for New Projects

This project is currently empty. As development progresses, this file should be updated with project-specific guidance to help future OpenCode sessions ramp up quickly and avoid common pitfalls.

## General Operating Environment
-   **OS:** `win32`
-   **Shell:** `PowerShell 5.1`

## Command Execution
-   **Working Directory:** Always use the `workdir` parameter in `default_api.bash` to specify the execution directory. Avoid using `Set-Location` or `cd` within commands.
-   **File Operations:** Prefer dedicated tools (`read`, `write`, `edit`, `glob`, `grep`) for file system interactions over PowerShell cmdlets within `default_api.bash`.
-   **Quoting:** Always use double quotes for paths and strings that contain spaces when executing PowerShell commands.
    -   *Correct:* `& "path with spaces\script.ps1"`
    -   *Incorrect:* `path with spaces\script.ps1`
-   **Chained Commands:** For sequential commands where success of one depends on the previous, use PowerShell conditionals: `command1; if ($?) { command2 }`. Do not use `&&`.

## Project-Specific Information

### 1. Overall Objective
Create a full-stack web app:
-   Upload CSV/JSON.
-   Generate AI narrative report (Python computes facts, AI writes prose).
-   View & export report (Markdown/HTML/PDF).
-   **Core Principle:** Python computes facts (stats.py), AI writes prose (ai.py + Gemini). AI never does arithmetic.

### 2. Technical Architecture
-   **Backend:** FastAPI (Python), Supabase (Storage), Neon (PostgreSQL).
    -   **Directory:** `backend/` (main.py, models.py, supabase_client.py, neon_client.py, stats.py, ai.py, config.py, storage/, templates/, tests/).
    -   **DB Schema:** `datasets`, `reports`, `report_exports` tables in Neon.
    -   **API Endpoints:**
        -   `POST /datasets`: Upload CSV/JSON.
        -   `GET /datasets/{id}`: Get columns + data preview.
        -   `GET /templates`: List report templates.
        -   `POST /reports`: Generate report.
        -   `GET /reports/{id}`: Get structured report.
        -   `GET /reports/{id}/export`: Export report.
        -   `GET /reports`: List all reports.
        -   `DELETE /reports/{id}`: Delete a report.
-   **Frontend:** Next.js (TypeScript), TailwindCSS.
    -   **Directory:** `frontend/` (app/, components/, lib/, public/, styles/, types/, package.json).
    -   **Pages:** Home (`/`), Report (`/report/[id]`), History (`/history`).

### 3. Recommended Toolchain
-   **Backend:** Python 3.12, FastAPI, psycopg2-binary, supabase-py, Pydantic, python-multipart.
-   **Frontend:** Next.js 14, TypeScript, TailwindCSS, react-dropzone, @supabase/supabase-js, @tanstack/react-query.
-   **Database:** Neon (PostgreSQL serverless) + Supabase Storage.
-   **AI:** Google AI Studio (Gemini).
-   **Export:** `markdown` (for HTML), `weasyprint` (for PDF).
-   **Testing:** `pytest` (backend), `vitest` (frontend).

### 4. Build Steps (Strict Order)
Follow the order defined in `PLAN.md` section 5. "Build Steps (Strict Order)".
-   **Phase 1: Backend (MVP)** (Scaffold, Configure Neon + Supabase, File Upload, Data Reading, Deterministic Calculations, Templates, AI Generation, Export, History).
-   **Phase 2: Frontend (MVP)** (Scaffold Next.js, Configure Supabase Frontend, Upload Page, Report Page, History Page, Global Layout, Styling).
-   **Phase 3: Finalization** (Tests & Review, Documentation, Demo).

### 5. Environment Variables
-   Store sensitive keys (NEON_DATABASE_URL, SUPABASE_URL, SUPABASE_KEY, Google AI Studio API key) in `.env` files.
-   Frontend environment variables should be prefixed with `NEXT_PUBLIC_`.

### 6. Security Constraints
-   API Keys: Store in `.env`.
-   Malicious Uploads: Validate MIME type (CSV/JSON), limit file size (10 MB).
-   Code Execution: Never execute content from uploaded files.
-   Insecure Storage: Sanitize filenames.
-   DB Access: Use restricted Neon/Supabase keys.
