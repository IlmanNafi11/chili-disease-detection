from sqlalchemy.orm import Session
from .database import SessionLocal
from typing import Generator, Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self._session_factory = SessionLocal
    
    def get_session(self) -> Generator[Session, None, None]:
        db = self._session_factory()
        try:
            yield db
        except Exception as e:
            logger.error(f"Database session error: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    def create_session(self) -> Session:
        return self._session_factory()
    
    def close_all_sessions(self):
        self._session_factory.close_all()

db_manager = DatabaseManager()

def get_db_session() -> Generator[Session, None, None]:
    yield from db_manager.get_session()

def create_database_session() -> Session:
    return db_manager.create_session()