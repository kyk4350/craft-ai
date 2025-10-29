"""
Performance model for content analytics
"""

from sqlalchemy import Column, Integer, Float, String, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base, TimestampMixin


class DataSource(str, enum.Enum):
    """데이터 출처"""
    AI_SIMULATION = "ai_simulation"  # AI 시뮬레이션
    REAL_DATA = "real_data"  # 실제 추적 데이터


class Performance(Base, TimestampMixin):
    """콘텐츠 성과 데이터 모델"""

    __tablename__ = "performances"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("contents.id", ondelete="CASCADE"), nullable=False, index=True)

    # 데이터 출처
    data_source = Column(SQLEnum(DataSource), default=DataSource.AI_SIMULATION, nullable=False)

    # 성과 지표
    impressions = Column(Integer, default=0)  # 노출 수
    clicks = Column(Integer, default=0)  # 클릭 수
    ctr = Column(Float, default=0.0)  # 클릭률 (%)
    engagement_rate = Column(Float, default=0.0)  # 참여도 (%)
    conversion_rate = Column(Float, default=0.0)  # 전환율 (%)
    brand_recall_score = Column(Float, default=0.0)  # 브랜드 기억도 (0-100)

    # 타겟별 세부 성과 (JSON)
    target_breakdown = Column(JSON)  # {"20대 여성": {"ctr": 8.5, ...}, ...}

    # AI 시뮬레이션 데이터
    personas_data = Column(JSON)  # 페르소나 정보 및 반응
    confidence_score = Column(Float)  # AI 예측 신뢰도 (0-1)

    # 실제 데이터 추적 정보
    tracking_url = Column(String(500))  # 추적 URL
    campaign_start_date = Column(String(50))  # 캠페인 시작일
    campaign_end_date = Column(String(50))  # 캠페인 종료일

    # Relationships
    content = relationship("Content", backref="performances")

    def __repr__(self):
        return f"<Performance(id={self.id}, content_id={self.content_id}, source='{self.data_source}', ctr={self.ctr}%)>"
