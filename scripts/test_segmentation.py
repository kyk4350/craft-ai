"""
세분화 서비스 테스트 스크립트

사용 예시:
python scripts/test_segmentation.py
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.services.segmentation_service import get_segmentation_service
import json


def print_json(data, title=""):
    """JSON 데이터 예쁘게 출력"""
    if title:
        print(f"\n{'='*60}")
        print(f"{title}")
        print('='*60)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def test_basic_filtering():
    """기본 필터링 테스트"""
    service = get_segmentation_service()

    print("\n" + "="*60)
    print("TEST 1: 10대 여성, 저소득, 패션 관심")
    print("="*60)

    # 필터링
    profiles = service.filter_profiles(
        age_group="10대",
        gender="여성",
        income_level="저소득",
        interests=["패션"],
        limit=5
    )

    print(f"\n매칭된 프로필 수: {len(profiles)}")

    if profiles:
        print("\n첫 번째 프로필 예시:")
        print_json(profiles[0])

        # 인사이트 추출
        print("\n" + "="*60)
        print("타겟 인사이트 분석")
        print("="*60)

        # 전체 매칭 프로필로 인사이트 (limit 없이)
        all_profiles = service.filter_profiles(
            age_group="10대",
            gender="여성",
            income_level="저소득",
            interests=["패션"]
        )

        insights = service.extract_insights(all_profiles)
        print_json(insights)


def test_various_segments():
    """다양한 세그먼트 테스트"""
    service = get_segmentation_service()

    test_cases = [
        {
            "name": "30대 워킹맘 (육아 관심)",
            "filters": {
                "age_group": "30대",
                "gender": "여성",
                "interests": ["육아"]
            }
        },
        {
            "name": "40대 고소득 남성 (골프 관심)",
            "filters": {
                "age_group": "40대",
                "gender": "남성",
                "income_level": "고소득",
                "interests": ["골프"]
            }
        },
        {
            "name": "20대 뷰티 관심자",
            "filters": {
                "age_group": "20대",
                "interests": ["뷰티"]
            }
        }
    ]

    for test_case in test_cases:
        print("\n" + "="*60)
        print(f"TEST: {test_case['name']}")
        print("="*60)

        profiles = service.filter_profiles(**test_case['filters'])
        print(f"매칭된 프로필 수: {len(profiles)}")

        if profiles:
            insights = service.extract_insights(profiles)

            print(f"\n📊 인구통계학:")
            print(f"  - 나이대 분포: {insights['demographics']['age_distribution']}")
            print(f"  - 성별 분포: {insights['demographics']['gender_distribution']}")
            print(f"  - 소득 분포: {insights['demographics']['income_distribution']}")

            print(f"\n🎯 주요 인사이트:")
            recs = insights['marketing_recommendations']
            print(f"  - 주요 나이대: {recs['key_insights']['dominant_age_group']}")
            print(f"  - 주요 관심사: {', '.join(recs['key_insights']['key_interests'][:3])}")
            print(f"  - 주요 고충: {', '.join(recs['key_insights']['key_pain_points'][:3])}")
            print(f"  - 추천 채널: {', '.join(recs['key_insights']['key_channels'])}")

            print(f"\n💡 콘텐츠 전략:")
            print(f"  - 톤앤매너: {recs['content_strategy']['tone_and_manner']}")
            print(f"  - 메시지 전략:")
            for i, strategy in enumerate(recs['content_strategy']['message_strategy'][:3], 1):
                print(f"    {i}. {strategy}")


def test_keyword_search():
    """키워드 검색 테스트"""
    service = get_segmentation_service()

    print("\n" + "="*60)
    print("TEST: 키워드 검색 - '시간 부족'")
    print("="*60)

    profiles = service.search_by_keywords(["시간 부족"], limit=10)
    print(f"매칭된 프로필 수: {len(profiles)}")

    if profiles:
        # 매칭된 프로필의 pain points 출력
        print("\n매칭된 고충들:")
        pain_points_set = set()
        for p in profiles:
            pain_points_set.update(p.get('pain_points', []))

        for pain in sorted(pain_points_set):
            if "시간" in pain:
                print(f"  - {pain}")


def test_all_segments_summary():
    """전체 세그먼트 요약"""
    service = get_segmentation_service()

    print("\n" + "="*60)
    print("전체 세그먼트 요약")
    print("="*60)

    summary = service.get_all_segments()
    print_json(summary, "전체 데이터 요약")


def main():
    """메인 실행 함수"""
    print("\n🎯 세분화 서비스 테스트 시작")
    print("="*60)

    # 1. 전체 요약
    test_all_segments_summary()

    # 2. 기본 필터링 테스트
    test_basic_filtering()

    # 3. 다양한 세그먼트 테스트
    test_various_segments()

    # 4. 키워드 검색 테스트
    test_keyword_search()

    print("\n" + "="*60)
    print("✅ 모든 테스트 완료!")
    print("="*60)


if __name__ == "__main__":
    main()
