# AI Report Studio

Upload CSV/JSON, generate AI narrative reports, and export them in Markdown/HTML/PDF.

**Core principle:** Python computes the facts (stats), AI writes the prose (Gemini). AI never does arithmetic.

## Tech Stack

| Layer    | Technology                                                |
| -------- | --------------------------------------------------------- |
| Backend  | Python 3.12, FastAPI, Supabase (Storage), Neon (PostgreSQL) |
| Frontend | Next.js 16, TypeScript, TailwindCSS                       |
| AI       | Google Gemini (via Google AI Studio)                      |
| Export   | Markdown, HTML, PDF                                       |

## Architecture

```
ai_report_studio/
├── backend/                  # FastAPI
│   ├── main.py               # Routes + static file serving
│   ├── models.py             # Pydantic schemas
│   ├── supabase_client.py    # Supabase Storage client
│   ├── neon_client.py        # Neon (PostgreSQL) client
│   ├── stats.py              # Deterministic calculations
│   ├── ai.py                 # Gemini abstraction
│   ├── config.py             # Environment variables
│   ├── templates/            # Markdown report templates
│   └── tests/                # pytest suite
├── frontend/                 # Next.js
│   ├── app/                  # App Router pages
│   ├── components/           # Reusable UI
│   ├── lib/                  # Utilities (Supabase, API)
│   ├── styles/               # Tailwind globals
│   └── types/                # TypeScript types
└── README.md
```

## Quick Start

### 1. Prerequisites

- Python 3.12+
- Node.js 20+
- A Neon (PostgreSQL) project
- A Supabase project
- A Google AI Studio API key

### 2. Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt

# Configure environment
copy .env.example .env    # then edit .env with your keys
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

### 4. Build & Run

```bash
# Build the frontend (required after every frontend change)
cd frontend
npx next build

# Start the backend (serves both API and frontend on port 8000)
cd backend
uvicorn main:app --reload
```

Open **http://localhost:8000** in your browser.

## API Endpoints

| Method | Endpoint                | Description            |
| ------ | ----------------------- | ---------------------- |
| GET    | `/health`               | Health check           |
| POST   | `/datasets`             | Upload CSV/JSON        |
| GET    | `/datasets/{id}`        | Dataset details        |
| GET    | `/templates`            | List report templates  |
| POST   | `/reports`              | Generate a report      |
| GET    | `/reports`              | List all reports       |
| GET    | `/reports/{id}`         | Get a report           |
| GET    | `/reports/{id}/export`  | Export a report        |
| DELETE | `/reports/{id}`         | Delete a report        |

Full docs at **http://localhost:8000/docs** (Swagger).

## Environment Variables

```env
NEON_DATABASE_URL=postgresql://...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key
GEMINI_API_KEY=your-gemini-api-key
```

## Development

```bash
# Backend (with auto-reload)
cd backend && uvicorn main:app --reload

# Frontend (standalone dev server, port 3000)
cd frontend && npm run dev

# Frontend tests
cd frontend && npx vitest

# Backend tests
cd backend && pytest
```

## Data Flow

1. User uploads CSV/JSON via the frontend
2. Backend validates and stores the file in Supabase Storage + metadata in Neon
3. `stats.py` computes deterministic metrics (totals, averages, growth, etc.)
4. `ai.py` sends metrics + a template to Gemini → returns narrative text
5. Report is saved in Neon and displayed in the frontend
6. User can export as Markdown, HTML, or PDF

## License

MIT
