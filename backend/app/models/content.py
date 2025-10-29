"""
Content model
"""

from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base, TimestampMixin


class ContentStatus(str, enum.Enum):
    """콘텐츠 상태"""
    DRAFT = "draft"  # 임시 저장
    COMPLETED = "completed"  # 생성 완료
    FAILED = "failed"  # 생성 실패


class Content(Base, TimestampMixin):
    """생성된 마케팅 콘텐츠 모델"""

    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)  # 프로젝트 없이도 콘텐츠 생성 가능

    # 타겟 정보 (Target 모델과 직접 관계는 없고 필터링 조건만 저장)
    target_age_group = Column(String(50))
    target_gender = Column(String(20))
    target_income_level = Column(String(50))
    target_interests = Column(JSON)  # 사용자가 선택한 관심사

    # 생성된 콘텐츠
    strategy = Column(JSON)  # 마케팅 전략 (3가지)
    copy_text = Column(Text)  # 카피라이팅
    copy_tone = Column(String(50))  # 프로페셔널, 캐주얼, 임팩트
    hashtags = Column(JSON)  # 해시태그 리스트
    image_prompt = Column(Text)  # 이미지 생성 프롬프트
    image_url = Column(String(500))  # 생성된 이미지 URL
    image_provider = Column(String(50))  # mock, stability, replicate

    # 메타데이터
    status = Column(SQLEnum(ContentStatus), default=ContentStatus.DRAFT, nullable=False)
    generation_time = Column(Integer)  # 생성 시간 (초)
    error_message = Column(Text)  # 실패 시 에러 메시지

    # 성과 예측 (선택적)
    predicted_ctr = Column(String(50))  # 예상 클릭률
    predicted_engagement = Column(String(50))  # 예상 참여도

    # Relationships
    project = relationship("Project", back_populates="contents")

    def __repr__(self):
        return f"<Content(id={self.id}, project_id={self.project_id}, status='{self.status}')>"
