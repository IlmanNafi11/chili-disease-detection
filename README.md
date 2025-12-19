# Sistem Deteksi penyakit Tanaman Cabai

## Deskripsi Proyek

Sistem deteksi penyakit tanaman cabai menggunakan machine learning dan IoT. Sistem ini menyediakan:

- Klasifikasi penyakit otomatis melalui upload gambar tanaman
- Pipeline image processing dengan preprocessing lengkap
- Machine learning menggunakan Random Forest classifier
- Monitoring kelembapan real-time dari sensor IoT
- Web interface yang user-friendly untuk upload dan monitoring

## Fitur Utama

### Pipeline Image Processing

1. Upload - Gambar diunggah ke sistem
2. Resize - Resize ke 224x224 pixels
3. Remove Background - Hapus background otomatis
4. Grayscale - Konversi ke grayscale
5. Feature Extraction - Ekstrak fitur GLCM (contrast, correlation, energy, homogeneity)
6. Classification - Prediksi menggunakan Random Forest model
7. Save - Simpan hasil ke database dan static/result/

### Model Machine Learning

- Algorithm: Random Forest Classifier
- Features: GLCM (Gray-Level Co-occurrence Matrix)
- Output: 0 = Sehat, 1 = Sakit
- Confidence Score: Probabilitas prediksi

## Struktur Project

```text
chili-disease-detection/
├── .env                    # Environment variables
├── .env.example           # Environment variables template
├── alembic/               # Database migrations
├── app/
│   ├── __init__.py       # FastAPI application initialization
│   ├── database.py       # Database configuration
│   ├── api/
│   │   └── endpoints/
│   │       └── api_endpoints.py  # API route handlers
│   ├── models/
│   │   └── models.py     # SQLAlchemy database models
│   ├── schemas/
│   │   └── classification_schemas.py  # Pydantic schemas
│   ├── services/
│   │   ├── classification_service.py  # Classification business logic
│   │   ├── humidity_service.py        # Humidity singleton service
│   │   ├── image_processing_service.py # Image processing pipeline
│   │   └── ml_prediction_service.py   # ML prediction singleton
│   └── utils/
│       └── image_utils.py             # Image utility functions
├── models/                # ML model files (pkl)
├── static/
│   ├── uploads/          # Uploaded images
│   ├── result/           # Classification result images
│   ├── style.css         # CSS styles
│   └── style.js          # JavaScript files
├── templates/
│   └── index.html        # Main page template
├── main.py               # Application entry point
├── api-specification.yaml # OpenAPI specification
├── requirements.txt      # Python dependencies
└── README.md            # Documentation
```

## Instalasi dan Setup

### 1. Prerequisites

- Python 3.8+
- MySQL 8.0+
- Docker (untuk MySQL)

### 2. Setup Database MySQL

```bash
# Jalankan MySQL container (jika belum berjalan)
docker run --name invento -e MYSQL_ROOT_PASSWORD=admin -e MYSQL_DATABASE=smartchili -p 3306:3306 -d mysql:8.0
```

### 3. Setup Project

```bash
# Clone atau download project
cd chili-disease-detection

# Buat virtual environment
python3 -m venv venv

# Aktifkan virtual environment
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Buat direktori uploads
mkdir -p static/uploads
```

### 4. Konfigurasi

Edit file `.env` sesuai dengan environment Anda:

```env
# Database Configuration
DATABASE_URL=mysql+pymysql://root:admin@localhost:3306/smartchili

# API Security
API_KEY=smartchili-api-key-2025
API_BASE_URL=/api/v1

# Application Settings
APP_VERSION=1.0.0

# File Upload Settings
MAX_FILE_SIZE=10485760  # 10MB
UPLOAD_DIR=static/uploads
RESULT_DIR=static/result
MODEL_DIR=models

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# CORS Configuration
CORS_ORIGINS=*

# Classification Polling Schedule
CLASSIFICATION_POLLING_HOURS=15
CLASSIFICATION_POLLING_MINUTES=28
TIMEZONE=Asia/Jakarta
```

### 5. Jalankan Aplikasi

```bash
# Aktifkan venv dan jalankan aplikasi
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Aplikasi akan berjalan di: http://localhost:8000

## API Documentation

Dokumentasi API otomatis tersedia di:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Architecture

### Layered Architecture

```text
API Layer (FastAPI Routes) 
    ↓
Service Layer (Business Logic)
    ↓
Data Layer (Database Models)
```

### Design Patterns

- Repository Pattern: ClassificationService untuk CRUD operations
- Singleton Pattern: HumidityService untuk real-time data
- Dependency Injection: Database sessions via FastAPI dependencies

## Security Features

- API Key Authentication: Semua endpoint memerlukan valid API key
- Input Validation: Pydantic schemas untuk validasi input
- File Upload Security: Validasi format dan ukuran file
- SQL Injection Protection: ORM Query parameters

## Deployment

1. Set `ENVIRONMENT=production` di `.env`
2. Set `DEBUG=false`
3. Gunakan HTTPS untuk production
4. Setup proper database backup
5. Configure monitoring dan alerting
6. Setup proper logging aggregation

## Monitoring

Logging terstruktur dengan levels:

- INFO: General application events
- WARNING: Non-critical issues
- ERROR: Errors yang memerlukan attention
- DEBUG: Detailed debugging information

Log file tersimpan di `app.log`.
