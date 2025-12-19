from sqlalchemy import Column, String, Boolean, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from ..database import Base
import datetime

class Classification(Base):
    __tablename__ = 'classifications'
    
    id = Column(String(length=255), primary_key=True, nullable=False)
    hasil = Column(Boolean(), nullable=False)
    path = Column(String(length=500), nullable=False)
    created_at = Column(DateTime(), server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    updated_at = Column(DateTime(), server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)
