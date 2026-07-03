import os
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles


FRONTEND_OUT = os.path.join(os.path.dirname(__file__), "..", "frontend", "out")

app = FastAPI(title="AI Report Studio API")

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Report Studio</title>
    <style>
        body { font-family: system-ui, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6; color: #333; }
        h1 { color: #1a56db; }
        a { color: #1a56db; }
        .endpoints { background: #f3f4f6; padding: 20px; border-radius: 8px; }
        code { background: #e5e7eb; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>AI Report Studio</h1>
    <p>Transform your data into insightful narrative reports with the power of AI.</p>
    <div class="endpoints">
        <h2>API Endpoints</h2>
        <ul>
            <li><code>GET /health</code> &mdash; Health check</li>
            <li><code>POST /datasets</code> &mdash; Upload CSV/JSON</li>
            <li><code>GET /datasets/{id}</code> &mdash; Get dataset details</li>
            <li><code>GET /templates</code> &mdash; List templates</li>
            <li><code>POST /reports</code> &mdash; Generate report</li>
            <li><code>GET /reports</code> &mdash; List reports</li>
            <li><code>GET /reports/{id}</code> &mdash; Get report</li>
            <li><code>GET /reports/{id}/export</code> &mdash; Export report</li>
            <li><code>DELETE /reports/{id}</code> &mdash; Delete report</li>
        </ul>
    </div>
    <p><a href="/docs">API Documentation (Swagger)</a></p>
</body>
</html>"""


# ---------------------------------------------------------------------------
# API routes (registered first, so they take priority)
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {"ok": True}


# ---------------------------------------------------------------------------
# Serve built frontend (out/)
# ---------------------------------------------------------------------------

if os.path.isdir(FRONTEND_OUT):
    app.mount("/_next", StaticFiles(directory=os.path.join(FRONTEND_OUT, "_next")), name="next")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        candidates = [
            os.path.join(FRONTEND_OUT, full_path, "index.html"),
            os.path.join(FRONTEND_OUT, full_path),
        ]
        for path in candidates:
            normalized = os.path.normpath(path)
            if normalized.startswith(FRONTEND_OUT) and os.path.isfile(normalized):
                return FileResponse(normalized)

        # SPA fallback: serve the main index.html
        spa = os.path.join(FRONTEND_OUT, "index.html")
        if os.path.isfile(spa):
            return FileResponse(spa)

        return Response("Not Found", status_code=404)
else:
    @app.get("/")
    async def root():
        return HTMLResponse(content=INDEX_HTML)
