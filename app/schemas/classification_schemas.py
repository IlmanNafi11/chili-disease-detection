from pydantic import BaseModel, Field, validator
from typing import List
from datetime import datetime


class HealthResponse(BaseModel):
    status: str = Field(...)
    message: str = Field(...)
    timestamp: datetime = Field(...)
    version: str = Field(...)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UploadResponse(BaseModel):
    success: bool = Field(...)
    message: str = Field(...)
    id: str = Field(...)
    hasil: int = Field(..., ge=0, le=1)
    confidence: float = Field(..., ge=0, le=1)
    gambar_url: str = Field(...)
    upload_time: datetime = Field(...)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class HumidityDataRequest(BaseModel):
    kelembapan: float = Field(..., ge=0, le=100)

    @validator('kelembapan')
    def validate_kelembapan(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('Nilai kelembapan harus berupa angka antara 0-100')
        return v

class HumidityResponse(BaseModel):
    success: bool = Field(...)
    kelembapan: float = Field(...)
    timestamp: datetime = Field(...)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ClassificationResult(BaseModel):
    id: str = Field(...)
    hasil: int = Field(..., ge=0, le=1)
    gambar_url: str = Field(...)
    timestamp: datetime = Field(...)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ClassificationResultsResponse(BaseModel):
    success: bool = Field(...)
    results: List[ClassificationResult] = Field(...)
    total_count: int = Field(..., ge=0)
    timestamp: datetime = Field(...)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ConfigResponse(BaseModel):
    classification_polling_hours: int = Field(...)
    classification_polling_minutes: int = Field(...)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
