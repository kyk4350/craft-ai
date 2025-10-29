"""
Replicate 서비스 테스트 스크립트
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

from app.services.replicate_service import replicate_service


async def test_sdxl_generation():
    """SDXL 이미지 생성 테스트 (개발 모드)"""
    print("\n" + "="*60)
    print("TEST 1: SDXL 이미지 생성 (개발 모드)")
    print("="*60)

    # 간단한 프롬프트로 테스트
    prompt = "A beautiful vitamin C serum bottle on a clean white background, professional product photography, high quality, soft lighting"

    try:
        image_url = await replicate_service.generate_image(
            prompt=prompt,
            width=512,  # 테스트용 작은 크기
            height=512,
            num_outputs=1
        )

        print(f"\n✅ 이미지 생성 완료!")
        print(f"URL: {image_url}")
        print(f"\n브라우저에서 확인: {image_url}")

    except Exception as e:
        print(f"\n❌ 이미지 생성 실패: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """메인 실행 함수"""
    print("\n🧪 Replicate 서비스 테스트 시작")
    print("="*60)

    # SDXL 테스트
    await test_sdxl_generation()

    print("\n" + "="*60)
    print("✅ 테스트 완료!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
