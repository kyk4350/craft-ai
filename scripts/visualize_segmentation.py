"""
타겟 세분화 데이터 시각화 스크립트

1,000개 합성 타겟 프로필의 분포를 다양한 차트로 시각화합니다.
"""

import sys
from pathlib import Path
import json
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'  # macOS
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지


def load_data():
    """타겟 프로필 데이터 로드"""
    data_path = project_root / "data" / "processed" / "target_profiles.json"
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def plot_age_distribution(profiles):
    """나이대 분포 막대 그래프"""
    age_dist = Counter([p['age_group'] for p in profiles])

    # 순서 정렬
    age_order = ['10대', '20대', '30대', '40대', '50대', '60대 이상', '무관']
    ages = [age for age in age_order if age in age_dist]
    counts = [age_dist[age] for age in ages]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(ages, counts, color='skyblue', edgecolor='navy', alpha=0.7)

    # 막대 위에 값 표시
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}개',
                ha='center', va='bottom')

    plt.title('타겟 프로필 나이대 분포', fontsize=16, fontweight='bold')
    plt.xlabel('나이대', fontsize=12)
    plt.ylabel('프로필 수', fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(project_root / 'data' / 'processed' / 'age_distribution.png', dpi=300)
    print("✅ 나이대 분포 그래프 저장: data/processed/age_distribution.png")


def plot_gender_distribution(profiles):
    """성별 분포 파이 차트"""
    gender_dist = Counter([p['gender'] for p in profiles])

    labels = list(gender_dist.keys())
    sizes = list(gender_dist.values())
    colors = ['#ff9999', '#66b3ff', '#99ff99']
    explode = (0.05, 0.05, 0.05)  # 약간 분리

    plt.figure(figsize=(8, 8))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=90)
    plt.title('타겟 프로필 성별 분포', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(project_root / 'data' / 'processed' / 'gender_distribution.png', dpi=300)
    print("✅ 성별 분포 그래프 저장: data/processed/gender_distribution.png")


def plot_income_distribution(profiles):
    """소득 분포 막대 그래프"""
    income_dist = Counter([p['income_level'] for p in profiles])

    # 순서 정렬
    income_order = ['저소득', '중소득', '중상소득', '고소득']
    incomes = [inc for inc in income_order if inc in income_dist]
    counts = [income_dist[inc] for inc in incomes]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(incomes, counts, color='lightgreen', edgecolor='darkgreen', alpha=0.7)

    # 막대 위에 값 표시
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}개',
                ha='center', va='bottom')

    plt.title('타겟 프로필 소득 수준 분포', fontsize=16, fontweight='bold')
    plt.xlabel('소득 수준', fontsize=12)
    plt.ylabel('프로필 수', fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(project_root / 'data' / 'processed' / 'income_distribution.png', dpi=300)
    print("✅ 소득 분포 그래프 저장: data/processed/income_distribution.png")


def plot_category_distribution(profiles):
    """카테고리 분포 막대 그래프"""
    category_dist = Counter([p['category'] for p in profiles])

    categories = list(category_dist.keys())
    counts = list(category_dist.values())

    plt.figure(figsize=(10, 6))
    bars = plt.barh(categories, counts, color='coral', edgecolor='darkred', alpha=0.7)

    # 막대 옆에 값 표시
    for i, bar in enumerate(bars):
        width = bar.get_width()
        plt.text(width, bar.get_y() + bar.get_height()/2.,
                f' {int(width)}개',
                ha='left', va='center')

    plt.title('타겟 프로필 제품 카테고리 분포', fontsize=16, fontweight='bold')
    plt.xlabel('프로필 수', fontsize=12)
    plt.ylabel('카테고리', fontsize=12)
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig(project_root / 'data' / 'processed' / 'category_distribution.png', dpi=300)
    print("✅ 카테고리 분포 그래프 저장: data/processed/category_distribution.png")


def plot_top_interests(profiles, top_n=20):
    """상위 관심사 막대 그래프"""
    all_interests = []
    for p in profiles:
        all_interests.extend(p.get('interests', []))

    interest_counts = Counter(all_interests)
    top_interests = interest_counts.most_common(top_n)

    interests = [item[0] for item in top_interests]
    counts = [item[1] for item in top_interests]

    plt.figure(figsize=(12, 8))
    bars = plt.barh(interests, counts, color='mediumpurple', edgecolor='indigo', alpha=0.7)

    # 막대 옆에 값 표시
    for i, bar in enumerate(bars):
        width = bar.get_width()
        plt.text(width, bar.get_y() + bar.get_height()/2.,
                f' {int(width)}',
                ha='left', va='center')

    plt.title(f'상위 {top_n}개 관심사', fontsize=16, fontweight='bold')
    plt.xlabel('언급 횟수', fontsize=12)
    plt.ylabel('관심사', fontsize=12)
    plt.gca().invert_yaxis()  # 상위가 위로
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig(project_root / 'data' / 'processed' / 'top_interests.png', dpi=300)
    print(f"✅ 상위 관심사 그래프 저장: data/processed/top_interests.png")


def plot_top_pain_points(profiles, top_n=15):
    """상위 고충(Pain Points) 막대 그래프"""
    all_pain_points = []
    for p in profiles:
        all_pain_points.extend(p.get('pain_points', []))

    pain_counts = Counter(all_pain_points)
    top_pains = pain_counts.most_common(top_n)

    pains = [item[0] for item in top_pains]
    counts = [item[1] for item in top_pains]

    plt.figure(figsize=(12, 8))
    bars = plt.barh(pains, counts, color='salmon', edgecolor='darkred', alpha=0.7)

    # 막대 옆에 값 표시
    for i, bar in enumerate(bars):
        width = bar.get_width()
        plt.text(width, bar.get_y() + bar.get_height()/2.,
                f' {int(width)}',
                ha='left', va='center')

    plt.title(f'상위 {top_n}개 고충 (Pain Points)', fontsize=16, fontweight='bold')
    plt.xlabel('언급 횟수', fontsize=12)
    plt.ylabel('고충', fontsize=12)
    plt.gca().invert_yaxis()  # 상위가 위로
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig(project_root / 'data' / 'processed' / 'top_pain_points.png', dpi=300)
    print(f"✅ 상위 고충 그래프 저장: data/processed/top_pain_points.png")


def plot_age_gender_heatmap(profiles):
    """나이대 × 성별 히트맵"""
    from collections import defaultdict

    # 데이터 집계
    age_gender_count = defaultdict(lambda: defaultdict(int))
    for p in profiles:
        age = p['age_group']
        gender = p['gender']
        age_gender_count[age][gender] += 1

    # 순서 정렬
    age_order = ['10대', '20대', '30대', '40대', '50대', '60대 이상', '무관']
    gender_order = ['남성', '여성', '무관']

    # 매트릭스 생성
    matrix = []
    for age in age_order:
        row = [age_gender_count[age][gender] for gender in gender_order]
        matrix.append(row)

    plt.figure(figsize=(8, 10))
    plt.imshow(matrix, cmap='YlOrRd', aspect='auto')

    # 축 레이블
    plt.xticks(range(len(gender_order)), gender_order)
    plt.yticks(range(len(age_order)), age_order)

    # 값 표시
    for i in range(len(age_order)):
        for j in range(len(gender_order)):
            text = plt.text(j, i, matrix[i][j],
                          ha="center", va="center", color="black", fontweight='bold')

    plt.title('나이대 × 성별 분포 히트맵', fontsize=16, fontweight='bold')
    plt.xlabel('성별', fontsize=12)
    plt.ylabel('나이대', fontsize=12)
    plt.colorbar(label='프로필 수')
    plt.tight_layout()
    plt.savefig(project_root / 'data' / 'processed' / 'age_gender_heatmap.png', dpi=300)
    print("✅ 나이대×성별 히트맵 저장: data/processed/age_gender_heatmap.png")


def print_summary(profiles):
    """요약 통계 출력"""
    print("\n" + "="*80)
    print("타겟 프로필 데이터 요약")
    print("="*80)

    print(f"\n📊 전체 통계:")
    print(f"  - 총 프로필 수: {len(profiles)}개")

    # 고유 관심사 수
    all_interests = set()
    for p in profiles:
        all_interests.update(p.get('interests', []))
    print(f"  - 고유 관심사 수: {len(all_interests)}개")

    # 고유 고충 수
    all_pain_points = set()
    for p in profiles:
        all_pain_points.update(p.get('pain_points', []))
    print(f"  - 고유 고충 수: {len(all_pain_points)}개")

    # 나이대 분포
    age_dist = Counter([p['age_group'] for p in profiles])
    print(f"\n📈 나이대 분포:")
    for age, count in sorted(age_dist.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(profiles)) * 100
        print(f"  - {age}: {count}개 ({percentage:.1f}%)")

    # 성별 분포
    gender_dist = Counter([p['gender'] for p in profiles])
    print(f"\n👥 성별 분포:")
    for gender, count in sorted(gender_dist.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(profiles)) * 100
        print(f"  - {gender}: {count}개 ({percentage:.1f}%)")

    # 소득 분포
    income_dist = Counter([p['income_level'] for p in profiles])
    print(f"\n💰 소득 분포:")
    for income, count in sorted(income_dist.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(profiles)) * 100
        print(f"  - {income}: {count}개 ({percentage:.1f}%)")

    # 카테고리 분포
    category_dist = Counter([p['category'] for p in profiles])
    print(f"\n🏷️ 카테고리 분포:")
    for category, count in sorted(category_dist.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(profiles)) * 100
        print(f"  - {category}: {count}개 ({percentage:.1f}%)")


def main():
    """메인 실행 함수"""
    print("\n🎨 타겟 세분화 데이터 시각화")
    print("="*80)

    # 데이터 로드
    print("\n데이터 로딩 중...")
    profiles = load_data()
    print(f"✅ {len(profiles)}개 프로필 로드 완료")

    # 요약 통계 출력
    print_summary(profiles)

    # 그래프 생성
    print("\n" + "="*80)
    print("시각화 차트 생성 중...")
    print("="*80 + "\n")

    plot_age_distribution(profiles)
    plot_gender_distribution(profiles)
    plot_income_distribution(profiles)
    plot_category_distribution(profiles)
    plot_top_interests(profiles, top_n=20)
    plot_top_pain_points(profiles, top_n=15)
    plot_age_gender_heatmap(profiles)

    print("\n" + "="*80)
    print("✅ 모든 시각화 완료!")
    print("="*80)
    print("\n📁 저장된 파일 위치: data/processed/")
    print("  - age_distribution.png (나이대 분포)")
    print("  - gender_distribution.png (성별 분포)")
    print("  - income_distribution.png (소득 분포)")
    print("  - category_distribution.png (카테고리 분포)")
    print("  - top_interests.png (상위 관심사)")
    print("  - top_pain_points.png (상위 고충)")
    print("  - age_gender_heatmap.png (나이대×성별 히트맵)")
    print()


if __name__ == "__main__":
    main()
