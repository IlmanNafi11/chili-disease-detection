import os
import pickle
import joblib
import logging
from typing import Dict, Tuple, Optional, Any
import numpy as np
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class MLPredictionService:
    _instance: Optional['MLPredictionService'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.model_dir = os.getenv("MODEL_DIR", "models")
        self.rf_model = None
        self.scaler = None
        self.feature_info = None
        self.model_metadata = None
        
        self._load_models()
        self._initialized = True
    
    def _load_models(self) -> None:
        try:
            rf_model_path = os.path.join(self.model_dir, "rf_model.pkl")
            scaler_path = os.path.join(self.model_dir, "scaler.pkl")
            feature_info_path = os.path.join(self.model_dir, "feature_info.pkl")
            metadata_path = os.path.join(self.model_dir, "model_metadata.pkl")
            
            try:
                self.rf_model = joblib.load(rf_model_path)
                logger.info("Model Random Forest berhasil dimuat dengan joblib")
            except Exception as e:
                logger.warning(f"Gagal load dengan joblib, mencoba pickle: {e}")
                with open(rf_model_path, 'rb') as f:
                    self.rf_model = pickle.load(f)
                logger.info("Model Random Forest berhasil dimuat dengan pickle")
            
            try:
                self.scaler = joblib.load(scaler_path)
                logger.info("Scaler berhasil dimuat dengan joblib")
            except Exception as e:
                logger.warning(f"Gagal load scaler dengan joblib, mencoba pickle: {e}")
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                logger.info("Scaler berhasil dimuat dengan pickle")
            
            if os.path.exists(feature_info_path):
                try:
                    self.feature_info = joblib.load(feature_info_path)
                    logger.info("Feature info berhasil dimuat dengan joblib")
                except:
                    with open(feature_info_path, 'rb') as f:
                        self.feature_info = pickle.load(f)
                    logger.info("Feature info berhasil dimuat dengan pickle")
            
            if os.path.exists(metadata_path):
                try:
                    self.model_metadata = joblib.load(metadata_path)
                    logger.info("Model metadata berhasil dimuat dengan joblib")
                except:
                    with open(metadata_path, 'rb') as f:
                        self.model_metadata = pickle.load(f)
                    logger.info("Model metadata berhasil dimuat dengan pickle")
            
            logger.info("Semua model ML berhasil dimuat")
            
        except FileNotFoundError as e:
            logger.error(f"File model tidak ditemukan: {e}")
            raise
        except Exception as e:
            logger.error(f"Gagal memuat model: {e}")
            raise
    
    def _validate_features(self, features: Dict[str, float]) -> None:
        required_features = ['contrast', 'correlation', 'energy', 'homogeneity']
        
        for feature in required_features:
            if feature not in features:
                raise ValueError(f"Fitur {feature} tidak ditemukan")
            
            if not isinstance(features[feature], (int, float)):
                raise ValueError(f"Fitur {feature} harus berupa angka")
        
        logger.debug("Validasi fitur berhasil")
    
    def predict(self, features: Dict[str, float]) -> Tuple[int, float]:
        try:
            self._validate_features(features)
            
            feature_array = np.array([[
                features['contrast'],
                features['correlation'],
                features['energy'],
                features['homogeneity']
            ]])
            
            feature_scaled = self.scaler.transform(feature_array)
            
            prediction = self.rf_model.predict(feature_scaled)[0]
            
            prediction_proba = self.rf_model.predict_proba(feature_scaled)[0]
            confidence = float(prediction_proba[prediction])
            
            hasil = int(prediction)
            
            logger.info(f"Prediksi: {hasil} (0=sehat, 1=sakit), Confidence: {confidence:.4f}")
            
            return hasil, confidence
            
        except Exception as e:
            logger.error(f"Gagal melakukan prediksi: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_type": type(self.rf_model).__name__ if self.rf_model else None,
            "scaler_type": type(self.scaler).__name__ if self.scaler else None,
            "feature_info": self.feature_info,
            "metadata": self.model_metadata
        }


def create_ml_prediction_service() -> MLPredictionService:
    return MLPredictionService()
