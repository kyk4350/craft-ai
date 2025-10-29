"""
이미지 생성 + 스토리지 통합 테스트
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


async def test_generate_and_save():
    """이미지 생성 및 로컬 저장 테스트"""
    print("\n" + "="*60)
    print("TEST: 이미지 생성 + 로컬 저장")
    print("="*60)

    prompt = "A beautiful vitamin C serum bottle on a clean white background, professional product photography, high quality, soft lighting"

    try:
        result = await replicate_service.generate_image(
            prompt=prompt,
            width=512,
            height=512,
            save_local=True  # 로컬 저장 활성화
        )

        print(f"\n✅ 이미지 생성 및 저장 완료!")
        print(f"\n결과:")
        print(f"  - 원본 URL: {result['original_url']}")

        if 'local_url' in result:
            print(f"  - 로컬 URL: {result['local_url']}")
            print(f"  - 파일 경로: {result['file_path']}")
            print(f"\n로컬 이미지 확인: http://localhost:8000{result['local_url']}")
        else:
            print(f"  ⚠️  로컬 저장 실패")

    except Exception as e:
        print(f"\n❌ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """메인 실행 함수"""
    print("\n🧪 이미지 생성 + 스토리지 테스트 시작")
    print("="*60)

    await test_generate_and_save()

    print("\n" + "="*60)
    print("✅ 테스트 완료!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
