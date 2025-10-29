"""
콘텐츠 생성 API 테스트 스크립트
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_strategy_api():
    """전략 생성 API 테스트"""
    print("\n" + "="*60)
    print("TEST 1: 전략 생성 API")
    print("="*60)

    payload = {
        "product_name": "비타민C 세럼",
        "product_description": "피부 톤 개선 및 미백 효과가 있는 고농축 비타민C 세럼",
        "category": "화장품",
        "target_age": "20대",
        "target_gender": "여성",
        "target_interests": ["뷰티", "스킨케어", "패션"]
    }

    response = requests.post(f"{BASE_URL}/api/content/strategy", json=payload)

    print(f"Status Code: {response.status_code}")
    print(f"\nResponse:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def test_copy_api():
    """카피 생성 API 테스트"""
    print("\n" + "="*60)
    print("TEST 2: 카피 생성 API")
    print("="*60)

    payload = {
        "product_name": "비타민C 세럼",
        "product_description": "피부 톤 개선 및 미백 효과가 있는 고농축 비타민C 세럼",
        "strategy": {
            "id": 1,
            "name": "감성적 스토리텔링",
            "core_message": "당신의 빛나는 피부, 비타민C와 함께",
            "emotion": "감성적",
            "expected_effect": "긍정적인 감성적 연결 형성"
        },
        "target_age": "20대",
        "target_gender": "여성",
        "target_interests": ["뷰티", "스킨케어", "패션"]
    }

    response = requests.post(f"{BASE_URL}/api/content/copy", json=payload)

    print(f"Status Code: {response.status_code}")
    print(f"\nResponse:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def test_image_prompt_api():
    """이미지 프롬프트 생성 API 테스트"""
    print("\n" + "="*60)
    print("TEST 3: 이미지 프롬프트 생성 API")
    print("="*60)

    payload = {
        "copy_text": "매일 아침, 빛나는 당신의 피부를 만나세요",
        "product_name": "비타민C 세럼",
        "target_age": "20대",
        "target_gender": "여성",
        "strategy": {
            "id": 1,
            "name": "감성적 스토리텔링",
            "core_message": "당신의 빛나는 피부, 비타민C와 함께",
            "emotion": "감성적",
            "expected_effect": "긍정적인 감성적 연결 형성"
        }
    }

    response = requests.post(f"{BASE_URL}/api/content/image-prompt", json=payload)

    print(f"Status Code: {response.status_code}")
    print(f"\nResponse:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def main():
    """메인 실행 함수"""
    print("\n🧪 콘텐츠 생성 API 테스트 시작")
    print("="*60)

    try:
        # 서버 헬스 체크
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ 서버가 실행 중이지 않습니다.")
            return

        print("✅ 서버 연결 확인\n")

        # 1. 전략 생성 API 테스트
        test_strategy_api()

        # 2. 카피 생성 API 테스트
        test_copy_api()

        # 3. 이미지 프롬프트 생성 API 테스트
        test_image_prompt_api()

        print("\n" + "="*60)
        print("✅ 모든 API 테스트 완료!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
