from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from dotenv import load_dotenv

load_dotenv()

from api_endpoints import router as api_router
from database import create_tables

app = FastAPI(
    title="API Sistem Deteksi Enfermedades Tanaman Cabai",
    description="API untuk sistem deteksi penyakit tanaman cabai menggunakan machine learning dan monitoring kelembapan tanah dengan IoT",
    version=os.getenv("APP_VERSION", "1.0.0"),
    docs_url="/docs",
    redoc_url="/redoc"
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", ["*"]).replace('"', '').split(','),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def setup_logging():
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_format = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("app.log")
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Logging setup completed")

@app.on_event("startup")
async def startup_event():
    setup_logging()
    create_tables()
    logger = logging.getLogger(__name__)
    logger.info("Application started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    logger = logging.getLogger(__name__)
    logger.info("Application shutting down")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    data = {
        "status_bibit": "Sehat",
        "kelembapan": "60%",
        "tanggal": "2 November 2025",
        "api_docs": "/docs"
    }
    return templates.TemplateResponse("index.html", {"request": request, "data": data})
