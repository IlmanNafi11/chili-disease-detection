from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Header, Request
from sqlalchemy.orm import Session
from typing import Optional
import os
import uuid
import logging
from datetime import datetime
import shutil

from ...database import get_db
from ...models.models import Classification
from ...schemas.classification_schemas import (
    HealthResponse, UploadResponse, HumidityDataRequest, HumidityResponse,
    ClassificationResultsResponse, ClassificationResult, ConfigResponse
)
from ...services.classification_service import create_classification_service
from ...services.humidity_service import create_humidity_service
from ...services.image_processing_service import create_image_processing_service
from ...services.ml_prediction_service import create_ml_prediction_service
from ...utils.image_utils import generate_filename

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["API"])

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    expected_api_key = os.getenv("API_KEY")
    if not expected_api_key:
        logger.warning("API_KEY tidak dikonfigurasi di environment")
        return
    
    if not x_api_key or x_api_key != expected_api_key:
        logger.warning(f"Percobaan API key tidak valid: {x_api_key}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key tidak valid",
            headers={"WWW-Authenticate": "ApiKey"},
        )

def validate_image_file(file: UploadFile):
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File gambar diperlukan",
        )
    
    if file.size and file.size > int(os.getenv("MAX_FILE_SIZE", 10485760)):
        raise HTTPException(
            status_code=status.HTTP_413_PAYLOAD_TOO_LARGE,
            detail="File terlalu besar. Maksimal 10MB",
        )
    
    allowed_types = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format file tidak valid. Hanya JPG, PNG, dan WEBP yang diperbolehkan",
        )
    
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nama file diperlukan",
        )
    
    file_ext = os.path.splitext(file.filename.lower())[1]
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ekstensi file tidak valid. Hanya .jpg, .jpeg, .png, .webp yang diperbolehkan",
        )

@router.get(
    "/health",
    response_model=HealthResponse,
    dependencies=[Depends(verify_api_key)],
    summary="Periksa kesehatan sistem",
    description="Endpoint untuk memverifikasi bahwa sistem sedang berjalan dan dapat menangani request"
)
async def health_check():
    try:
        db = next(get_db())
        db_status = "connected" if db else "disconnected"
        db.close()
        
        status_info = "sehat"
        message = "Sistem berjalan normal"
        
        if db_status == "disconnected":
            status_info = "tidak_sehat"
            message = "Koneksi database terputus"
        
        logger.info("Health check performed successfully")
        
        return HealthResponse(
            status=status_info,
            message=message,
            timestamp=datetime.utcnow(),
            version=os.getenv("APP_VERSION", "1.0.0")
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="tidak_sehat",
            message="Sistem mengalami masalah",
            timestamp=datetime.utcnow(),
            version=os.getenv("APP_VERSION", "1.0.0")
        )

