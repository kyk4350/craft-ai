"""
Gemini 서비스 테스트 스크립트
"""

import sys
from pathlib import Path
import asyncio

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "backend"))

# .env 파일 로드
from dotenv import load_dotenv
load_dotenv(project_root / "backend" / ".env")

from app.services.gemini_service import gemini_service
import json


async def test_strategy_generation():
    """마케팅 전략 생성 테스트"""
    print("\n" + "="*60)
    print("TEST 1: 마케팅 전략 생성")
    print("="*60)

    strategies = await gemini_service.generate_marketing_strategies(
        product_name="비타민C 세럼",
        product_description="피부 톤 개선 및 미백 효과가 있는 고농축 비타민C 세럼",
        category="화장품",
        target_age="20대",
        target_gender="여성",
        target_interests=["뷰티", "스킨케어", "패션"]
    )

    print(f"\n✅ 생성된 전략: {len(strategies)}개\n")
    for strategy in strategies:
        print(f"전략 {strategy.get('id')}: {strategy.get('name')}")
        print(f"  핵심 메시지: {strategy.get('core_message')}")
        print(f"  감성 유형: {strategy.get('emotion')}")
        print(f"  예상 효과: {strategy.get('expected_effect')}")
        print()


async def test_copy_generation():
    """광고 카피 생성 테스트"""
    print("\n" + "="*60)
    print("TEST 2: 광고 카피 생성")
    print("="*60)

    # 테스트용 전략
    test_strategy = {
        "id": 1,
        "name": "감성적 스토리텔링",
        "core_message": "당신의 빛나는 피부, 비타민C와 함께",
        "emotion": "감성적"
    }

    copies = await gemini_service.generate_copies(
        product_name="비타민C 세럼",
        product_description="피부 톤 개선 및 미백 효과가 있는 고농축 비타민C 세럼",
        strategy=test_strategy,
        target_age="20대",
        target_gender="여성",
        target_interests=["뷰티", "스킨케어", "패션"]
    )

    print(f"\n✅ 생성된 카피: {len(copies)}개\n")
    for copy in copies:
        print(f"카피 {copy.get('id')} ({copy.get('tone')}): {copy.get('length')}자")
        print(f"  내용: {copy.get('text')}")
        print(f"  해시태그: {' '.join(copy.get('hashtags', []))}")
        print()


async def test_image_prompt_conversion():
    """이미지 프롬프트 변환 테스트"""
    print("\n" + "="*60)
    print("TEST 3: 이미지 프롬프트 변환")
    print("="*60)

    test_strategy = {
        "id": 1,
        "name": "감성적 스토리텔링",
        "core_message": "당신의 빛나는 피부, 비타민C와 함께"
    }

    image_prompt = await gemini_service.convert_to_image_prompt(
        copy_text="매일 아침, 빛나는 당신의 피부를 만나세요",
        product_name="비타민C 세럼",
        target_age="20대",
        target_gender="여성",
        strategy=test_strategy
    )

    print(f"\n✅ 생성된 이미지 프롬프트:\n")
    print(image_prompt)
    print()


async def main():
    """메인 실행 함수"""
    print("\n🧪 Gemini 서비스 테스트 시작")
    print("="*60)

    try:
        # 1. 전략 생성 테스트
        await test_strategy_generation()

        # 2. 카피 생성 테스트
        await test_copy_generation()

        # 3. 이미지 프롬프트 변환 테스트
        await test_image_prompt_conversion()

        print("\n" + "="*60)
        print("✅ 모든 테스트 완료!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
