1. Overall Objective
Create a full-stack web app that allows users to:

Upload a CSV or JSON file.
Generate a narrative report (via AI) from structured data.
View and export the report in Markdown/HTML/PDF.
Core Principle : ✅ Python computes the facts (stats.py). ✅ AI writes the prose (ai.py + Gemini). ❌ AI never does arithmetic.

2. Technical Architecture
2.1. Backend (FastAPI + Supabase)
Directory Structure & Files
backend/
├── main.py              # FastAPI routes + configuration
├── models.py            # Pydantic models (validation)
├── supabase_client.py   # Supabase client (Storage)
├── neon_client.py       # Neon client (PostgreSQL)
├── stats.py             # Deterministic calculations (totals, averages, etc.)
├── ai.py                # Abstraction for Gemini API calls
├── config.py            # Environment variable loading
├── storage/             # Optional: local file storage for uploads
│   └── uploads/         # Temporary CSV/JSON files
├── templates/           # Report templates (Markdown)
│   ├── weekly_digest.md
│   ├── executive_summary.md
│   └── incident_report.md
└── tests/               # Unit tests (pytest)
    ├── test_stats.py
    └── test_ai.py
Cloud Services Setup
Neon (PostgreSQL serverless):
Benefits:
Serverless (no server management).
Free Tier: 3 projects, 500MB storage, 10,000 requests/month.
Scalable: Suitable for projects of all sizes.
Configuration:
Create a Neon project.
Get NEON_DATABASE_URL from Dashboard > Connection Details.
Store in .env (ignored by Git).
Supabase Storage:
Benefits:
Simple and secure file storage for uploads and exports.
Free Tier: 500MB storage, 1,000 downloads/month.
Configuration:
Create uploads and exports buckets in Supabase Storage.
Get SUPABASE_URL and SUPABASE_KEY from Settings > API.
PostgreSQL Database Schema (Neon)
-- Table for uploaded datasets
CREATE TABLE datasets (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,  -- Path to file in Supabase Storage
    columns JSONB NOT NULL,            -- Detected columns (e.g., ["date", "sales"])
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table for generated reports
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    dataset_id INTEGER REFERENCES datasets(id),
    template VARCHAR(50) NOT NULL,     -- e.g., "weekly_digest"
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,             -- Generated report (Markdown)
    status VARCHAR(20) DEFAULT 'pending', -- "pending", "completed", "failed"
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Optional: Table for exports
CREATE TABLE report_exports (
    id SERIAL PRIMARY KEY,
    report_id INTEGER REFERENCES reports(id),
    format VARCHAR(10) NOT NULL,      -- "md", "html", "pdf"
    file_path VARCHAR(255) NOT NULL,  -- Path to file in Supabase Storage
    created_at TIMESTAMP DEFAULT NOW()
);
API Endpoints
Method	Endpoint	Description	Responsible
POST	/datasets	Upload CSV/JSON → validate → store in Supabase Storage + DB → return dataset_id.	main.py + models.py
GET	/datasets/{id}	Return column names + data preview.	main.py
GET	/templates	List available report templates (e.g., weekly_digest).	main.py
POST	/reports	Generate report: {"dataset_id": str, "template": str} → report_id.	main.py + ai.py
GET	/reports/{id}	Return a structured report (title, sections, metrics).	main.py
GET	/reports/{id}/export	Export as Markdown/HTML/PDF (stored in Supabase Storage).	main.py
GET	/reports	List all reports (history).	main.py
DELETE	/reports/{id}	Delete a report (and associated exports).	main.py
2.2. Frontend (Next.js + TypeScript)
Directory Structure & Files
frontend/
├── app/                 # Next.js App Router
│   ├── (main)/          # Main layout group
│   │   ├── layout.tsx   # Global layout (navbar, footer)
│   │   ├── page.tsx     # Homepage (upload)
│   │   ├── report/
│   │   │   └── [id]/     # Dynamic report page
│   │   │       └── page.tsx
│   │   └── history/
│   │       └── page.tsx  # Report history page
│   └── api/             # Optional API routes proxy
│       └── auth/
│           └── callback/ # Auth callback page (if added)
├── components/          # Reusable UI components
│   ├── UploadForm.tsx
│   ├── TemplateSelector.tsx
│   ├── ReportViewer.tsx
│   └── ReportHistory.tsx
├── lib/                 # Utilities
│   ├── supabase.ts      # Supabase client configuration
│   └── api.ts           # API calls to backend
├── public/              # Static assets
├── styles/              # CSS (Tailwind or CSS Modules)
│   └── globals.css
├── types/               # TypeScript types
│   └── api.d.ts
└── package.json         # Project dependencies
Next.js - Configuration
Benefits:

Integrated Routing: No need for react-router-dom.
SSR/SSG: Better performance and SEO.
API Routes: Option to proxy backend calls (if needed).
Optimizations: Image, script, and font optimization.
Setup:

Use App Router (recommended for Next.js 13+).
Global Layout: app/(main)/layout.tsx for shared navbar and footer.
Dynamic Routes:
app/(main)/report/[id]/page.tsx for displaying a specific report.
app/(main)/history/page.tsx for the report history page.
Supabase - Frontend Configuration
Services Used:

Supabase Client:
Interact with PostgreSQL and Storage.
Configuration:
Install @supabase/supabase-js.
Configure in lib/supabase.ts:
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_KEY!;
export const supabase = createClient(supabaseUrl, supabaseKey);
Storage:
Upload CSV/JSON files and download MD/HTML/PDF exports.
Usage Example:
// Upload a file
const { data, error } = await supabase.storage
  .from('uploads')
  .upload(`uploads/${fileName}`, file);

// Download an export
const { data: url } = supabase.storage
  .from('exports')
  .getPublicUrl(`exports/${fileName}`);
Pages & Workflows
Page	Description	Next.js Link
Home	File upload + template selection.	/
Report	Display generated report (dynamic sections).	/report/[id]
History	List of generated reports (filters, actions).	/history
Frontend Features
Upload: Drag & drop or file input (react-dropzone). Column preview (react-table).
Template Selection: Dropdown list.
Report Viewing: Dynamic sections, export buttons (MD/HTML/PDF).
History: Table with filtering (template/date) and actions (View, Export, Delete) using react-query for caching.
3. End-to-End Data Flow
graph TD
    A[User] --> B[Frontend: Upload CSV/JSON]
    B --> C[Backend: Validate + Store in Supabase Storage]
    C --> D[Backend: Save metadata in Neon (PostgreSQL)]
    D --> E[Backend: Calculations (stats.py)]
    E --> F[Backend: Generate text (ai.py)]
    F --> G[Backend: Save report in Neon]
    G --> H[Frontend: Display report]
    H --> I[User: Export/Regenerate]
    I --> J[Backend: Store export in Supabase Storage]
    J --> K[Frontend: Download export]
Key Steps:
Upload:
Validated CSV/JSON file → stored in Supabase Storage (uploads/{dataset_id}.csv).
Metadata saved in Neon (datasets table).
Returns dataset_id to frontend.
Calculations:
stats.py extracts metrics (e.g., total_sales, avg_growth).
Mandatory Tests: Pytest to validate calculations (e.g., test_total_sales).
Generation:
ai.py sends metrics + template to Gemini → returns structured text.
Report saved in Neon (reports table).
Export:
Markdown → HTML (via markdown library) → PDF (via weasyprint).
Exported files stored in Supabase Storage (exports/{report_id}.{format}).
4. Security
Risk	Solution
Exposed API Keys	Store NEON_DATABASE_URL, SUPABASE_URL, SUPABASE_KEY in .env + .env.example.
Malicious Uploads	Validate MIME type (CSV/JSON) + limit file size (10 MB).
Code Execution	Never execute content from uploaded files.
Leaked Errors	Clear user messages (e.g., "Invalid file format") + server-side logging.
Insecure Storage	Sanitize filenames (e.g., dataset_123.csv).
DB Access	Use restricted Neon/Supabase keys.
5. Build Steps (Strict Order)
Phase 1: Backend (MVP)
Scaffold:
Create .venv + install FastAPI/uvicorn.
Add /health route → {"ok": true}.
Create .gitignore (.env, .venv/) + .env.example.
Commit: "Scaffold backend".
Configure Neon + Supabase:
Create Neon project → get NEON_DATABASE_URL.
Create Supabase project → get SUPABASE_URL + SUPABASE_KEY.
Configure neon_client.py and supabase_client.py.
Commit: "Backend: Configure Neon + Supabase".
File Upload:
POST /datasets endpoint:
Accept CSV/JSON.
Validate file, store metadata in DB + file in Supabase Storage.
Return dataset_id + detected columns.
Validation: Reject non-CSV/JSON files.
Test: Upload example file (sales.csv).
Commit: "Backend: File upload with Neon + Supabase".
Data Reading:
GET /datasets/{id} endpoint:
Return columns + first 5 rows.
Commit: "Backend: Dataset reading".
Deterministic Calculations:
Create stats.py with functions:
compute_totals(data)
compute_growth(current, previous)
get_top_n(data, n)
Tests: Pytest with known dataset (e.g., test_total_sales).
Commit: "Backend: Stats calculations".
Templates:
Create 3 Markdown files in templates/ (with placeholders).
GET /templates endpoint → list templates.
Commit: "Backend: Report templates".
AI Generation:
Create ai.py with generate_report(metrics, template) function.
POST /reports endpoint:
Call stats.py → pass to ai.py → save report to DB.
Secure Prompt: Always include provided metrics (no raw data).
Commit: "Backend: AI Report Generation".
Export:
GET /reports/{id}/export?format=md endpoint (Markdown).
Add HTML (markdown library) then PDF (weasyprint).
Storage: Exported files in Supabase Storage.
Commit: "Backend: Export Markdown/HTML/PDF with Supabase Storage".
History:
GET /reports endpoint (paginated list with filters).
DELETE /reports/{id} endpoint.
Commit: "Backend: Report history with Neon".
Phase 2: Frontend (MVP)
Scaffold Next.js:
Create project: npx create-next-app@latest frontend --typescript --tailwind --eslint.
Configure TailwindCSS.
Commit: "Frontend: Scaffold Next.js".
Configure Supabase Frontend:
Set up lib/supabase.ts with NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_KEY.
Commit: "Frontend: Configure Supabase".
Upload Page:
app/(main)/page.tsx:
Upload form (react-dropzone).
Column preview (react-table).
Template selector (dropdown).
Commit: "Frontend: Upload page".
Report Page:
app/(main)/report/[id]/page.tsx:
Display generated report (dynamic sections).
Export buttons (MD/HTML/PDF) with auto-download.
Commit: "Frontend: Report page".
History Page:
app/(main)/history/page.tsx:
Report table with filters (template/date).
Actions: "View", "Export", "Delete".
Commit: "Frontend: History page".
Global Layout:
app/(main)/layout.tsx:
Navbar with page links.
Footer.
Commit: "Frontend: Global layout".
Styling:
Apply TailwindCSS for a polished, responsive UI.
Commit: "Frontend: Styling with TailwindCSS".
Phase 3: Finalization
Tests & Review:
Write REVIEW.md (code audit by a senior engineer).
Fix critical issues.
Commit: "Review: Fixes".
Documentation:
Write README.md (setup, usage, examples).
Add PROMPTS.md (AI prompt examples).
Commit: "Docs: README + PROMPTS".
Demo:
Record a demo GIF (e.g., upload → report → export).
Commit: "Demo: GIF".
6. Recommended Toolchain
Category	Tools
Backend	Python 3.12, FastAPI, psycopg2-binary (for Neon), supabase-py, Pydantic, python-multipart
Frontend	Next.js 14, TypeScript, TailwindCSS, react-dropzone, @supabase/supabase-js, @tanstack/react-query
Database	Neon (PostgreSQL serverless) + Supabase Storage
AI	Google AI Studio (Gemini), API key in .env
Export	markdown (for HTML), weasyprint (for PDF)
Testing	pytest (backend), vitest (frontend)
7. Example Dataset & Template
Example Dataset (sales.csv)
date,product,sales,region
2026-07-01,A,1000,North
2026-07-01,B,1500,South
2026-07-02,A,1200,North
2026-07-02,B,1300,South
Example Template (weekly_digest.md)
# Weekly Digest - {{ date }}

## Sales Summary
- **Total Sales**: {{ total_sales }} (vs {{ previous_period }}: {{ growth_rate }}%)
- **Top Product**: {{ top_product }} ({{ top_product_sales }} sales)

