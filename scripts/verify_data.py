"""
데이터 검증 스크립트
다운로드된 Kaggle 데이터셋을 분석하고 품질을 확인
"""

import pandas as pd
import os
from pathlib import Path

# 프로젝트 루트 디렉토리
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"


def verify_ifood_data():
    """
    iFood 마케팅 데이터 검증
    """
    print("\n=== iFood Marketing Data 검증 ===")

    file_path = DATA_RAW_DIR / "ifood_df.csv"
    if not file_path.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
        return None

    df = pd.read_csv(file_path)

    print(f"✓ 데이터 로드 성공")
    print(f"  - 행 개수: {len(df):,}")
    print(f"  - 열 개수: {len(df.columns)}")

    print(f"\n✓ 컬럼 목록 ({len(df.columns)}개):")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i:2d}. {col}")

    print(f"\n✓ 데이터 타입:")
    print(df.dtypes)

    print(f"\n✓ 결측치 확인:")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_df = pd.DataFrame({
        '결측치': missing,
        '비율(%)': missing_pct
    })
    missing_df = missing_df[missing_df['결측치'] > 0]
    if len(missing_df) > 0:
        print(missing_df)
    else:
        print("  결측치 없음")

    print(f"\n✓ 기본 통계:")
    print(df.describe())

    print(f"\n✓ 샘플 데이터 (첫 3행):")
    print(df.head(3))

    return df


def verify_customer_data():
    """
    고객 세분화 데이터 검증
    """
    print("\n=== Customer Segmentation Data 검증 ===")

    file_path = DATA_RAW_DIR / "Mall_Customers.csv"
    if not file_path.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
        return None

    df = pd.read_csv(file_path)

    print(f"✓ 데이터 로드 성공")
    print(f"  - 행 개수: {len(df):,}")
    print(f"  - 열 개수: {len(df.columns)}")

    print(f"\n✓ 컬럼 목록:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. {col}")

    print(f"\n✓ 데이터 타입:")
    print(df.dtypes)

    print(f"\n✓ 결측치 확인:")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_df = pd.DataFrame({
        '결측치': missing,
        '비율(%)': missing_pct
    })
    missing_df = missing_df[missing_df['결측치'] > 0]
    if len(missing_df) > 0:
        print(missing_df)
    else:
        print("  결측치 없음")

    print(f"\n✓ 기본 통계:")
    print(df.describe())

    print(f"\n✓ 성별 분포:")
    if 'Gender' in df.columns:
        print(df['Gender'].value_counts())

    print(f"\n✓ 샘플 데이터 (첫 5행):")
    print(df.head())

    return df


def analyze_data_quality():
    """
    데이터 품질 분석 및 사용 가능성 평가
    """
    print("\n" + "="*50)
    print("데이터 품질 분석 결과")
    print("="*50)

    ifood_df = verify_ifood_data()
    customer_df = verify_customer_data()

    print("\n" + "="*50)
    print("종합 평가")
    print("="*50)

    if ifood_df is not None:
        print("\n✓ iFood 데이터:")
        print(f"  - 마케팅 캠페인 응답 데이터 포함")
        print(f"  - 고객 구매 이력 데이터 포함")
        print(f"  - 인구통계 정보 포함 (연령, 수입, 교육 등)")
        print(f"  - 사용 가능: ✓ 합성 데이터 생성 시 참고용으로 적합")

    if customer_df is not None:
        print("\n✓ Customer Segmentation 데이터:")
        print(f"  - 고객 세분화에 필요한 기본 정보 포함")
        print(f"  - 데이터 양이 적음 ({len(customer_df)}행)")
        print(f"  - 사용 가능: ✓ 세분화 알고리즘 테스트용으로 적합")

    print("\n✓ 다음 단계:")
    print("  1. Gemini API로 합성 데이터 생성 (1,000+ 프로필)")
    print("  2. 기존 데이터 패턴을 참고하여 다양한 타겟 프로필 생성")
    print("  3. 생성된 데이터를 data/processed/ 에 저장")


if __name__ == "__main__":
    analyze_data_quality()
