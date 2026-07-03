import os
import uuid
import csv
import json
import io
import logging
from pathlib import Path
from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response

from models import GenerateReportRequest


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn.error")
UPLOAD_DIR = Path(__file__).parent / "storage" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="AI Report Studio API")
api_router = APIRouter(prefix="/api")

MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".csv", ".json"}


def sanitize_filename(filename: str) -> str:
    name = "".join(c if c.isalnum() or c in (
        ".", "-", "_") else "_" for c in filename)
    return name or "upload"


def detect_columns_and_preview(content: bytes, filename: str):
    text = content.decode("utf-8-sig")

    if filename.endswith(".csv"):
        reader = csv.DictReader(io.StringIO(text))
        columns = reader.fieldnames or []
        preview = []
        for i, row in enumerate(reader):
            if i >= 5:
                break
            preview.append(row)
        return columns, preview

    elif filename.endswith(".json"):
        data = json.loads(text)
        if isinstance(data, list) and len(data) > 0:
            columns = list(data[0].keys())
            preview = data[:5]
            return columns, preview
        elif isinstance(data, dict):
            columns = list(data.keys())
            preview = [data]
            return columns, preview
        return [], []

    return [], []


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------

@api_router.get("/health")
async def health_check():
    return {"ok": True}


@api_router.post("/datasets")
async def upload_file(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, detail="Only CSV and JSON files are allowed")

    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, detail="File too large (max 10 MB)")

    dataset_id = str(uuid.uuid4())
    safe_name = sanitize_filename(file.filename or "upload")
    columns, preview = detect_columns_and_preview(content, file.filename or "")

    storage_path = UPLOAD_DIR / f"{dataset_id}_{safe_name}"
    with open(storage_path, "wb") as f:
        f.write(content)

    return {
        "id": dataset_id,
        "filename": safe_name,
        "columns": columns,
        "preview": preview,
    }

reports_store: dict[str, dict] = {}
next_report_id = 1


@api_router.post("/reports")
async def generate_report(body: GenerateReportRequest):
    global next_report_id

    # 1. Trouver le fichier uploadé
    dataset_id = body.dataset_id
    file_path = None
    for f in UPLOAD_DIR.iterdir():
        if f.is_file() and f.name.startswith(f"{dataset_id}_"):
            file_path = f
            break

    if not file_path:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # 2. Déterminer le template
    template_name = body.template
    template_path = Path(__file__).parent / "templates" / f"{template_name}.md"
    if not template_path.is_file():
        raise HTTPException(
            status_code=400, detail=f"Template '{template_name}' not found")

    # 3. Lire le fichier et le template
    with open(file_path, "rb") as f:
        content = f.read()
    template_content = template_path.read_text()

    # 4. Calculer les stats (à implémenter dans stats.py)
    from stats import compute_metrics
    metrics = compute_metrics(content, file_path.name)
    # Pour l'instant, metrics = {} si stats.py est vide

    # 5. Appeler l'IA
    from ai import ask
    prompt = f"""You are a data analyst. Generate a report using this template:

    {template_content}

    Here are the metrics:
    {metrics}

    Write the report in Markdown. Fill in the {{placeholders}} with the actual metrics.
    """
    report_content = ask(prompt)

    # 6. Sauvegarder le rapport
    report_id = str(next_report_id)
    next_report_id += 1
    reports_store[report_id] = {
        "id": report_id,
        "dataset_id": dataset_id,
        "template": template_name,
        "title": f"Report #{report_id}",
        "content": report_content,
        "status": "completed",
        "created_at": "2026-07-03",
    }

    logger.info(f"REPORT ID : {report_id}")
    return {"id": report_id}


@api_router.get("/reports")
async def list_reports():
    return [
        {
            "id": rid,
            "title": r["title"],
            "template": r["template"],
            "status": r["status"],
            "created_at": r["created_at"],
        }
        for rid, r in reports_store.items()
    ]


@api_router.get("/reports/{report_id}")
async def get_report(report_id: str):
    report = reports_store.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@api_router.delete("/reports/{report_id}")
async def delete_report(report_id: str):
    if report_id not in reports_store:
        raise HTTPException(status_code=404, detail="Report not found")
    del reports_store[report_id]
    return {"ok": True}


@api_router.get("/reports/{report_id}/export")
async def export_report(report_id: str, format: str = "markdown"):
    report = reports_store.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    content = report["content"]
    content_type = "text/markdown"
    filename = f"report_{report_id}.md"

    if format == "html":
        content = f"<html><body>{content}</body></html>"
        content_type = "text/html"
        filename = f"report_{report_id}.html"
    elif format == "pdf":
        content = f"<html><body>{content}</body></html>"
        content_type = "text/html"
        filename = f"report_{report_id}.html"

    return Response(content=content, media_type=content_type, headers={
        "Content-Disposition": f"attachment; filename={filename}",
    })


@api_router.get("/datasets/{dataset_id}")
async def get_dataset(dataset_id: str):
    for f in UPLOAD_DIR.iterdir():
        if f.is_file() and f.name.startswith(f"{dataset_id}_"):
            with open(f, "rb") as fh:
                content = fh.read()
            columns, preview = detect_columns_and_preview(content, f.name)
            original = f.name[len(dataset_id) + 1:]
            return {
                "id": dataset_id,
                "filename": original,
                "columns": columns,
                "preview": preview,
            }

    raise HTTPException(status_code=404, detail="Dataset not found")


app.include_router(api_router)


# ---------------------------------------------------------------------------
# Health root endpoint — simple JSON, no UI
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    return {"service": "AI Report Studio API", "status": "running", "docs": "/docs"}
