"""
통합 콘텐츠 생성 API 테스트
전략 → 카피 → 이미지 프롬프트 → 이미지를 한 번에 생성
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"


def test_full_content_generation():
    """통합 콘텐츠 생성 테스트"""
    print("\n" + "="*60)
    print("🧪 통합 콘텐츠 생성 API 테스트")
    print("="*60)

    # 요청 데이터
    request_data = {
        "product_name": "비타민C 브라이트닝 세럼",
        "product_description": "순수 비타민C 20% 고농축 세럼. 피부 톤 개선과 잡티 완화에 효과적입니다.",
        "category": "화장품",
        "target_age": "30대",
        "target_gender": "여성",
        "target_interests": ["뷰티", "스킨케어", "안티에이징"],
        "target_income_level": "중상소득",
        "copy_tone": "professional",
        "save_to_db": False  # 테스트이므로 DB 저장 안 함
    }

    print("\n📤 요청 데이터:")
    print(json.dumps(request_data, ensure_ascii=False, indent=2))

    print("\n⏳ 콘텐츠 생성 중... (예상 시간: 30-40초)")
    print("   1/4 마케팅 전략 생성...")

    start_time = time.time()

    try:
        response = requests.post(
            f"{BASE_URL}/api/content/generate",
            json=request_data,
            timeout=120  # 2분 타임아웃
        )

        elapsed_time = int(time.time() - start_time)

        if response.status_code == 200:
            result = response.json()

            print(f"\n✅ 콘텐츠 생성 완료 (소요 시간: {elapsed_time}초)")
            print("\n" + "="*60)
            print("📊 생성 결과")
            print("="*60)

            # 전략
            print("\n🎯 마케팅 전략:")
            for i, strategy in enumerate(result["data"]["strategies"], 1):
                print(f"  {i}. {strategy['name']}")
                print(f"     핵심 메시지: {strategy['core_message']}")
                print(f"     감성 유형: {strategy['emotion']}")

            print(f"\n   ✓ 선택된 전략: {result['data']['selected_strategy']['name']}")

            # 카피
            print("\n✍️  생성된 카피:")
            copy_data = result["data"]["copy"]
            print(f"   텍스트: {copy_data['text']}")
            print(f"   톤: {copy_data['tone']}")
            print(f"   해시태그: {' '.join(copy_data.get('hashtags', []))}")

            # 이미지
            print("\n🖼️  생성된 이미지:")
            image_data = result["data"]["image"]
            print(f"   프롬프트: {image_data['prompt'][:80]}...")
            print(f"   원본 URL: {image_data['original_url']}")
            if image_data.get('local_url'):
                print(f"   로컬 URL: http://localhost:8000{image_data['local_url']}")
                print(f"   파일 경로: {image_data['file_path']}")

            # 메타데이터
            print("\n📈 메타데이터:")
            print(f"   생성 시간: {result['generation_time']}초")
            if result["data"].get("content_id"):
                print(f"   Content ID: {result['data']['content_id']}")

            print("\n" + "="*60)
            print("✅ 테스트 완료!")
            print("="*60)

            # 이미지 확인 안내
            if image_data.get('local_url'):
                print(f"\n💡 브라우저에서 이미지 확인:")
                print(f"   http://localhost:8000{image_data['local_url']}")

        else:
            print(f"\n❌ 테스트 실패: HTTP {response.status_code}")
            print(f"응답: {response.text}")

    except requests.exceptions.Timeout:
        print("\n❌ 타임아웃: 요청이 2분을 초과했습니다")
    except requests.exceptions.ConnectionError:
        print("\n❌ 연결 실패: 서버가 실행 중인지 확인하세요 (http://localhost:8000)")
    except Exception as e:
        print(f"\n❌ 에러 발생: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 서버 헬스체크
    try:
        health_check = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_check.status_code != 200:
            print("⚠️  서버가 응답하지 않습니다")
            exit(1)
    except:
        print("❌ 서버에 연결할 수 없습니다. 서버를 먼저 시작하세요:")
        print("   cd backend && uvicorn app.main:app --reload")
        exit(1)

    test_full_content_generation()
