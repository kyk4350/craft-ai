"""
세분화 API 엔드포인트 테스트 스크립트
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def print_json(data, title=""):
    """JSON 데이터 예쁘게 출력"""
    if title:
        print(f"\n{'='*60}")
        print(f"{title}")
        print('='*60)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def test_filter_api():
    """필터 API 테스트"""
    print("\n" + "="*60)
    print("TEST 1: POST /api/segmentation/filter")
    print("="*60)

    payload = {
        "age_group": "10대",
        "gender": "여성",
        "income_level": "저소득",
        "interests": ["패션"],
        "limit": 3
    }

    print(f"\nRequest:")
    print_json(payload)

    response = requests.post(
        f"{BASE_URL}/api/segmentation/filter",
        json=payload
    )

    print(f"\nStatus Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Success!")
        print(f"Message: {data['message']}")
        print(f"Profiles Count: {len(data['data']['profiles'])}")

        # 첫 번째 프로필 출력
        if data['data']['profiles']:
            print(f"\n첫 번째 프로필:")
            print_json(data['data']['profiles'][0])

        # 인사이트 출력
        insights = data['data']['insights']
        print(f"\n타겟 인사이트:")
        print(f"  - 톤앤매너: {insights['marketing_recommendations']['content_strategy']['tone_and_manner']}")
        print(f"  - 추천 채널: {', '.join(insights['marketing_recommendations']['key_insights']['key_channels'])}")
    else:
        print(f"\n❌ Error: {response.text}")


def test_summary_api():
    """요약 API 테스트"""
    print("\n" + "="*60)
    print("TEST 2: GET /api/segmentation/summary")
    print("="*60)

    response = requests.get(f"{BASE_URL}/api/segmentation/summary")

    print(f"\nStatus Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Success!")
        summary = data['data']
        print(f"\n전체 요약:")
        print(f"  - 총 프로필 수: {summary['total_profiles']}")
        print(f"  - 나이대 분포: {summary['age_groups']}")
        print(f"  - 성별 분포: {summary['genders']}")
        print(f"  - 소득 분포: {summary['income_levels']}")
        print(f"  - 카테고리 분포: {summary['categories']}")
        print(f"  - 고유 관심사 수: {len(summary['unique_interests'])}")
    else:
        print(f"\n❌ Error: {response.text}")


def test_insights_api():
    """인사이트 API 테스트"""
    print("\n" + "="*60)
    print("TEST 3: GET /api/segmentation/insights")
    print("="*60)

    params = {
        "age_group": "30대",
        "gender": "여성"
    }

    print(f"\nQuery Params: {params}")

    response = requests.get(
        f"{BASE_URL}/api/segmentation/insights",
        params=params
    )

    print(f"\nStatus Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Success!")
        print(f"Message: {data['message']}")

        insights = data['data']
        print(f"\n인사이트:")
        print(f"  - 프로필 수: {insights['count']}")

        recs = insights['marketing_recommendations']
        print(f"  - 주요 나이대: {recs['key_insights']['dominant_age_group']}")
        print(f"  - 주요 관심사: {', '.join(recs['key_insights']['key_interests'][:3])}")
        print(f"  - 주요 고충: {', '.join(recs['key_insights']['key_pain_points'][:3])}")
        print(f"  - 톤앤매너: {recs['content_strategy']['tone_and_manner']}")
    else:
        print(f"\n❌ Error: {response.text}")


def test_search_api():
    """키워드 검색 API 테스트"""
    print("\n" + "="*60)
    print("TEST 4: POST /api/segmentation/search")
    print("="*60)

    payload = {
        "keywords": ["시간 부족", "육아"],
        "limit": 5
    }

    print(f"\nRequest:")
    print_json(payload)

    response = requests.post(
        f"{BASE_URL}/api/segmentation/search",
        json=payload
    )

    print(f"\nStatus Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Success!")
        print(f"Message: {data['message']}")
        print(f"Profiles Count: {len(data['data']['profiles'])}")

        # 인사이트 출력
        insights = data['data']['insights']
        print(f"\n타겟 인사이트:")
        recs = insights['marketing_recommendations']
        print(f"  - 주요 고충: {', '.join(recs['key_insights']['key_pain_points'][:3])}")
        print(f"  - 추천 채널: {', '.join(recs['key_insights']['key_channels'])}")
    else:
        print(f"\n❌ Error: {response.text}")


def main():
    """메인 실행 함수"""
    print("\n🎯 세분화 API 테스트 시작")
    print("="*60)

    try:
        # 1. 필터 API 테스트
        test_filter_api()

        # 2. 요약 API 테스트
        test_summary_api()

        # 3. 인사이트 API 테스트
        test_insights_api()

        # 4. 키워드 검색 API 테스트
        test_search_api()

        print("\n" + "="*60)
        print("✅ 모든 API 테스트 완료!")
        print("="*60)

    except requests.exceptions.ConnectionError:
        print("\n❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
        print("서버 시작: cd backend && uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")


if __name__ == "__main__":
    main()
