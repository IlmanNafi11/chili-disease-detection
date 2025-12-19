import os
from typing import Optional
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class Config:
    _instance: Optional['Config'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.base_url_development = os.getenv("BASE_URL_DEVELOPMENT", "http://localhost:8000")
        self.base_url_production = os.getenv("BASE_URL_PRODUCTION", "https://api.chili-detection.com")
        self.database_url = os.getenv("DATABASE_URL", "mysql+pymysql://root:admin@localhost:3306/smartchili")
        self.api_key = os.getenv("API_KEY", "")
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE", "10485760"))
        self.upload_dir = os.getenv("UPLOAD_DIR", "static/uploads")
        self.result_dir = os.getenv("RESULT_DIR", "static/result")
        self.model_dir = os.getenv("MODEL_DIR", "models")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_format = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.app_version = os.getenv("APP_VERSION", "1.0.0")
        self.cors_origins = os.getenv("CORS_ORIGINS", "*").replace('"', '').split(',')
        self.classification_polling_hours = int(os.getenv("CLASSIFICATION_POLLING_HOURS", "15"))
        self.classification_polling_minutes = int(os.getenv("CLASSIFICATION_POLLING_MINUTES", "28"))
        self.humidity_polling_interval_ms = int(os.getenv("HUMIDITY_POLLING_INTERVAL_MS", "3000"))
        self.timezone = os.getenv("TIMEZONE", "Asia/Jakarta")
        
        self._initialized = True
        logger.info(f"Config diinisialisasi untuk environment: {self.environment}")
    
    @property
    def base_url(self) -> str:
        if self.environment == "production":
            return self.base_url_production
        return self.base_url_development

def get_config() -> Config:
    return Config()
