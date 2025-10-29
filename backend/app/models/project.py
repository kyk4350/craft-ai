"""
Project model
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class Project(Base, TimestampMixin):
    """프로젝트 모델 - 마케팅 캠페인/프로젝트"""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    product_name = Column(String(200))
    product_category = Column(String(100))  # 화장품, 식품, 패션, 전자제품, 서비스

    # Relationships
    user = relationship("User", back_populates="projects")
    contents = relationship("Content", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', category='{self.product_category}')>"
