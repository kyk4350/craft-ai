"""
성별 필터링 로직 테스트 (무관 포함 확인)
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.services.segmentation_service import get_segmentation_service


def test_gender_filter():
    """성별 필터링 테스트"""
    service = get_segmentation_service()

    print("\n" + "="*80)
    print("성별 필터링 로직 테스트 (무관 포함 여부 확인)")
    print("="*80)

    # 테스트 1: 20대 식품 카테고리 - 성별 지정 안 함
    print("\n[테스트 1] 20대 식품 - 성별 지정 안 함")
    print("-" * 80)
    profiles_all = service.filter_profiles(
        age_group="20대",
        category="식품"
    )

    from collections import Counter
    gender_dist_all = Counter([p['gender'] for p in profiles_all])

    print(f"결과: 총 {len(profiles_all)}개")
    print(f"  - 여성: {gender_dist_all.get('여성', 0)}개")
    print(f"  - 남성: {gender_dist_all.get('남성', 0)}개")
    print(f"  - 무관: {gender_dist_all.get('무관', 0)}개")
    print(f"✅ 예상: 모든 성별 포함")

    # 테스트 2: 20대 식품 - 여성만
    print("\n[테스트 2] 20대 식품 - 여성만")
    print("-" * 80)
    profiles_female = service.filter_profiles(
        age_group="20대",
        category="식품",
        gender="여성"
    )

    gender_dist_female = Counter([p['gender'] for p in profiles_female])

    print(f"결과: 총 {len(profiles_female)}개")
    print(f"  - 여성: {gender_dist_female.get('여성', 0)}개")
    print(f"  - 남성: {gender_dist_female.get('남성', 0)}개")
    print(f"  - 무관: {gender_dist_female.get('무관', 0)}개")

    if gender_dist_female.get('무관', 0) > 0:
        print(f"✅ 성공: 여성 + 무관 포함 (총 {len(profiles_female)}개)")
    else:
        print(f"❌ 실패: 무관이 포함되지 않음")

    # 테스트 3: 20대 식품 - 남성만
    print("\n[테스트 3] 20대 식품 - 남성만")
    print("-" * 80)
    profiles_male = service.filter_profiles(
        age_group="20대",
        category="식품",
        gender="남성"
    )

    gender_dist_male = Counter([p['gender'] for p in profiles_male])

    print(f"결과: 총 {len(profiles_male)}개")
    print(f"  - 여성: {gender_dist_male.get('여성', 0)}개")
    print(f"  - 남성: {gender_dist_male.get('남성', 0)}개")
    print(f"  - 무관: {gender_dist_male.get('무관', 0)}개")

    if gender_dist_male.get('무관', 0) > 0:
        print(f"✅ 성공: 남성 + 무관 포함 (총 {len(profiles_male)}개)")
    else:
        print(f"❌ 실패: 무관이 포함되지 않음")

    # 테스트 4: 실제 사용 예시
    print("\n[테스트 4] 실제 사용 예시: 30대 워킹맘 타겟")
    print("-" * 80)
    profiles_mom = service.filter_profiles(
        age_group="30대",
        gender="여성",
        interests=["육아"]
    )

    gender_dist_mom = Counter([p['gender'] for p in profiles_mom])

    print(f'사용자 요청: "30대 워킹맘을 위한 마케팅 콘텐츠"')
    print(f"결과: 총 {len(profiles_mom)}개")
    print(f"  - 여성: {gender_dist_mom.get('여성', 0)}개")
    print(f"  - 무관: {gender_dist_mom.get('무관', 0)}개")

    if gender_dist_mom.get('무관', 0) > 0:
        print(f"✅ 육아 관심사는 남녀 모두 해당될 수 있으므로 무관 포함됨")

    # 인사이트 출력
    insights = service.extract_insights(profiles_mom)
    recs = insights['marketing_recommendations']
    print(f"\n📊 타겟 인사이트:")
    print(f"  - 주요 고충: {', '.join(recs['key_insights']['key_pain_points'][:3])}")
    print(f"  - 추천 채널: {', '.join(recs['key_insights']['key_channels'])}")

    # 최종 요약
    print("\n" + "="*80)
    print("✅ 테스트 완료")
    print("="*80)
    print("\n📌 결론:")
    print(f"  - 성별 미지정: 전체 ({len(profiles_all)}개)")
    print(f"  - 여성 지정: 여성 + 무관 ({len(profiles_female)}개)")
    print(f"  - 남성 지정: 남성 + 무관 ({len(profiles_male)}개)")
    print(f"\n💡 무관 프로필은 성별 구분 없이 모두에게 적용 가능한 타겟입니다.")


if __name__ == "__main__":
    test_gender_filter()
