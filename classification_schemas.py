from pydantic import BaseModel, Field, validator
from typing import Optional, List
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

class ImageUploadRequest(BaseModel):
    image: bytes = Field(...)

class UploadResponse(BaseModel):
    success: bool = Field(...)
    message: str = Field(...)
    id: str = Field(...)
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
    message: str = Field(...)
    humidity_value: float = Field(...)
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

class ErrorResponse(BaseModel):
    error: str = Field(...)
    message: str = Field(...)
    timestamp: datetime = Field(...)
    details: Optional[dict] = Field(None)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ClassificationCreate(BaseModel):
    id: str = Field(..., max_length=255)
    hasil: int = Field(..., ge=0, le=1)
    path: str = Field(..., max_length=500)
    confidence: float = Field(..., ge=0, le=1)

class ClassificationUpdate(BaseModel):
    hasil: Optional[int] = Field(None, ge=0, le=1)
    path: Optional[str] = Field(None, max_length=500)
    confidence: Optional[float] = Field(None, ge=0, le=1)

class ClassificationResponse(BaseModel):
    id: str
    hasil: int
    path: str
    confidence: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ClassificationListResponse(BaseModel):
    results: List[ClassificationResponse]
    total_count: int
    timestamp: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }