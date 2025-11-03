from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from models import Classification
from db_session import create_database_session
import logging

logger = logging.getLogger(__name__)

class ClassificationService:
    
    def __init__(self, session: Optional[Session] = None):
        self.session = session or create_database_session()
    
    def create_classification(
        self,
        classification_id: str,
        hasil: int,
        path: str
    ) -> Classification:
        try:
            classification = Classification(
                id=classification_id,
                hasil=hasil,
                path=path
            )
            self.session.add(classification)
            self.session.commit()
            self.session.refresh(classification)
            logger.info(f"Classification created: {classification_id}, hasil: {hasil}")
            return classification
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating classification: {e}")
            raise
    
    def get_classification_by_id(self, classification_id: str) -> Optional[Classification]:
        try:
            return self.session.query(Classification).filter(
                Classification.id == classification_id
            ).first()
        except Exception as e:
            logger.error(f"Error getting classification {classification_id}: {e}")
            return None
    
    def get_all_classifications(
        self, 
        limit: int = 10, 
        offset: int = 0
    ) -> List[Classification]:
        try:
            return self.session.query(Classification).order_by(
                desc(Classification.created_at)
            ).offset(offset).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting classifications: {e}")
            return []
    
    def update_classification(
        self,
        classification_id: str,
        hasil: Optional[int] = None,
        path: Optional[str] = None
    ) -> Optional[Classification]:
        try:
            classification = self.get_classification_by_id(classification_id)
            if not classification:
                return None
            
            if hasil is not None:
                if not isinstance(hasil, int) or hasil not in [0, 1]:
                    raise ValueError("Hasil harus berupa integer 0 (sehat) atau 1 (sakit)")
                classification.hasil = hasil
            
            if path is not None:
                classification.path = path
            
            self.session.commit()
            self.session.refresh(classification)
            logger.info(f"Classification updated: {classification_id}")
            return classification
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating classification {classification_id}: {e}")
            raise
    
    def delete_classification(self, classification_id: str) -> bool:
        try:
            classification = self.get_classification_by_id(classification_id)
            if not classification:
                return False
            
            self.session.delete(classification)
            self.session.commit()
            logger.info(f"Classification deleted: {classification_id}")
            return True
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error deleting classification {classification_id}: {e}")
            raise
    
    def close(self):
        self.session.close()

def create_classification_service(session: Optional[Session] = None) -> ClassificationService:
    return ClassificationService(session)