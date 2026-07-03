import asyncio
import os
import uuid  # Keep for temporary processing if needed
import csv
import json
import io
import logging
from pathlib import Path
from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response

from models import GenerateReportRequest
from config import NEON_DATABASE_URL
from neon_client import get_dataset, get_report, init_db, save_dataset, save_report

UPLOAD_DIR = Path(__file__).parent / "storage" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn.error")


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

    # Use a temporary UUID for local file processing before DB insertion
    # This is needed for detect_columns_and_preview if it relies on a filename structure
    temp_dataset_id_for_processing = str(uuid.uuid4())
    safe_name = sanitize_filename(file.filename or "upload")

    # Detect columns and preview using the content directly
    columns, preview = detect_columns_and_preview(content, file.filename or "")

    # Save dataset metadata to the database
    # For now, file_path is a placeholder as we are not using Supabase Storage yet.
    # In a real scenario with Supabase Storage, this would be the path in Supabase.
    dataset_id = await save_dataset(safe_name, f"{temp_dataset_id_for_processing}_{safe_name}", columns)

    if dataset_id is None:
        raise HTTPException(
            status_code=500, detail="Failed to save dataset metadata")

    storage_path = UPLOAD_DIR / f"{temp_dataset_id_for_processing}_{safe_name}"
    with open(storage_path, "wb") as f:
        f.write(content)

    return {
        "id": dataset_id,  # Return the database ID
        "filename": safe_name,
        "columns": columns,
        "preview": preview,
    }


@api_router.post("/reports")
async def generate_report(body: GenerateReportRequest):
    # 1. Get dataset info from DB using the provided dataset_id

    dataset_info = await get_dataset(body.dataset_id)

    if not dataset_info:
        raise HTTPException(status_code=404, detail="Dataset not found")

    file_path = Path(__file__).parent / "storage" / "uploads" / \
        dataset_info.get("file_path")  # Get the path from DB
    if not file_path:
        raise HTTPException(
            status_code=404, detail="Dataset file path not found")

    # 2. Determine the template
    template_name = body.template
    template_path = Path(__file__).parent / "templates" / f"{template_name}.md"
    if not template_path.is_file():
        raise HTTPException(
            status_code=400, detail=f"Template '{template_name}' not found")

    # 3. Read the file and the template
    # NOTE: In this MVP, we are reading the file from the local storage path.
    # If Supabase Storage were integrated, this would involve downloading from Supabase.
    try:
        with open(file_path, "rb") as f:
            content = f.read()
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Dataset file not found at path: {file_path}")

    template_content = template_path.read_text()

    # 4. Compute metrics (using stats.py)
    from stats import compute_metrics
    metrics = compute_metrics(content, os.path.basename(
        file_path))  # Pass filename for stats.py

    # 5. Call the AI
    from ai import ask
    prompt = f"""You are a data analyst. Generate a report using this template:

    {template_content}

    Here are the metrics:
    {metrics}

    Write the report in Markdown. Fill in the {{placeholders}} with the actual metrics.
    """
    report_content = ask(prompt)

    # 6. Save the report to the database
    report_id = await save_report(
        dataset_id=body.dataset_id,
        template=template_name,
        # More descriptive title
        title=f"Report for Dataset #{body.dataset_id}",
        content=report_content
    )

    if report_id is None:
        raise HTTPException(status_code=500, detail="Failed to save report")

    logger.info(f"Report generated and saved with ID: {report_id}")
    return {"id": report_id}


@api_router.get("/reports/{report_id}")
async def get_report_route(report_id: str):
    logger.info("tafiditra")
    try:
        report_id_int = int(report_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid report ID format")
    logger.info("mivoka")
    # Appel à la fonction get_report de ton neon_client.py
    report = await get_report(report_id_int)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Convertir les objets datetime de PostgreSQL en chaînes ISO pour le JSON
    if report.get('created_at'):
        report['created_at'] = report['created_at'].isoformat()
    if report.get('updated_at'):
        report['updated_at'] = report['updated_at'].isoformat()

    return report

app.include_router(api_router)


# ---------------------------------------------------------------------------
# Health root endpoint — simple JSON, no UI
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    return {"service": "AI Report Studio API", "status": "running", "docs": "/docs"}
