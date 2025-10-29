"""
Gemini API를 활용한 합성 타겟 데이터 생성
1,000+ 다양한 타겟 프로필 생성
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

from app.services.gemini_service import gemini_service
from app.config import settings

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 출력 디렉토리
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


async def generate_target_profiles(
    category: str,
    count: int = 50
) -> List[Dict]:
    """
    특정 카테고리에 대한 타겟 프로필 생성

    Args:
        category: 제품 카테고리 (화장품, 식품, 패션, 전자제품, 서비스)
        count: 생성할 프로필 수

    Returns:
        타겟 프로필 리스트
    """
    logger.info(f"카테고리 '{category}' 타겟 프로필 {count}개 생성 중...")

    prompt = f"""
당신은 마케팅 데이터 전문가입니다.

{category} 카테고리 제품을 구매할 가능성이 있는 다양한 타겟 고객 프로필 {count}개를 생성해주세요.

각 프로필은 다음 정보를 포함해야 합니다:
- profile_id: 고유 ID (1부터 시작)
- age_group: 연령대 (10대, 20대, 30대, 40대, 50대, 60대 이상)
- gender: 성별 (남성, 여성, 무관)
- income_level: 소득 수준 (저소득, 중소득, 중상소득, 고소득)
- interests: 관심사 리스트 (최소 3개, 최대 5개)
- lifestyle: 라이프스타일 (예: 건강 중시, 트렌디, 실용적, 럭셔리 선호 등)
- pain_points: 불편함/니즈 (2-3개)
- preferred_channels: 선호 채널 (SNS, 검색, TV, 지인 추천 등)

⚠️ 중요한 규칙:
1. 성별 분포: 남성 40%, 여성 40%, 무관 20% 비율로 균형있게 배치
2. 스테레오타입 피하기:
   - 남성도 뷰티, 패션, 육아에 관심 가질 수 있음
   - 여성도 게임, IT, 스포츠에 관심 가질 수 있음
   - 성별 무관은 정말 성별 구분이 의미 없는 경우만 (예: 건강식품, 가전제품)
3. 다양성 극대화:
   - 같은 나이대/성별이라도 완전히 다른 관심사 조합
   - 연령대를 고르게 분포
   - 소득 수준을 다양하게

JSON 배열 형식으로만 출력해주세요:
[
  {{
    "profile_id": 1,
    "age_group": "20대",
    "gender": "여성",
    "income_level": "중소득",
    "interests": ["뷰티", "헬스케어", "자기계발"],
    "lifestyle": "건강 중시",
    "pain_points": ["피부 트러블", "바쁜 일상"],
    "preferred_channels": ["인스타그램", "유튜브", "네이버 블로그"]
  }}
]

JSON만 출력하고 다른 설명은 하지 마세요.
"""

    try:
        response = await gemini_service.generate_text(
            prompt=prompt,
            temperature=0.9,  # 높은 창의성
            max_tokens=8000
        )

        # JSON 파싱
        # Gemini가 ```json ``` 으로 감쌀 수 있으므로 제거
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()

        profiles = json.loads(response)
        logger.info(f"✓ {len(profiles)}개 프로필 생성 완료")

        return profiles

    except json.JSONDecodeError as e:
        logger.error(f"JSON 파싱 실패: {str(e)}")
        logger.error(f"응답 내용: {response[:500]}")
        return []
    except Exception as e:
        logger.error(f"프로필 생성 실패: {str(e)}")
        return []


async def generate_all_categories():
    """
    모든 카테고리에 대한 타겟 프로필 생성
    """
    logger.info("="*60)
    logger.info("합성 타겟 데이터 생성 시작")
    logger.info("="*60)

    # 카테고리별 생성 수
    categories = {
        "화장품": 200,
        "식품": 200,
        "패션": 200,
        "전자제품": 200,
        "서비스": 200
    }

    all_profiles = []

    for category, count in categories.items():
        logger.info(f"\n[{category}] 카테고리 처리 중...")

        # 10개씩 나눠서 생성 (JSON 응답 길이 제한 고려)
        batch_size = 10
        category_profiles = []

        for i in range(0, count, batch_size):
            batch_count = min(batch_size, count - i)
            logger.info(f"  배치 {i//batch_size + 1}: {batch_count}개 생성 중...")

            profiles = await generate_target_profiles(category, batch_count)

            if profiles:
                # profile_id를 전체 기준으로 재조정
                for profile in profiles:
                    profile["profile_id"] = len(all_profiles) + len(category_profiles) + 1
                    profile["category"] = category

                category_profiles.extend(profiles)

                # API Rate Limit 고려 (15 RPM)
                logger.info(f"  API 제한 대기 중 (5초)...")
                await asyncio.sleep(5)
            else:
                logger.warning(f"  배치 {i//batch_size + 1} 생성 실패")

        logger.info(f"✓ {category}: {len(category_profiles)}개 생성 완료")
        all_profiles.extend(category_profiles)

    return all_profiles


def save_profiles(profiles: List[Dict], filename: str = "target_profiles.json"):
    """
    생성된 프로필 저장

    Args:
        profiles: 프로필 리스트
        filename: 저장할 파일명
    """
    output_path = OUTPUT_DIR / filename

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(profiles, f, ensure_ascii=False, indent=2)

    logger.info(f"\n✓ 저장 완료: {output_path}")
    logger.info(f"  - 총 프로필 수: {len(profiles):,}개")

    # 카테고리별 통계
    categories = {}
    for profile in profiles:
        cat = profile.get("category", "기타")
        categories[cat] = categories.get(cat, 0) + 1

    logger.info(f"\n카테고리별 분포:")
    for cat, count in sorted(categories.items()):
        logger.info(f"  - {cat}: {count}개")


async def main():
    """
    메인 실행 함수
    """
    # Gemini API 키 확인
    if not settings.GEMINI_API_KEY:
        logger.error("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
        logger.error("backend/.env 파일에 API 키를 추가해주세요.")
        return

    logger.info(f"Gemini 모델: {settings.GEMINI_MODEL}")

    # 프로필 생성
    profiles = await generate_all_categories()

    if profiles:
        # 저장
        save_profiles(profiles)

        logger.info("\n" + "="*60)
        logger.info("합성 데이터 생성 완료")
        logger.info("="*60)
        logger.info(f"생성된 프로필: {len(profiles):,}개")
        logger.info(f"저장 위치: {OUTPUT_DIR / 'target_profiles.json'}")
    else:
        logger.error("\n❌ 프로필 생성 실패")


if __name__ == "__main__":
    asyncio.run(main())
