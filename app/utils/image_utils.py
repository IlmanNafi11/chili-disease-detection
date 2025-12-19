import os
import cv2
import numpy as np
from PIL import Image
from rembg import remove
from skimage.feature import graycomatrix, graycoprops
from datetime import datetime
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


def generate_filename(klasifikasi: str, extension: str = "png") -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{klasifikasi}_{timestamp}.{extension}"


def resize_single_image(input_path: str, output_path: str, size: Tuple[int, int] = (224, 224)) -> str:
    try:
        img = Image.open(input_path)
        img_resized = img.resize(size, Image.Resampling.LANCZOS)
        img_resized.save(output_path)
        logger.info(f"Gambar berhasil diresize: {os.path.basename(output_path)}")
        return output_path
    except Exception as e:
        logger.error(f"Gagal resize gambar {input_path}: {e}")
        raise


def remove_background_single(input_path: str, output_path: str) -> str:
    try:
        img = Image.open(input_path)
        output_rgba = remove(img)
        
        output_array = np.array(output_rgba)
        alpha_mask = output_array[:, :, 3]
        
        alpha_mask = cv2.normalize(alpha_mask, None, 0, 255, cv2.NORM_MINMAX)
        _, binary = cv2.threshold(alpha_mask, 127, 255, cv2.THRESH_BINARY)
        
        kernel_dilate = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        binary = cv2.dilate(binary, kernel_dilate, iterations=2)
        
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary)
        clean_mask = np.zeros(binary.shape, dtype=np.uint8)
        
        min_area = 50
        for i in range(1, num_labels):
            area = stats[i, cv2.CC_STAT_AREA]
            if area >= min_area:
                clean_mask[labels == i] = 255
        
        kernel_morph = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        clean_mask = cv2.morphologyEx(clean_mask, cv2.MORPH_CLOSE, kernel_morph, iterations=1)
        
        clean_mask = cv2.GaussianBlur(clean_mask, (7, 7), 0)
        
        output_array[:, :, 3] = clean_mask
        output_pil = Image.fromarray(output_array, 'RGBA')
        output_pil.save(output_path, 'PNG')
        
        logger.info(f"Background berhasil dihapus: {os.path.basename(output_path)}")
        return output_path
    except Exception as e:
        logger.error(f"Gagal hapus background {input_path}: {e}")
        raise


def convert_to_grayscale_single(input_path: str, output_path: str) -> str:
    try:
        img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
        
        if img is None:
            raise ValueError(f"Tidak dapat membaca gambar: {input_path}")
        
        if len(img.shape) == 2:
            gray = img
        elif img.shape[2] == 4:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        else:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        cv2.imwrite(output_path, gray)
        logger.info(f"Gambar berhasil dikonversi ke grayscale: {os.path.basename(output_path)}")
        return output_path
    except Exception as e:
        logger.error(f"Gagal konversi ke grayscale {input_path}: {e}")
        raise


def extract_glcm_features_single(image_path: str, distance: int = 1, angle: int = 0) -> Dict[str, float]:
    try:
        gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        
        if gray is None:
            raise ValueError(f"Tidak dapat membaca gambar: {image_path}")
        
        glcm = graycomatrix(
            gray, 
            distances=[distance], 
            angles=[np.radians(angle)], 
            levels=256, 
            symmetric=True, 
            normed=True
        )
        
        features = {
            'contrast': float(graycoprops(glcm, 'contrast')[0, 0]),
            'correlation': float(graycoprops(glcm, 'correlation')[0, 0]),
            'energy': float(graycoprops(glcm, 'energy')[0, 0]),
            'homogeneity': float(graycoprops(glcm, 'homogeneity')[0, 0])
        }
        
        logger.info(f"Fitur GLCM berhasil diekstrak dari: {os.path.basename(image_path)}")
        return features
    except Exception as e:
        logger.error(f"Gagal ekstrak fitur GLCM dari {image_path}: {e}")
        raise


def ensure_directory_exists(directory: str) -> None:
    os.makedirs(directory, exist_ok=True)
    logger.debug(f"Direktori dipastikan ada: {directory}")
