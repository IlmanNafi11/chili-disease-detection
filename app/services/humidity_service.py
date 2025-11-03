from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class HumidityService:
    
    def __init__(self):
        pass
    
    def process_humidity_data(self, kelembapan: float) -> Dict[str, Any]:
        try:
            logger.info(f"Processing humidity data: {kelembapan}%")
            
            result = {
                "kelembapan": kelembapan,
                "timestamp": datetime.utcnow(),
                "status": "processed",
                "message": "Data kelembapan berhasil diproses"
            }
            
            return result
        except Exception as e:
            logger.error(f"Error processing humidity data: {e}")
            raise
    
    def get_latest_humidity_info(self, kelembapan: float) -> Dict[str, Any]:
        try:
            from datetime import datetime
            
            return {
                "kelembapan_terbaru": kelembapan,
                "timestamp": datetime.utcnow(),
                "status": "aktif",
                "keterangan": "Data terbaru dari sensor"
            }
        except Exception as e:
            logger.error(f"Error getting latest humidity info: {e}")
            raise
    
    def analyze_humidity(self, kelembapan: float) -> Dict[str, Any]:
        try:
            status = "optimal"
            message = "Kelembapan dalam kondisi optimal"
            
            if kelembapan < 30:
                status = "kering"
                message = "Kelembapan terlalu kering, perlu penyiraman"
            elif kelembapan > 80:
                status = "basah"
                message = "Kelembapan terlalu basah, perlu drainage"
            elif kelembapan < 40:
                status = "kurang"
                message = "Kelembapan kurang, perlu perhatian"
            elif kelembapan > 70:
                status = "berlebih"
                message = "Kelembapan berlebih, perlu pengurangan air"
            
            return {
                "kelembapan": kelembapan,
                "status": status,
                "message": message,
                "timestamp": datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error analyzing humidity: {e}")
            raise

def create_humidity_service() -> HumidityService:
    return HumidityService()