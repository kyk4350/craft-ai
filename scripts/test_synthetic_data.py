"""
합성 데이터 생성 테스트 스크립트
소량의 데이터로 API 테스트
"""

import json
import asyncio
import logging
from pathlib import Path
import sys

# 프로젝트 루트를 Python 경로에 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

# .env 파일 로드
from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / "backend" / ".env")

from app.services.gemini_service import gemini_service
from app.config import settings

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_generate_profiles():
    """
    소량의 프로필 생성 테스트 (5개)
    """
    logger.info("합성 데이터 생성 테스트 시작")
    logger.info(f"Gemini 모델: {settings.GEMINI_MODEL}")

    prompt = """
당신은 마케팅 데이터 전문가입니다.

화장품 카테고리 제품을 구매할 가능성이 있는 다양한 타겟 고객 프로필 5개를 생성해주세요.

각 프로필은 다음 정보를 포함해야 합니다:
- profile_id: 고유 ID (1부터 시작)
- age_group: 연령대 (10대, 20대, 30대, 40대, 50대, 60대 이상)
- gender: 성별 (남성, 여성, 무관)
- income_level: 소득 수준 (저소득, 중소득, 중상소득, 고소득)
- interests: 관심사 리스트 (최소 3개, 최대 5개)
- lifestyle: 라이프스타일 (예: 건강 중시, 트렌디, 실용적, 럭셔리 선호 등)
- pain_points: 불편함/니즈 (2-3개)
- preferred_channels: 선호 채널 (SNS, 검색, TV, 지인 추천 등)

JSON 배열 형식으로만 출력해주세요:
[
  {
    "profile_id": 1,
    "age_group": "20대",
    "gender": "여성",
    "income_level": "중소득",
    "interests": ["뷰티", "헬스케어", "자기계발"],
    "lifestyle": "건강 중시",
    "pain_points": ["피부 트러블", "바쁜 일상"],
    "preferred_channels": ["인스타그램", "유튜브", "네이버 블로그"]
  }
]

JSON만 출력하고 다른 설명은 하지 마세요.
"""

    try:
        logger.info("\nGemini API 호출 중...")
        response = await gemini_service.generate_text(
            prompt=prompt,
            temperature=0.9,
            max_tokens=4000
        )

        logger.info("\n응답 받음. 파싱 중...")
        logger.info(f"응답 길이: {len(response)} 문자")

        # JSON 파싱
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()

        # JSON 로드 시 에러 처리 개선
        try:
            profiles = json.loads(response)
        except json.JSONDecodeError:
            # JSON이 잘렸을 수 있으므로 마지막 객체까지만 파싱 시도
            logger.warning("JSON 파싱 실패, 부분 파싱 시도...")
            # 마지막 완전한 객체를 찾음
            last_bracket = response.rfind("}")
            if last_bracket > 0:
                response = response[:last_bracket+1] + "]"
                profiles = json.loads(response)

        logger.info(f"\n✓ {len(profiles)}개 프로필 생성 성공!")
        logger.info("\n생성된 프로필:")
        for profile in profiles:
            logger.info(f"\n프로필 ID: {profile['profile_id']}")
            logger.info(f"  연령대: {profile['age_group']}")
            logger.info(f"  성별: {profile['gender']}")
            logger.info(f"  소득: {profile['income_level']}")
            logger.info(f"  관심사: {', '.join(profile['interests'])}")
            logger.info(f"  라이프스타일: {profile['lifestyle']}")
            logger.info(f"  Pain Points: {', '.join(profile['pain_points'])}")
            logger.info(f"  선호 채널: {', '.join(profile['preferred_channels'])}")

        # 테스트 결과 저장
        output_path = PROJECT_ROOT / "data" / "processed" / "test_profiles.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(profiles, f, ensure_ascii=False, indent=2)

        logger.info(f"\n✓ 테스트 데이터 저장: {output_path}")
        logger.info("\n테스트 성공! 이제 전체 데이터 생성이 가능합니다.")
        logger.info("실행: python scripts/generate_synthetic_data.py")

    except json.JSONDecodeError as e:
        logger.error(f"\n❌ JSON 파싱 실패: {str(e)}")
        logger.error(f"응답 내용:\n{response}")
    except Exception as e:
        logger.error(f"\n❌ 오류 발생: {str(e)}")


async def main():
    # API 키 확인
    if not settings.GEMINI_API_KEY:
        logger.error("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
        logger.error("backend/.env 파일에 API 키를 추가해주세요.")
        return

    await test_generate_profiles()


if __name__ == "__main__":
    asyncio.run(main())
