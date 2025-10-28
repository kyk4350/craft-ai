"""
Replicate API 연결 테스트 스크립트

Replicate API 토큰이 제대로 설정되었는지 확인하고,
SDXL 모델을 사용해 간단한 테스트 이미지를 생성합니다.
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트를 PYTHONPATH에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "backend"))

from dotenv import load_dotenv
import replicate

# .env 파일 로드
env_path = project_root / "backend" / ".env"
load_dotenv(env_path)

def test_replicate_connection():
    """Replicate API 연결 테스트"""

    print("=" * 60)
    print("Replicate API 연결 테스트")
    print("=" * 60)

    # 1. API 토큰 확인
    api_token = os.getenv("REPLICATE_API_TOKEN")
    if not api_token:
        print("❌ REPLICATE_API_TOKEN이 .env 파일에 없습니다")
        print(f"   .env 파일 위치: {env_path}")
        return False

    print(f"✅ REPLICATE_API_TOKEN 확인: {api_token[:15]}...")
    print()

    # 2. Replicate 클라이언트 테스트 - 모델 정보 가져오기
    try:
        print("📡 Replicate API 연결 테스트 중...")

        # 간단한 API 호출로 연결 테스트
        # SDXL 모델로 매우 간단한 이미지 생성 (빠르고 저렴)
        print("🎨 SDXL 모델로 테스트 이미지 생성 중...")
        print("   프롬프트: 'a simple red circle on white background'")
        print("   예상 비용: $0.012")

        output = replicate.run(
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input={
                "prompt": "a simple red circle on white background",
                "width": 512,  # 작은 크기로 빠르게 테스트
                "height": 512,
                "num_outputs": 1,
                "num_inference_steps": 20  # 적은 스텝으로 빠르게
            }
        )

        if output:
            image_url = output[0] if isinstance(output, list) else output
            print(f"✅ 이미지 생성 성공!")
            print(f"   이미지 URL: {image_url}")
            print()
            print("=" * 60)
            print("✅ Replicate API 연결 테스트 성공!")
            print("=" * 60)
            return True
        else:
            print("❌ 이미지 생성 실패: 출력 없음")
            return False

    except Exception as e:
        print(f"❌ Replicate API 연결 실패: {e}")
        print()
        print("문제 해결 방법:")
        print("1. REPLICATE_API_TOKEN이 올바른지 확인")
        print("2. Replicate 계정에 크레딧이 있는지 확인")
        print("3. 인터넷 연결 확인")
        return False

if __name__ == "__main__":
    success = test_replicate_connection()
    sys.exit(0 if success else 1)
