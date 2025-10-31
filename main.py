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
    hasil = Column(Integer)  # tinyint(1)
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

# ======================
# ENDPOINT UPLOAD
# ======================
@app.post("/upload")
async def upload_data(
    file: UploadFile = File(...),
    hasil: int = Form(...)
):
    try:
        # Simpan file
        file_location = f"{UPLOAD_DIR}/{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Simpan ke database
        db = SessionLocal()
        new_data = Klasifikasi(path=file_location, hasil=hasil)
        db.add(new_data)
        db.commit()
        db.refresh(new_data)
        db.close()

        return JSONResponse(content={
            "message": "✅ Data berhasil disimpan",
            "data": {
                "id": new_data.id,
                "path": new_data.path,
                "hasil": "Sehat" if new_data.hasil == 1 else "Sakit",
                "created_at": str(new_data.created_at),
                "updated_at": str(new_data.updated_at)
            }
        })
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# ======================
# ENDPOINT GET
# ======================
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

# ======================
# ENDPOINT ROOT
# ======================
@app.get("/")
def root():
    return {"message": "✅ API Klasifikasi Cabai Aktif!"}
