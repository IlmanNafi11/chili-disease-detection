from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import shutil
import os

# ======================
# KONFIGURASI DATABASE
# ======================
DATABASE_URL = "mysql+pymysql://root:@localhost/klasifikasi_cabai"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ======================
# MODEL DATABASE
# ======================
class Klasifikasi(Base):
    __tablename__ = "klasifikasi"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    path = Column(String(255))
    hasil = Column(Integer, nullable=True)  # tinyint(1)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
    )

# Tidak perlu Base.metadata.create_all kalau tabel sudah ada di MySQL

# ======================
# KONFIGURASI FASTAPI
# ======================
app = FastAPI(title="API Klasifikasi Cabai", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ======================================
# ENDPOINT UPLOAD ESP 32 CAM TO DATABASE
# ======================================
@app.post("/upload_image")
async def upload_data(
    file: UploadFile = File(...),
):
    try:
        # Simpan file
        file_location = f"{UPLOAD_DIR}/{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Simpan ke database
        db = SessionLocal()
        new_data = Klasifikasi(path=file_location)
        db.add(new_data)
        db.commit()
        db.refresh(new_data)
        db.close()

        return JSONResponse(content={
            "message": "Data berhasil disimpan",
            "data": {
                "id": new_data.id,
                "path": new_data.path,
            #    "hasil": "Sehat" if new_data.hasil == 1 else "Sakit",
                "created_at": str(new_data.created_at),
                "updated_at": str(new_data.updated_at)
            }
        })
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# =============================
# ENDPOINT GET DATA KLASIFIKASI
# =============================
@app.get("/klasifikasi")
def get_all_data():
    db = SessionLocal()
    records = db.query(Klasifikasi).order_by(Klasifikasi.id.desc()).all()
    db.close()

    result = [
        {
            "id": r.id,
            "path": r.path,
            "hasil": "Sehat" if r.hasil == 1 else "Sakit",
            "created_at": str(r.created_at),
            "updated_at": str(r.updated_at)
        }
        for r in records
    ]
    return {"data": result}

# =================================
# ENDPOINT GET HASIL BY ID PATH NEW
# =================================
@app.post("/hasil")
async def post_hasil(
    hasil: int = Form(...)
):
    try:
        # Validasi hasil (hanya 0 atau 1)
        if hasil not in [0, 1]:
            return JSONResponse(
                content={"error": "Nilai hasil hanya boleh 0 (Sakit) atau 1 (Sehat)"},
                status_code=400
            )

        db = SessionLocal()
        last_data = db.query(Klasifikasi).order_by(Klasifikasi.id.desc()).first()
        if not last_data:
            db.close()
            return JSONResponse(
                content={"error": f"Data dengan id {id} tidak ditemukan"},
                status_code=404
            )

        last_data.hasil = hasil
        db.commit()
        db.refresh(last_data)
        db.close()

        return JSONResponse(content={
            "message": "Hasil klasifikasi berhasil disimpan",
            "data": {
                "id": last_data.id,
                "path": last_data.path,
                "hasil": "Sehat" if last_data.hasil == 1 else "Sakit",
                "created_at": str(last_data.created_at),
                "updated_at": str(last_data.updated_at)
            }
        })
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


# ======================
# GET PATH TERBARU
# ======================
@app.get("/path_terbaru")
def get_path_terbaru():
    db = SessionLocal()
    latest_data = db.query(Klasifikasi).order_by(Klasifikasi.updated_at.desc()).first()
    db.close()

    if not latest_data:
        return JSONResponse(content={"error": "Belum ada data"}, status_code=404)

    return {"path": latest_data.path}


# ======================
# GET HASIL TERBARU
# ======================
@app.get("/hasil_terbaru")
def get_hasil_terbaru():
    db = SessionLocal()
    latest_data = db.query(Klasifikasi).order_by(Klasifikasi.updated_at.desc()).first()
    db.close()

    if not latest_data:
        return JSONResponse(content={"error": "Belum ada data"}, status_code=404)

    hasil_label = (
        "Sehat" if latest_data.hasil == 1
        else "Sakit" if latest_data.hasil == 0
        else None
    )

    return {"hasil": hasil_label}


# ======================
# GET WAKTU TERBARU
# ======================
@app.get("/waktu_terbaru")
def get_waktu_terbaru():
    db = SessionLocal()
    latest_data = db.query(Klasifikasi).order_by(Klasifikasi.updated_at.desc()).first()
    db.close()

    if not latest_data:
        return JSONResponse(content={"error": "Belum ada data"}, status_code=404)

    return {"updated_at": str(latest_data.updated_at)}



# ======================
# ENDPOINT ROOT
# ======================
@app.get("/")
def root():
    return {"message": "API Klasifikasi Cabai Aktif!"}
