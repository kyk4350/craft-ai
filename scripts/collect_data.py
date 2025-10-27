"""
데이터 수집 스크립트
Kaggle 데이터 다운로드 및 정리
"""

import os
import subprocess
from pathlib import Path
import shutil


# 프로젝트 루트 디렉토리
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"


def download_kaggle_dataset(dataset_id: str, dataset_name: str) -> bool:
    """
    Kaggle 데이터셋 다운로드

    Args:
        dataset_id: Kaggle 데이터셋 ID (예: jackdaoud/marketing-data)
        dataset_name: 저장할 파일명 (예: marketing_data)

    Returns:
        성공 여부
    """
    print(f"\n다운로드 중: {dataset_id}")

    try:
        # Kaggle API로 다운로드
        cmd = f"kaggle datasets download -d {dataset_id} -p {DATA_RAW_DIR}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ 다운로드 실패: {result.stderr}")
            return False

        print(f"✓ 다운로드 완료: {dataset_id}")

        # ZIP 파일 압축 해제
        zip_files = list(DATA_RAW_DIR.glob("*.zip"))
        for zip_file in zip_files:
            print(f"압축 해제 중: {zip_file.name}")
            shutil.unpack_archive(zip_file, DATA_RAW_DIR)
            zip_file.unlink()  # ZIP 파일 삭제
            print(f"✓ 압축 해제 완료")

        return True

    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return False


def collect_all_datasets():
    """
    필요한 모든 데이터셋 수집
    """
    print("="*50)
    print("Kaggle 데이터셋 수집 시작")
    print("="*50)

    # 데이터 디렉토리 생성
    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)

    # 수집할 데이터셋 목록
    datasets = [
        {
            "id": "jackdaoud/marketing-data",
            "name": "marketing_data",
            "description": "마케팅 캠페인 데이터 (iFood)"
        },
        {
            "id": "vjchoudhary7/customer-segmentation-tutorial-in-python",
            "name": "customer_segmentation",
            "description": "고객 세분화 데이터"
        }
    ]

    success_count = 0

    for dataset in datasets:
        print(f"\n[{dataset['description']}]")
        if download_kaggle_dataset(dataset["id"], dataset["name"]):
            success_count += 1

    print("\n" + "="*50)
    print(f"수집 완료: {success_count}/{len(datasets)} 데이터셋")
    print("="*50)

    # 다운로드된 파일 목록
    print("\n다운로드된 파일:")
    for file in sorted(DATA_RAW_DIR.glob("*.csv")):
        file_size = file.stat().st_size / 1024  # KB
        print(f"  - {file.name} ({file_size:.1f} KB)")


def clean_raw_data():
    """
    Raw 데이터 정리 (불필요한 파일 삭제)
    """
    print("\n데이터 정리 중...")

    # ZIP 파일 삭제
    zip_files = list(DATA_RAW_DIR.glob("*.zip"))
    for zip_file in zip_files:
        zip_file.unlink()
        print(f"✓ 삭제: {zip_file.name}")

    print("✓ 정리 완료")


if __name__ == "__main__":
    collect_all_datasets()
    clean_raw_data()

    print("\n다음 단계:")
    print("  python scripts/verify_data.py  # 데이터 검증")
