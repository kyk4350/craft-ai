"""
실제 사용자 요청 시나리오 테스트

다양한 실제 마케팅 상황을 시뮬레이션하여 세분화 API를 테스트합니다.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"


def print_header(title):
    """섹션 헤더 출력"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def print_result(scenario_num, user_request, response_data):
    """테스트 결과 출력"""
    print(f"\n📝 사용자 요청 #{scenario_num}:")
    print(f'   "{user_request}"')
    print(f"\n✅ API 응답:")
    print(f"   - 매칭된 프로필: {len(response_data['data']['profiles'])}개")

    insights = response_data['data']['insights']
    count = insights['count']

    if count > 0:
        recs = insights['marketing_recommendations']

        print(f"\n📊 타겟 분석:")
        print(f"   - 총 {count}명의 타겟 프로필 발견")
        print(f"   - 주요 나이대: {recs['key_insights']['dominant_age_group']}")
        print(f"   - 주요 소득: {recs['key_insights']['dominant_income_level']}")

        print(f"\n💡 주요 인사이트:")
        print(f"   - 관심사: {', '.join(recs['key_insights']['key_interests'][:5])}")
        print(f"   - 고충: {', '.join(recs['key_insights']['key_pain_points'][:3])}")
        print(f"   - 추천 채널: {', '.join(recs['key_insights']['key_channels'])}")

        print(f"\n✍️ 콘텐츠 전략:")
        print(f"   - 톤앤매너: {recs['content_strategy']['tone_and_manner']}")
        print(f"   - 메시지 전략:")
        for i, strategy in enumerate(recs['content_strategy']['message_strategy'][:2], 1):
            print(f"     {i}. {strategy}")
    else:
        print(f"\n⚠️ 매칭되는 타겟이 없습니다.")


def scenario_1():
    """시나리오 1: 20대 직장인 여성을 위한 간편식 홍보"""
    print_header("시나리오 1: 간편식 브랜드")

    user_request = "바쁜 20대 직장인 여성들을 위한 간편식 제품 마케팅 콘텐츠를 만들고 싶어요"

    payload = {
        "age_group": "20대",
        "gender": "여성",
        "interests": ["간편식", "요리"],
        "category": "식품",
        "limit": 10
    }

    response = requests.post(f"{BASE_URL}/api/segmentation/filter", json=payload)

    if response.status_code == 200:
        print_result(1, user_request, response.json())
    else:
        print(f"❌ Error: {response.status_code}")


def scenario_2():
    """시나리오 2: 50대 남성을 위한 프리미엄 건강기능식품"""
    print_header("시나리오 2: 프리미엄 건강식품 브랜드")

    user_request = "50대 고소득 남성들을 위한 프리미엄 건강기능식품 광고를 만들고 싶습니다"

    payload = {
        "age_group": "50대",
        "gender": "남성",
        "income_level": "고소득",
        "interests": ["건강", "건강 관리"],
        "category": "식품",
        "limit": 10
    }

    response = requests.post(f"{BASE_URL}/api/segmentation/filter", json=payload)

    if response.status_code == 200:
        print_result(2, user_request, response.json())
    else:
        print(f"❌ Error: {response.status_code}")


def scenario_3():
    """시나리오 3: 30대 워킹맘을 위한 시간 절약 가전"""
    print_header("시나리오 3: 스마트 가전 브랜드")

    user_request = "시간이 부족한 30대 워킹맘들에게 시간 절약 가전제품을 소개하고 싶어요"

    # 키워드 검색 사용
    payload = {
        "keywords": ["시간 부족", "육아", "가사"],
        "limit": 15
    }

    response = requests.post(f"{BASE_URL}/api/segmentation/search", json=payload)

    if response.status_code == 200:
        data = response.json()

        # 30대 여성만 필터링
        profiles = [p for p in data['data']['profiles']
                   if p.get('age_group') == '30대' and p.get('gender') == '여성']

        print(f"\n📝 사용자 요청 #3:")
        print(f'   "{user_request}"')
        print(f"\n✅ API 응답:")
        print(f"   - 키워드 매칭: {len(data['data']['profiles'])}개")
        print(f"   - 30대 여성 필터링 후: {len(profiles)}개")

        if profiles:
            # 필터링된 프로필로 인사이트 재추출하기 위해 다시 API 호출
            filter_payload = {
                "age_group": "30대",
                "gender": "여성",
                "interests": ["육아", "가사"],
                "limit": 15
            }
            response2 = requests.post(f"{BASE_URL}/api/segmentation/filter", json=filter_payload)
            if response2.status_code == 200:
                insights = response2.json()['data']['insights']
                recs = insights['marketing_recommendations']

                print(f"\n📊 타겟 분석:")
                print(f"   - 주요 나이대: 30대 워킹맘")
                print(f"   - 핵심 니즈: 시간 절약, 가사 효율화")

                print(f"\n💡 주요 인사이트:")
                print(f"   - 관심사: {', '.join(recs['key_insights']['key_interests'][:5])}")
                print(f"   - 고충: {', '.join(recs['key_insights']['key_pain_points'][:3])}")
                print(f"   - 추천 채널: {', '.join(recs['key_insights']['key_channels'])}")

                print(f"\n✍️ 콘텐츠 전략:")
                print(f"   - 톤앤매너: {recs['content_strategy']['tone_and_manner']}")
    else:
        print(f"❌ Error: {response.status_code}")


