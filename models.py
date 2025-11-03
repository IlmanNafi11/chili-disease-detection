from sqlalchemy import Column, Integer, Float, String, DateTime, func
from database import Base

class Classification(Base):
    __tablename__ = "classifications"
    
    id = Column(String(255), primary_key=True, index=True)
    hasil = Column(Integer, nullable=False)
    path = Column(String(500), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

