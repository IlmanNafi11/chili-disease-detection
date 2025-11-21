import os
import logging
from typing import Dict, Tuple
from datetime import datetime

from ..utils.image_utils import (
    resize_single_image,
    remove_background_single,
    convert_to_grayscale_single,
    extract_glcm_features_single,
    generate_filename,
    ensure_directory_exists
)

logger = logging.getLogger(__name__)


class ImageProcessingService:
    
    def __init__(self):
        self.upload_dir = os.getenv("UPLOAD_DIR", "static/uploads")
        self.result_dir = os.getenv("RESULT_DIR", "static/result")
        
        ensure_directory_exists(self.upload_dir)
        ensure_directory_exists(self.result_dir)
    
    def process_image(
        self, 
        input_path: str
    ) -> Tuple[str, Dict[str, float]]:
        temp_files = []
        
        try:
            logger.info(f"Memulai pemrosesan gambar: {input_path}")
            
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            temp_dir = os.path.join(self.upload_dir, "temp")
            ensure_directory_exists(temp_dir)
            
            resized_path = os.path.join(temp_dir, f"{base_name}_resized.png")
            logger.info("Step 1: Resize gambar ke 224x224")
            resize_single_image(input_path, resized_path, size=(224, 224))
            temp_files.append(resized_path)
            
            bg_removed_path = os.path.join(temp_dir, f"{base_name}_nobg.png")
            logger.info("Step 2: Hapus background")
            remove_background_single(resized_path, bg_removed_path)
            temp_files.append(bg_removed_path)
            
            grayscale_path = os.path.join(temp_dir, f"{base_name}_gray.png")
            logger.info("Step 3: Konversi ke grayscale")
            convert_to_grayscale_single(bg_removed_path, grayscale_path)
            temp_files.append(grayscale_path)
            
            logger.info("Step 4: Ekstrak fitur GLCM")
            features = extract_glcm_features_single(grayscale_path)
            
            self._cleanup_temp_files(temp_files)
            
            logger.info(f"Pemrosesan gambar selesai, fitur GLCM diekstrak")
            return input_path, features
            
        except Exception as e:
            logger.error(f"Gagal memproses gambar: {e}")
            self._cleanup_temp_files(temp_files)
            raise
    
    def _cleanup_temp_files(self, file_paths: list) -> None:
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"File temporary dihapus: {file_path}")
            except Exception as e:
                logger.warning(f"Gagal menghapus file temporary {file_path}: {e}")
    
    def cleanup_upload_file(self, file_path: str) -> None:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"File upload dihapus: {file_path}")
        except Exception as e:
            logger.warning(f"Gagal menghapus file upload {file_path}: {e}")
    
    def validate_image_path(self, path: str) -> bool:
        if not os.path.exists(path):
            logger.error(f"File tidak ditemukan: {path}")
            return False
        
        if not os.path.isfile(path):
            logger.error(f"Path bukan file: {path}")
            return False
        
        return True


def create_image_processing_service() -> ImageProcessingService:
    return ImageProcessingService()
