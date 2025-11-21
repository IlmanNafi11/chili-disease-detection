from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class HumidityService:
    _current_humidity: Optional[float] = None
    _last_update: Optional[datetime] = None
    _instance = None
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HumidityService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not HumidityService._initialized:
            logger.info("HumidityService diinisialisasi")
            HumidityService._initialized = True
    
    def update_humidity(self, kelembapan: float) -> None:
        HumidityService._current_humidity = kelembapan
        HumidityService._last_update = datetime.utcnow()
        logger.info(f"Kelembapan diupdate: {kelembapan}%")
    
    def get_current_humidity(self) -> Optional[float]:
        return HumidityService._current_humidity
    
    def get_last_update(self) -> Optional[datetime]:
        return HumidityService._last_update
    
    def get_humidity_status(self) -> Dict[str, Any]:
        current_humidity = self.get_current_humidity()
        last_update = self.get_last_update()
        
        if current_humidity is None:
            return {
                "status": "Tidak Tersedia",
                "value": None,
                "last_update": last_update,
                "message": "Data kelembapan tidak tersedia"
            }
        
        status_text = "Optimal" if 40 <= current_humidity <= 70 else "Tidak Optimal"
        return {
            "status": status_text,
            "value": current_humidity,
            "last_update": last_update,
            "message": f"Kelembapan {status_text.lower()}: {current_humidity}%"
        }

_instance = None

def create_humidity_service() -> HumidityService:
    global _instance
    if _instance is None:
        _instance = HumidityService()
    return _instance