def scenario_4():
    """시나리오 4: 대학생을 위한 가성비 뷰티 제품"""
    print_header("시나리오 4: 가성비 뷰티 브랜드")

    user_request = "대학생들을 위한 저렴하면서도 효과 좋은 뷰티 제품 홍보 콘텐츠가 필요해요"

    payload = {
        "age_group": "20대",
        "income_level": "저소득",
        "interests": ["뷰티", "화장품"],
        "category": "화장품",
        "limit": 10
    }

    response = requests.post(f"{BASE_URL}/api/segmentation/filter", json=payload)

    if response.status_code == 200:
        print_result(4, user_request, response.json())
    else:
        print(f"❌ Error: {response.status_code}")


def scenario_5():
    """시나리오 5: 40대 남성을 위한 골프웨어"""
    print_header("시나리오 5: 프리미엄 골프웨어 브랜드")

    user_request = "골프를 즐기는 40대 남성들을 위한 고급 골프웨어 광고를 제작하고 싶습니다"

    payload = {
        "age_group": "40대",
        "gender": "남성",
        "interests": ["골프"],
        "category": "패션",
        "limit": 10
    }

    response = requests.post(f"{BASE_URL}/api/segmentation/filter", json=payload)

    if response.status_code == 200:
        print_result(5, user_request, response.json())
    else:
        print(f"❌ Error: {response.status_code}")


def scenario_6():
    """시나리오 6: 10대를 위한 저렴한 스마트폰 액세서리"""
    print_header("시나리오 6: 모바일 액세서리 브랜드")

    user_request = "용돈이 부족한 10대 청소년들에게 저렴한 스마트폰 액세서리를 판매하고 싶어요"

    payload = {
        "age_group": "10대",
        "income_level": "저소득",
        "interests": ["스마트폰", "디지털 기기"],
        "category": "전자제품",
        "limit": 10
    }

    response = requests.post(f"{BASE_URL}/api/segmentation/filter", json=payload)

    if response.status_code == 200:
        print_result(6, user_request, response.json())
    else:
        print(f"❌ Error: {response.status_code}")


def scenario_7():
    """시나리오 7: 60대 이상을 위한 건강관리 서비스"""
    print_header("시나리오 7: 시니어 헬스케어 서비스")

    user_request = "건강에 관심 많은 시니어 세대를 위한 건강관리 서비스를 소개하고 싶습니다"

    payload = {
        "age_group": "60대 이상",
        "interests": ["건강", "건강 관리"],
        "category": "서비스",
        "limit": 10
    }

    response = requests.post(f"{BASE_URL}/api/segmentation/filter", json=payload)

    if response.status_code == 200:
        print_result(7, user_request, response.json())
    else:
        print(f"❌ Error: {response.status_code}")


def scenario_8():
    """시나리오 8: 자기계발에 관심 있는 30대 직장인"""
    print_header("시나리오 8: 온라인 교육 플랫폼")

    user_request = "커리어 성장을 원하는 30대 직장인들을 위한 온라인 강의 플랫폼을 홍보하려고 합니다"

    payload = {
        "age_group": "30대",
        "interests": ["자기계발", "자기 계발", "커리어"],
        "category": "서비스",
        "limit": 15
    }

    response = requests.post(f"{BASE_URL}/api/segmentation/filter", json=payload)

    if response.status_code == 200:
        print_result(8, user_request, response.json())
    else:
        print(f"❌ Error: {response.status_code}")