@router.post(
    "/upload-gambar",
    response_model=UploadResponse,
    dependencies=[Depends(verify_api_key)],
    summary="Upload gambar tanaman untuk klasifikasi",
    description="Endpoint untuk mengunggah gambar tanaman cabai yang akan dianalisis untuk mendeteksi penyakit"
)
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    temp_upload_path = None
    
    try:
        validate_image_file(file)
        
        upload_dir = os.getenv("UPLOAD_DIR", "static/uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        file_id = f"img_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"
        file_ext = os.path.splitext(file.filename)[1]
        filename = f"{file_id}{file_ext}"
        temp_upload_path = os.path.join(upload_dir, filename)
        
        logger.info(f"Menyimpan file upload: {filename}")
        with open(temp_upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info("Memulai prediksi ML dengan pipeline image processing")
        ml_service = create_ml_prediction_service()
        image_service = create_image_processing_service()
        
        logger.info("Step 1: Proses gambar dengan pipeline")
        temp_klasifikasi = "temp"
        processed_path, features = image_service.process_image(temp_upload_path, temp_klasifikasi)
        
        logger.info(f"Fitur GLCM diekstrak: {features}")
        
        logger.info("Step 2: Prediksi menggunakan Random Forest model")
        hasil, confidence = ml_service.predict(features)
        
        klasifikasi_label = "sehat" if hasil == 0 else "sakit"
        logger.info(f"Hasil prediksi: {klasifikasi_label} (confidence: {confidence:.4f})")
        
        final_filename = generate_filename(klasifikasi_label, "png")
        result_dir = os.getenv("RESULT_DIR", "static/result")
        final_path = os.path.join(result_dir, final_filename)
        
        logger.info("Step 3: Rename file hasil dengan klasifikasi yang benar")
        if os.path.exists(processed_path.lstrip('/')):
            actual_processed_path = processed_path.lstrip('/')
        else:
            actual_processed_path = processed_path
        
        if os.path.exists(actual_processed_path):
            shutil.move(actual_processed_path, final_path)
        else:
            temp_processed = processed_path.replace("/static/result/", "static/result/")
            if os.path.exists(temp_processed):
                shutil.move(temp_processed, final_path)
        
        final_relative_path = f"/static/result/{final_filename}"
        
        logger.info("Step 4: Simpan hasil ke database")
        classification_service = create_classification_service(db)
        classification = classification_service.create_classification(
            classification_id=file_id,
            hasil=hasil,
            path=final_relative_path
        )
        
        image_service.cleanup_upload_file(temp_upload_path)
        
        logger.info(f"Upload dan klasifikasi berhasil: {file_id}, hasil: {klasifikasi_label}")
        
        return UploadResponse(
            success=True,
            message=f"Gambar berhasil diklasifikasikan sebagai tanaman {klasifikasi_label}",
            id=file_id,
            hasil=hasil,
            confidence=confidence,
            gambar_url=final_relative_path,
            upload_time=datetime.utcnow()
        )
        
    except HTTPException:
        if temp_upload_path and os.path.exists(temp_upload_path):
            try:
                os.remove(temp_upload_path)
            except:
                pass
        raise
    except Exception as e:
        logger.error(f"Error memproses gambar: {e}", exc_info=True)
        if temp_upload_path and os.path.exists(temp_upload_path):
            try:
                os.remove(temp_upload_path)
            except:
                pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Kesalahan server saat memproses gambar: {str(e)}"
        )

@router.post(
    "/data-kelembapan",
    response_model=HumidityResponse,
    dependencies=[Depends(verify_api_key)],
    summary="Menerima data kelembapan dari sensor ESP32",
    description="Endpoint untuk menerima data kelembapan tanah dari sensor IoT ESP32"
)
async def submit_humidity_data(
    request: HumidityDataRequest,
    db: Session = Depends(get_db)
):
    try:
        humidity_service = create_humidity_service()
        humidity_service.update_humidity(request.kelembapan)
        
        logger.info(f"Data kelembapan diterima: {request.kelembapan}%")
        
        return HumidityResponse(
            success=True,
            kelembapan=request.kelembapan,
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error menerima data kelembapan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Kesalahan server saat memproses data kelembapan"
        )

@router.get(
    "/kelembapan",
    response_model=HumidityResponse,
    dependencies=[Depends(verify_api_key)],
    summary="Ambil data kelembapan terbaru",
    description="Endpoint untuk mengambil data kelembapan terbaru yang diterima dari ESP32"
)
async def get_current_humidity(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        humidity_service = create_humidity_service()
        humidity_status = humidity_service.get_humidity_status()
        
        if humidity_status["value"] is None:
            return HumidityResponse(
                success=False,
                kelembapan=-1.0,
                timestamp=datetime.utcnow()
            )
        
        return HumidityResponse(
            success=True,
            kelembapan=humidity_status["value"],
            timestamp=humidity_status["last_update"] or datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error mengambil data kelembapan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Kesalahan server saat mengambil data kelembapan"
        )

@router.get(
    "/config",
    response_model=ConfigResponse,
    dependencies=[Depends(verify_api_key)],
    summary="Ambil konfigurasi aplikasi",
    description="Endpoint untuk mengambil konfigurasi aplikasi seperti jam polling klasifikasi"
)
async def get_config(
    request: Request
):
    try:
        polling_hours = int(os.getenv("CLASSIFICATION_POLLING_HOURS", "16"))
        polling_minutes = int(os.getenv("CLASSIFICATION_POLLING_MINUTES", "25"))
        logger.info(f"Konfigurasi jam polling klasifikasi: {polling_hours}:{polling_minutes:02d}")
        
        return ConfigResponse(
            classification_polling_hours=polling_hours,
            classification_polling_minutes=polling_minutes
        )
        
    except Exception as e:
        logger.error(f"Error mengambil konfigurasi: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Kesalahan server saat mengambil konfigurasi"
        )

@router.get(
    "/hasil-klasifikasi",
    response_model=ClassificationResultsResponse,
    dependencies=[Depends(verify_api_key)],
    summary="Mengambil data hasil klasifikasi",
    description="Endpoint untuk mengambil hasil klasifikasi penyakit tanaman cabai"
)
async def get_classification_results(
    request: Request,
    id: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    try:
        classification_service = create_classification_service(db)
        
        if id:
            classification = classification_service.get_classification_by_id(id)
            if not classification:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Hasil klasifikasi untuk id tersebut tidak ditemukan"
                )
            
            results = [
                ClassificationResult(
                    id=classification.id,
                    hasil=classification.hasil,
                    gambar_url=classification.path,
                    timestamp=classification.created_at
                )
            ]
            total_count = 1
        else:
            if limit < 1 or limit > 100:
                limit = 10
            
            classifications = classification_service.get_all_classifications(limit=limit)
            
            results = [
                ClassificationResult(
                    id=c.id,
                    hasil=c.hasil,
                    gambar_url=c.path,
                    timestamp=c.created_at
                )
                for c in classifications
            ]
            total_count = len(results)
        
        return ClassificationResultsResponse(
            success=True,
            results=results,
            total_count=total_count,
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saat mengambil hasil klasifikasi: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Kesalahan server saat mengambil data"
        )

