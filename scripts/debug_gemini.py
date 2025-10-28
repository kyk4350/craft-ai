"""
Gemini API 응답 시간 및 오류 디버깅
"""

import asyncio
import logging
import time
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / "backend" / ".env")

from app.services.gemini_service import gemini_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_small_request():
    """작은 요청 테스트"""
    logger.info("테스트 1: 작은 요청 (10개 프로필)")

    prompt = """
당신은 마케팅 데이터 전문가입니다.

화장품 카테고리 제품을 구매할 가능성이 있는 타겟 고객 프로필 10개를 생성해주세요.

각 프로필: profile_id, age_group, gender, income_level, interests(리스트), lifestyle, pain_points(리스트), preferred_channels(리스트)

JSON 배열 형식으로만 출력하고 다른 설명은 하지 마세요.
"""

    start = time.time()
    try:
        response = await gemini_service.generate_text(
            prompt=prompt,
            temperature=0.9,
            max_tokens=4000
        )
        elapsed = time.time() - start
        logger.info(f"✓ 성공 (소요 시간: {elapsed:.2f}초)")
        logger.info(f"  응답 길이: {len(response)} 문자")
        return True
    except Exception as e:
        elapsed = time.time() - start
        logger.error(f"❌ 실패 (소요 시간: {elapsed:.2f}초)")
        logger.error(f"  오류: {str(e)}")
        return False


async def test_large_request():
    """큰 요청 테스트 (50개)"""
    logger.info("\n테스트 2: 큰 요청 (50개 프로필)")

    prompt = """
당신은 마케팅 데이터 전문가입니다.

화장품 카테고리 제품을 구매할 가능성이 있는 타겟 고객 프로필 50개를 생성해주세요.

각 프로필: profile_id, age_group, gender, income_level, interests(리스트), lifestyle, pain_points(리스트), preferred_channels(리스트)

JSON 배열 형식으로만 출력하고 다른 설명은 하지 마세요.
"""

    start = time.time()
    try:
        response = await gemini_service.generate_text(
            prompt=prompt,
            temperature=0.9,
            max_tokens=16000  # 더 큰 토큰 제한
        )
        elapsed = time.time() - start
        logger.info(f"✓ 성공 (소요 시간: {elapsed:.2f}초)")
        logger.info(f"  응답 길이: {len(response)} 문자")
        return True
    except Exception as e:
        elapsed = time.time() - start
        logger.error(f"❌ 실패 (소요 시간: {elapsed:.2f}초)")
        logger.error(f"  오류: {str(e)}")
        return False


async def main():
    logger.info("="*60)
    logger.info("Gemini API 응답 시간 테스트")
    logger.info("="*60)

    # 작은 요청 테스트
    success1 = await test_small_request()

    await asyncio.sleep(2)

    # 큰 요청 테스트
    success2 = await test_large_request()

    logger.info("\n" + "="*60)
    logger.info("테스트 결과")
    logger.info("="*60)
    logger.info(f"작은 요청 (10개): {'성공' if success1 else '실패'}")
    logger.info(f"큰 요청 (50개): {'성공' if success2 else '실패'}")

    if not success2:
        logger.info("\n권장 사항:")
        logger.info("1. 배치 크기를 10-20개로 줄이기")
        logger.info("2. max_tokens를 충분히 크게 설정 (8000-16000)")
        logger.info("3. 프롬프트를 더 간결하게 수정")


if __name__ == "__main__":
    asyncio.run(main())