def scenario_9():
    """시나리오 9: 비건 트렌드에 관심 있는 20-30대"""
    print_header("시나리오 9: 비건 식품 브랜드")

    user_request = "친환경과 건강을 중시하는 젊은 세대에게 비건 식품을 소개하고 싶어요"

    payload = {
        "keywords": ["비건", "친환경", "건강"],
        "limit": 20
    }

    response = requests.post(f"{BASE_URL}/api/segmentation/search", json=payload)

    if response.status_code == 200:
        data = response.json()
        print(f"\n📝 사용자 요청 #9:")
        print(f'   "{user_request}"')
        print(f"\n✅ API 응답:")
        print(f"   - 비건/친환경 관심층: {len(data['data']['profiles'])}개")

        insights = data['data']['insights']
        if insights['count'] > 0:
            recs = insights['marketing_recommendations']

            print(f"\n📊 타겟 분석:")
            print(f"   - 주요 나이대: {recs['key_insights']['dominant_age_group']}")
            print(f"   - 트렌드: 비건, 친환경, 지속가능성")

            print(f"\n💡 주요 인사이트:")
            print(f"   - 관심사: {', '.join(recs['key_insights']['key_interests'][:5])}")
            print(f"   - 가치관: 환경 보호, 동물 복지, 건강한 라이프스타일")
            print(f"   - 추천 채널: {', '.join(recs['key_insights']['key_channels'])}")
    else:
        print(f"❌ Error: {response.status_code}")


def scenario_10():
    """시나리오 10: 럭셔리 라이프스타일을 추구하는 고소득층"""
    print_header("시나리오 10: 럭셔리 브랜드")

    user_request = "프리미엄 라이프스타일을 추구하는 고소득층을 위한 럭셔리 제품 마케팅이 필요합니다"

    payload = {
        "income_level": "고소득",
        "interests": ["럭셔리", "명품", "프리미엄"],
        "limit": 15
    }

    response = requests.post(f"{BASE_URL}/api/segmentation/filter", json=payload)

    if response.status_code == 200:
        print_result(10, user_request, response.json())
    else:
        print(f"❌ Error: {response.status_code}")


def main():
    """메인 실행 함수"""
    print("\n" + "🎯"*40)
    print("       실제 사용자 시나리오 기반 세분화 API 테스트")
    print("🎯"*40)

    try:
        # 서버 연결 확인
        print("\n서버 연결 확인 중...")
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print("✅ 서버 연결 성공!")
        else:
            print("❌ 서버 응답 오류")
            return
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다.")
        print("서버를 먼저 시작하세요: cd backend && uvicorn app.main:app --reload")
        return

    # 각 시나리오 실행
    scenarios = [
        scenario_1,   # 20대 직장인 여성 - 간편식
        scenario_2,   # 50대 고소득 남성 - 건강식품
        scenario_3,   # 30대 워킹맘 - 시간 절약 가전
        scenario_4,   # 대학생 - 가성비 뷰티
        scenario_5,   # 40대 남성 - 골프웨어
        scenario_6,   # 10대 - 저렴한 액세서리
        scenario_7,   # 60대 이상 - 건강관리 서비스
        scenario_8,   # 30대 직장인 - 온라인 교육
        scenario_9,   # 비건 트렌드 - 젊은 세대
        scenario_10,  # 고소득층 - 럭셔리 브랜드
    ]

    for i, scenario_func in enumerate(scenarios, 1):
        scenario_func()
        if i < len(scenarios):
            time.sleep(0.5)  # API 부하 방지

    print("\n" + "="*80)
    print("  ✅ 모든 시나리오 테스트 완료!")
    print("="*80)
    print("\n📌 요약:")
    print("   - 10가지 실제 마케팅 시나리오 테스트 완료")
    print("   - 다양한 연령대/소득/관심사별 타겟 분석")
    print("   - 각 타겟에 맞는 콘텐츠 전략 자동 생성")
    print("   - 톤앤매너, 채널, 메시지 전략 추천 확인")
    print("\n")


if __name__ == "__main__":
    main()
