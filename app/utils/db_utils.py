from contextlib import contextmanager
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

@contextmanager
def transaction(db: Session):
    """
    Context manager for database transactions.
    Automatically handles commit/rollback.
    """
    try:
        yield
        db.commit()
    except Exception as e:
        logger.error(f"Transaction error, rolling back: {str(e)}")
        db.rollback()
        raise