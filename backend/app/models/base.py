"""
SQLAlchemy Base class and Database Session
"""

from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import Column, Integer, DateTime, create_engine
from datetime import datetime
from app.config import settings


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


# Database Engine and Session
engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """데이터베이스 세션 Dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
