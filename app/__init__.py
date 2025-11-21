from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from pathlib import Path

from .api.endpoints.api_endpoints import router as api_router
from .database import create_tables
from .config import get_config

config = get_config()

app = FastAPI(
    title="API Agro Chili Sense",
    description="API untuk sistem deteksi penyakit tanaman cabai menggunakan machine learning dan monitoring kelembapan tanah dengan IoT",
    version=config.app_version,
    docs_url="/docs",
    redoc_url="/redoc"
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
