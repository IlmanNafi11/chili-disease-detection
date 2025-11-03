import os
import cv2
import numpy as np
from rembg import remove
from PIL import Image

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def is_image_file(fname: str) -> bool:
    return os.path.splitext(fname)[1].lower() in IMG_EXTS

def remove_small_noise(mask: np.ndarray, min_area: int = 50) -> np.ndarray:
    mask = cv2.normalize(mask, None, 0, 255, cv2.NORM_MINMAX)
    _, binary = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
    
    kernel_dilate = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    binary = cv2.dilate(binary, kernel_dilate, iterations=2)
    
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary)
    
    clean_mask = np.zeros(binary.shape, dtype=np.uint8)

    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area >= min_area:
            clean_mask[labels == i] = 255
    
    return clean_mask

def smooth_mask_edges(mask: np.ndarray, blur_kernel: int = 5) -> np.ndarray:
    if blur_kernel % 2 == 0:
        blur_kernel += 1
    return cv2.GaussianBlur(mask, (blur_kernel, blur_kernel), 0)

def remove_bg_one(in_path: str, out_path: str) -> bool:
    try:
        img = Image.open(in_path)
        if img is None:
            print(f"[SKIP] Tidak bisa baca: {in_path}")
            return False
        print(f"[PROCESS] Removing background: {os.path.basename(in_path)}")
        output_rgba = remove(img)
        
        output_array = np.array(output_rgba)
        alpha_mask = output_array[:, :, 3]
        
        alpha_mask = remove_small_noise(alpha_mask, min_area=5)

        kernel_morph = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

        alpha_mask = cv2.morphologyEx(alpha_mask, cv2.MORPH_CLOSE, kernel_morph, iterations=1)
        
        kernel_dilate = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        alpha_mask = cv2.dilate(alpha_mask, kernel_dilate, iterations=1)
        
        alpha_mask = smooth_mask_edges(alpha_mask, blur_kernel=7)
        
        output_array[:, :, 3] = alpha_mask
        
        output_pil = Image.fromarray(output_array, 'RGBA')
        output_pil.save(out_path, 'PNG')
        
        print(f"[SUCCESS] Background removed: {os.path.basename(in_path)} -> {os.path.basename(out_path)}")
        return True
        
    except Exception as e:
        print(f"[ERROR] {in_path}: {e}")
        return False

def remove_dir(src_dir: str, dst_dir: str):
    ensure_dir(dst_dir)
    total, saved = 0, 0

    for root, _, files in os.walk(src_dir):
        rel = os.path.relpath(root, src_dir)
        out_root = os.path.join(dst_dir, rel) if rel != "." else dst_dir
        ensure_dir(out_root)

        for fname in sorted(files):
            if not is_image_file(fname):
                continue
            total += 1
            in_path = os.path.join(root, fname)
            base, _ = os.path.splitext(fname)
            out_path = os.path.join(out_root, base + ".png")
            if remove_bg_one(in_path, out_path):
                saved += 1

    print(f"\n{'='*60}")
    print(f"Selesai: {os.path.basename(src_dir)} -> {os.path.basename(dst_dir)}")
    print(f"Hasil: {saved}/{total} file berhasil diproses")
    print(f"{'='*60}\n")

def main():
    base_path = "/home/ilmannafi/Documents/project-pbl/resize-citra"
    pairs = [
        ("sakit-augmentation", "sakit-bg-remove"),
        ("sehat-augmentation", "sehat-bg-remove"),
    ]
    
    for src, dst in pairs:
        src_full = os.path.join(base_path, src)
        dst_full = os.path.join(base_path, dst)
        if not os.path.isdir(src_full):
            print(f"[WARNING] Folder sumber tidak ditemukan: {src_full}")
            continue
        remove_dir(src_full, dst_full)

if __name__ == "__main__":
    main()