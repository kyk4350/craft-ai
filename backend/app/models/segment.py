"""
Segment 모델
사용자가 자주 사용하는 타겟 세분화 필터 조합을 저장
"""

from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin
from datetime import datetime


class Segment(Base, TimestampMixin):
    """
    타겟 세분화 결과 캐싱 모델

    자주 사용하는 필터 조합과 그 결과를 영구 저장하여
    Redis 캐시가 만료된 후에도 빠른 조회 가능
    """
    __tablename__ = "segments"

    id = Column(Integer, primary_key=True, index=True)

    # 세그먼트 식별
    name = Column(String(200), nullable=True, index=True, comment="세그먼트 이름 (예: MZ세대 뷰티 관심자)")

    # 필터 조건 (JSON)
    filter_conditions = Column(JSON, nullable=False, comment="필터 조건 (age_group, gender, interests 등)")

    # 캐싱된 결과
    cached_profile_ids = Column(JSON, nullable=False, comment="매칭된 Target 프로필 ID 목록")
    profile_count = Column(Integer, nullable=False, default=0, comment="매칭된 프로필 수")

    # 메타데이터
    last_accessed_at = Column(DateTime, nullable=True, comment="마지막 접근 시간")
    access_count = Column(Integer, default=0, comment="접근 횟수")

    def __repr__(self):
        return f"<Segment(id={self.id}, name='{self.name}', count={self.profile_count})>"

    def to_dict(self):
        """딕셔너리로 변환"""
        return {
            "id": self.id,
            "name": self.name,
            "filter_conditions": self.filter_conditions,
            "profile_count": self.profile_count,
            "access_count": self.access_count,
            "last_accessed_at": self.last_accessed_at.isoformat() if self.last_accessed_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    def update_access(self):
        """접근 정보 업데이트"""
        self.last_accessed_at = datetime.utcnow()
        self.access_count += 1
