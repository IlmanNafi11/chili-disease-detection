import os
import cv2


class GrayscaleConverter:
    """Konversi citra RGB ke grayscale"""
    
    @staticmethod
    def convert_single_image(image_path):
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Gambar tidak dapat dibaca: {image_path}")
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    @staticmethod
    def batch_convert(input_dir, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
        if not os.path.exists(input_dir):
            print(f"Folder tidak ditemukan: {input_dir}")
            return []
        
        image_files = [f for f in os.listdir(input_dir)
                      if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))]
        
        if not image_files:
            print(f"Tidak ada gambar di: {input_dir}")
            return []
        
        print(f"Konversi: {input_dir} → {output_dir}")
        print(f"Total: {len(image_files)} gambar")
        
        converted = []
        for idx, filename in enumerate(image_files, 1):
            try:
                gray = GrayscaleConverter.convert_single_image(os.path.join(input_dir, filename))
                cv2.imwrite(os.path.join(output_dir, filename), gray)
                converted.append(filename)
                print(f"[{idx}] {filename}")
            except Exception as e:
                print(f"[{idx}] {filename} - {str(e)}")
        
        return converted