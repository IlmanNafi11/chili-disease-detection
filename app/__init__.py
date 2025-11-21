from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import yaml
import json
import logging
import os
from pathlib import Path

from .api.endpoints.api_endpoints import router as api_router
from .database import create_tables
from .config import get_config

config = get_config()

def load_openapi_spec():
    openapi_path = Path("api-specification.yaml")
    if openapi_path.exists():
        with open(openapi_path, "r", encoding="utf-8") as f:
            spec = yaml.safe_load(f)
        return spec
    else:
        return {}

custom_openapi = load_openapi_spec()

app = FastAPI(
    title="API Agro Chili Sense",
    description="API untuk sistem deteksi penyakit tanaman cabai menggunakan machine learning dan monitoring kelembapan tanah dengan IoT",
    version=config.app_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

def get_custom_openapi():
    if custom_openapi:
        return custom_openapi
    else:
        return app.openapi()

app.openapi = get_custom_openapi

@app.get("/openapi-yaml", include_in_schema=False)
async def get_openapi_yaml():
    return HTMLResponse(
        content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>API Specification - YAML</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                pre {{ background: #f8f9fa; padding: 15px; border-radius: 4px; overflow-x: auto; border: 1px solid #e9ecef; }}
                h1 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
                .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
                .btn {{ background: #007bff; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; font-size: 14px; }}
                .btn:hover {{ background: #0056b3; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Agro Chili Sense API Specification</h1>
                    <div>
                        <a href="/docs" class="btn">Swagger UI</a>
                        <a href="/redoc" class="btn">ReDoc</a>
                    </div>
                </div>
                <p><strong>API Title:</strong> {custom_openapi.get('info', {}).get('title', 'N/A')}</p>
                <p><strong>Version:</strong> {custom_openapi.get('info', {}).get('version', 'N/A')}</p>
                <p><strong>Description:</strong> {custom_openapi.get('info', {}).get('description', 'N/A')}</p>
                <h2>📄 Raw YAML Specification</h2>
                <pre><code id="yaml-content">Loading...</code></pre>
            </div>
            <script>
                fetch('/api-spec')
                    .then(response => response.text())
                    .then(yaml_content => {{
                        document.getElementById('yaml-content').textContent = yaml_content;
                    }})
                    .catch(error => {{
                        document.getElementById('yaml-content').textContent = 'Error loading specification: ' + error;
                    }});
            </script>
        </body>
        </html>
        """,
        media_type="text/html"
    )

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def setup_logging():
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format=config.log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("app.log")
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Setup logging selesai")

@app.on_event("startup")
async def startup_event():
    setup_logging()
    create_tables()
    
    logger = logging.getLogger(__name__)
    logger.info("Aplikasi berhasil dijalankan")

@app.on_event("shutdown")
async def shutdown_event():
    logger = logging.getLogger(__name__)
    logger.info("Aplikasi dimatikan")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    data = {
        "status_bibit": "Tidak Tersedia",
        "kelembapan": "Tidak Tersedia",
        "tanggal": "N/A",
        "api_docs": "/docs"
    }
    
    # Inject configuration to frontend
    frontend_config = {
        "API_KEY": config.api_key,
        "API_BASE_URL": "/api/v1",
        "HUMIDITY_POLLING_INTERVAL_MS": config.humidity_polling_interval_ms,
        "CLASSIFICATION_POLLING_HOUR": config.classification_polling_hours,
        "CLASSIFICATION_POLLING_MINUTE": config.classification_polling_minutes
    }
    
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "data": data,
            "config": frontend_config
        }
    )

@app.get("/api-spec", include_in_schema=False)
async def get_api_spec():
    """Serve the custom OpenAPI specification file"""
    openapi_path = Path("api-specification.yaml")
    if openapi_path.exists():
        with open(openapi_path, "r", encoding="utf-8") as f:
            content = f.read()
        return JSONResponse(
            content=content,
            media_type="application/yaml"
        )
    else:
        raise HTTPException(status_code=404, detail="API specification not found")

@app.get("/api-docs-yaml", include_in_schema=False)
async def get_api_docs_yaml():
    """Serve API documentation in YAML format"""
    if custom_openapi:
        return JSONResponse(
            content=custom_openapi,
            media_type="application/json"
        )
    else:
        return JSONResponse(
            content=app.openapi(),
            media_type="application/json"
        )

