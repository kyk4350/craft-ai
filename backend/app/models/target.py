"""
Target model
"""

from sqlalchemy import Column, Integer, String, JSON

from app.models.base import Base, TimestampMixin


class Target(Base, TimestampMixin):
    """타겟 고객 프로필 모델"""

    __tablename__ = "targets"

    id = Column(Integer, primary_key=True, index=True)
    age_group = Column(String(50), index=True)  # 10대, 20대, 30대, 40대, 50대, 60대 이상
    gender = Column(String(20), index=True)  # 남성, 여성, 무관
    income_level = Column(String(50), index=True)  # 저소득, 중소득, 중상소득, 고소득
    category = Column(String(100), index=True)  # 화장품, 식품, 패션, 전자제품, 서비스

    # JSON 타입 필드
    interests = Column(JSON)  # 관심사 리스트 ["뷰티", "패션", ...]
    pain_points = Column(JSON)  # 고충 리스트 ["피부 트러블", "시간 부족", ...]
    preferred_channels = Column(JSON)  # 선호 채널 리스트 ["인스타그램", "유튜브", ...]

    lifestyle = Column(String(500))  # 라이프스타일 설명

    def __repr__(self):
        return f"<Target(id={self.id}, age='{self.age_group}', gender='{self.gender}', category='{self.category}')>"
