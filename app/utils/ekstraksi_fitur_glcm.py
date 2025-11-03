import os
import cv2
import numpy as np
import pandas as pd
from skimage.feature import graycomatrix, graycoprops


class GLCMFeatureExtractor:
    """Ekstraksi fitur GLCM dari citra grayscale"""
    
    def __init__(self, distance=1, angle=0):
        self.distance = distance
        self.angle = angle
    
    def extract_features(self, image_path):
        gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if gray is None:
            raise ValueError(f"Gambar tidak dapat dibaca: {image_path}")
        
        glcm = graycomatrix(gray, distances=[self.distance], 
                           angles=[np.radians(self.angle)], 
                           levels=256, symmetric=True, normed=True)
        
        return {
            'contrast': float(graycoprops(glcm, 'contrast')[0, 0]),
            'correlation': float(graycoprops(glcm, 'correlation')[0, 0]),
            'energy': float(graycoprops(glcm, 'energy')[0, 0]),
            'homogeneity': float(graycoprops(glcm, 'homogeneity')[0, 0])
        }
    
    def process_directory(self, directory_path, label):
        data = []
        
        if not os.path.exists(directory_path):
            print(f"Folder tidak ditemukan: {directory_path}")
            return data
        
        image_files = [f for f in os.listdir(directory_path)
                      if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))]
        
        if not image_files:
            print(f"Tidak ada gambar di: {directory_path}")
            return data
        
        print(f"Ekstraksi: {directory_path}")
        print(f"Total: {len(image_files)} gambar")
        
        for idx, filename in enumerate(image_files, 1):
            try:
                features = self.extract_features(os.path.join(directory_path, filename))
                row = {'filename': filename, 'label': label}
                row.update(features)
                data.append(row)
                print(f"[{idx}] {filename}")
            except Exception as e:
                print(f"[{idx}] {filename} - {str(e)}")
        
        return data
    
    def extract_all_datasets(self, sehat_dir, sakit_dir, output_csv='glcm_features.csv'):
        print("\n" + "="*70)
        print("EKSTRAKSI FITUR GLCM")
        print("="*70)
        
        all_data = []
        sehat_data = self.process_directory(sehat_dir, '0')
        all_data.extend(sehat_data)
        
        sakit_data = self.process_directory(sakit_dir, '1')
        all_data.extend(sakit_data)
        
        df = pd.DataFrame(all_data)
        df.to_csv(output_csv, index=False)
        
        print("\n" + "="*70)
        
        if df.empty:
            print("TIDAK ADA DATA! Periksa folder dataset Anda.")
            return df
        
        print(f"Total: {len(df)} gambar | Sehat: {len(sehat_data)} | Sakit: {len(sakit_data)}")
        print(f"Disimpan: {output_csv}")
        print("Preview:")
        print(df.head())
        print("Statistik:")
        print(df.groupby('label')[['contrast', 'correlation', 'energy', 'homogeneity']].mean())
        print("="*70)
        
        return df