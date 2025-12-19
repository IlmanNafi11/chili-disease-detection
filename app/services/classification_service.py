from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models.models import Classification
from ..database import SessionLocal
import logging

logger = logging.getLogger(__name__)

class ClassificationService:
    
    def __init__(self, session: Optional[Session] = None):
        self.session = session or SessionLocal()
    
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
    
    def close(self):
        self.session.close()

def create_classification_service(session: Optional[Session] = None) -> ClassificationService:
    return ClassificationService(session)