"""
타겟 프로필 데이터를 PostgreSQL 데이터베이스에 임포트
"""

import json
import asyncio
import logging
from pathlib import Path
from typing import List, Dict
import sys

# 프로젝트 루트를 Python 경로에 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

# .env 파일 로드
from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / "backend" / ".env")

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

from app.models.target import Target

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_target_profiles() -> List[Dict]:
    """
    JSON 파일에서 타겟 프로필 로드

    Returns:
        타겟 프로필 리스트
    """
    data_file = PROJECT_ROOT / "data" / "processed" / "target_profiles.json"

    if not data_file.exists():
        logger.error(f"❌ 데이터 파일을 찾을 수 없습니다: {data_file}")
        return []

    with open(data_file, "r", encoding="utf-8") as f:
        profiles = json.load(f)

    logger.info(f"✓ JSON 파일 로드 완료: {len(profiles):,}개 프로필")
    return profiles


def import_to_database(profiles: List[Dict]):
    """
    타겟 프로필을 데이터베이스에 임포트
    기존 데이터를 전부 삭제하고 새로 임포트

    Args:
        profiles: 타겟 프로필 리스트
    """
    # 데이터베이스 연결
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logger.error("❌ DATABASE_URL이 설정되지 않았습니다.")
        return

    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        # 기존 데이터 전부 삭제
        logger.info("기존 타겟 데이터 삭제 중...")
        deleted = session.query(Target).delete()
        session.commit()
        logger.info(f"✓ {deleted}개 기존 데이터 삭제 완료")

        # 새 데이터 삽입
        logger.info(f"\n{len(profiles):,}개 프로필 임포트 중...")

        imported_count = 0
        batch_size = 100

        for i in range(0, len(profiles), batch_size):
            batch = profiles[i:i + batch_size]

            for profile_data in batch:
                target = Target(
                    age_group=profile_data.get("age_group"),
                    gender=profile_data.get("gender"),
                    income_level=profile_data.get("income_level"),
                    category=profile_data.get("category"),
                    interests=profile_data.get("interests", []),
                    pain_points=profile_data.get("pain_points", []),
                    preferred_channels=profile_data.get("preferred_channels", []),
                    lifestyle=profile_data.get("lifestyle")
                )
                session.add(target)
                imported_count += 1

            # 배치 커밋
            session.commit()
            logger.info(f"  진행률: {imported_count:,}/{len(profiles):,} ({imported_count/len(profiles)*100:.1f}%)")

        logger.info(f"\n✓ 총 {imported_count:,}개 프로필 임포트 완료")

        # 통계 출력
        logger.info("\n" + "="*60)
        logger.info("데이터베이스 통계")
        logger.info("="*60)

        # 연령대별 분포
        age_groups = session.execute(
            text("SELECT age_group, COUNT(*) FROM targets GROUP BY age_group ORDER BY age_group")
        ).fetchall()

        logger.info("\n연령대별 분포:")
        for age, count in age_groups:
            logger.info(f"  {age}: {count}개")

        # 성별 분포
        genders = session.execute(
            text("SELECT gender, COUNT(*) FROM targets GROUP BY gender ORDER BY gender")
        ).fetchall()

        logger.info("\n성별 분포:")
        for gender, count in genders:
            logger.info(f"  {gender}: {count}개")

        # 카테고리별 분포
        categories = session.execute(
            text("SELECT category, COUNT(*) FROM targets GROUP BY category ORDER BY category")
        ).fetchall()

        logger.info("\n카테고리별 분포:")
        for category, count in categories:
            logger.info(f"  {category}: {count}개")

        # 10대 성별 분포 (검증용)
        teens_gender = session.execute(
            text("""
                SELECT gender, COUNT(*)
                FROM targets
                WHERE age_group = '10대'
                GROUP BY gender
                ORDER BY gender
            """)
        ).fetchall()

        logger.info("\n10대 성별 분포 (검증):")
        teens_total = sum(count for _, count in teens_gender)
        for gender, count in teens_gender:
            percentage = (count / teens_total * 100) if teens_total > 0 else 0
            logger.info(f"  {gender}: {count}개 ({percentage:.1f}%)")

    except Exception as e:
        logger.error(f"❌ 임포트 실패: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()


def main():
    """
    메인 실행 함수
    """
    logger.info("="*60)
    logger.info("타겟 프로필 데이터베이스 임포트 시작")
    logger.info("="*60)

    # 1. JSON 파일 로드
    profiles = load_target_profiles()

    if not profiles:
        logger.error("❌ 프로필 데이터가 없습니다.")
        return

    # 2. 데이터베이스 임포트
    import_to_database(profiles)

    logger.info("\n" + "="*60)
    logger.info("임포트 완료")
    logger.info("="*60)


if __name__ == "__main__":
    main()
