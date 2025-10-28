"""
합성 데이터 품질 검증 스크립트
- 다양성, 현실성, 적절성, 중복 등을 검증
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
from typing import List, Dict
import difflib

# 합성 데이터 로드
data_path = Path(__file__).parent.parent / "data" / "processed" / "target_profiles.json"
with open(data_path, 'r', encoding='utf-8') as f:
    profiles = json.load(f)

print('=' * 70)
print('합성 타겟 프로필 - 상세 품질 검증')
print('=' * 70)
print()

# ============================================================
# 1. 기본 통계
# ============================================================
print('[1] 기본 통계')
print(f'  총 프로필 수: {len(profiles)}개')
print()

# ============================================================
# 2. 관심사 다양성 검증
# ============================================================
print('[2] 관심사 다양성 검증')
all_interests = []
for p in profiles:
    all_interests.extend(p.get('interests', []))

interest_counts = Counter(all_interests)
unique_interests = len(interest_counts)
total_interests = len(all_interests)

print(f'  ✓ 총 관심사 출현 횟수: {total_interests}')
print(f'  ✓ 고유 관심사 종류: {unique_interests}개')
print(f'  ✓ 평균 관심사 개수/프로필: {total_interests/len(profiles):.1f}개')
print()
print(f'  상위 10개 관심사:')
for interest, count in interest_counts.most_common(10):
    print(f'    - {interest}: {count}회 ({count/total_interests*100:.1f}%)')
print()

# 관심사 다양성 평가
if unique_interests < 30:
    print(f'  ⚠️ 관심사 종류가 부족합니다 (30개 미만)')
elif unique_interests < 50:
    print(f'  ✓ 관심사 종류가 적당합니다 (30-50개)')
else:
    print(f'  ✅ 관심사가 매우 다양합니다 (50개 이상)')
print()

# ============================================================
# 3. Pain Points 다양성 검증
# ============================================================
print('[3] Pain Points 다양성 검증')
all_pain_points = []
for p in profiles:
    all_pain_points.extend(p.get('pain_points', []))

pain_counts = Counter(all_pain_points)
unique_pains = len(pain_counts)

print(f'  ✓ 고유 Pain Points 종류: {unique_pains}개')
print(f'  ✓ 평균 Pain Points 개수/프로필: {len(all_pain_points)/len(profiles):.1f}개')
print()
print(f'  상위 10개 Pain Points:')
for pain, count in pain_counts.most_common(10):
    print(f'    - {pain}: {count}회')
print()

# ============================================================
# 4. 채널 적절성 검증 (연령대별)
# ============================================================
print('[4] 연령대별 선호 채널 분석')
age_channel_map = defaultdict(lambda: defaultdict(int))

for p in profiles:
    age = p.get('age_group', '')
    channels = p.get('preferred_channels', [])
    for channel in channels:
        age_channel_map[age][channel] += 1

# 연령대별 상위 3개 채널
for age in sorted(age_channel_map.keys()):
    channels = age_channel_map[age]
    total = sum(channels.values())
    print(f'  {age}:')
    for channel, count in Counter(channels).most_common(3):
        print(f'    - {channel}: {count}회 ({count/total*100:.0f}%)')
print()

# ============================================================
# 5. 카테고리별 라이프스타일 분석
# ============================================================
print('[5] 카테고리별 주요 라이프스타일')
category_lifestyle_map = defaultdict(lambda: defaultdict(int))

for p in profiles:
    category = p.get('category', '')
    lifestyle = p.get('lifestyle', '')
    if lifestyle:
        # 라이프스타일을 쉼표로 분리 (여러 개일 수 있음)
        lifestyles = [ls.strip() for ls in lifestyle.split(',')]
        for ls in lifestyles[:1]:  # 첫 번째만 카운트
            category_lifestyle_map[category][ls] += 1

for category in sorted(category_lifestyle_map.keys()):
    lifestyles = category_lifestyle_map[category]
    print(f'  {category}:')
    for lifestyle, count in Counter(lifestyles).most_common(3):
        print(f'    - {lifestyle}: {count}개')
print()

# ============================================================
# 6. 중복 프로필 검출
# ============================================================
print('[6] 중복/유사 프로필 검출')

# 프로필 유사도 계산 (간단 버전 - interests + lifestyle 기반)
def profile_signature(p: Dict) -> str:
    """프로필의 고유 시그니처 생성"""
    interests_str = ','.join(sorted(p.get('interests', [])))
    lifestyle = p.get('lifestyle', '')
    pain_points_str = ','.join(sorted(p.get('pain_points', [])))
    return f"{p.get('age_group')}|{p.get('gender')}|{p.get('income_level')}|{interests_str}|{lifestyle}|{pain_points_str}"

signatures = [profile_signature(p) for p in profiles]
signature_counts = Counter(signatures)

duplicates = {sig: count for sig, count in signature_counts.items() if count > 1}

if duplicates:
    print(f'  ⚠️ {len(duplicates)}개의 중복 프로필 발견:')
    for sig, count in list(duplicates.items())[:5]:  # 상위 5개만 출력
        print(f'    - {count}회 중복: {sig[:80]}...')
    print()
else:
    print(f'  ✅ 중복 프로필 없음 (모든 프로필이 고유함)')
    print()

# 유사 프로필 검출 (첫 100개만 샘플링)
print('  유사도가 높은 프로필 쌍 검사 (샘플 100개):')
similar_pairs = []
sample_size = min(100, len(profiles))

for i in range(sample_size):
    for j in range(i+1, sample_size):
        sig1 = signatures[i]
        sig2 = signatures[j]
        similarity = difflib.SequenceMatcher(None, sig1, sig2).ratio()
        if similarity > 0.8:  # 80% 이상 유사
            similar_pairs.append((i+1, j+1, similarity))

if similar_pairs:
    print(f'  ⚠️ {len(similar_pairs)}쌍의 유사 프로필 발견:')
    for id1, id2, sim in similar_pairs[:5]:
        print(f'    - Profile {id1} vs {id2}: {sim*100:.1f}% 유사')
else:
    print(f'  ✅ 유사 프로필 없음 (샘플 {sample_size}개 검사)')
print()

# ============================================================
# 7. 소득-연령 적절성 검증
# ============================================================
print('[7] 소득-연령 적절성 검증')
age_income_map = defaultdict(lambda: defaultdict(int))

for p in profiles:
    age = p.get('age_group', '')
    income = p.get('income_level', '')
    age_income_map[age][income] += 1

# 이상한 조합 검출 (10대 고소득 등)
suspicious = []
if age_income_map['10대']['고소득'] > 5:
    suspicious.append(f"10대 고소득: {age_income_map['10대']['고소득']}개")
if age_income_map['60대 이상']['저소득'] > 50:
    suspicious.append(f"60대 이상 저소득 과다: {age_income_map['60대 이상']['저소득']}개")

if suspicious:
    print('  ⚠️ 부자연스러운 조합 발견:')
    for s in suspicious:
        print(f'    - {s}')
else:
    print('  ✅ 연령-소득 조합이 적절함')
print()

# 연령별 소득 분포
for age in ['10대', '20대', '30대', '40대', '50대', '60대 이상']:
    if age in age_income_map:
        incomes = age_income_map[age]
        total = sum(incomes.values())
        high_income_pct = (incomes['고소득'] / total * 100) if total > 0 else 0
        print(f'  {age}: 고소득 비율 {high_income_pct:.1f}%')
print()

# ============================================================
# 8. 종합 평가
# ============================================================
print('=' * 70)
print('[종합 평가]')
print('=' * 70)

score = 0
max_score = 5

# 1. 관심사 다양성
if unique_interests >= 50:
    print('✅ 관심사 다양성: 우수')
    score += 1
elif unique_interests >= 30:
    print('✓ 관심사 다양성: 양호')
    score += 0.7
else:
    print('⚠️ 관심사 다양성: 부족')

# 2. Pain Points 다양성
if unique_pains >= 100:
    print('✅ Pain Points 다양성: 우수')
    score += 1
elif unique_pains >= 50:
    print('✓ Pain Points 다양성: 양호')
    score += 0.7
else:
    print('⚠️ Pain Points 다양성: 부족')

# 3. 중복 프로필
if len(duplicates) == 0:
    print('✅ 프로필 고유성: 우수 (중복 없음)')
    score += 1
elif len(duplicates) < 10:
    print('✓ 프로필 고유성: 양호 (중복 10개 미만)')
    score += 0.7
else:
    print(f'⚠️ 프로필 고유성: 개선 필요 (중복 {len(duplicates)}개)')

# 4. 유사 프로필
if len(similar_pairs) == 0:
    print('✅ 프로필 다양성: 우수 (유사 프로필 없음)')
    score += 1
elif len(similar_pairs) < 10:
    print('✓ 프로필 다양성: 양호')
    score += 0.7
else:
    print(f'⚠️ 프로필 다양성: 개선 필요 (유사 쌍 {len(similar_pairs)}개)')

# 5. 연령-소득 적절성
if len(suspicious) == 0:
    print('✅ 연령-소득 조합: 적절함')
    score += 1
else:
    print(f'⚠️ 연령-소득 조합: 일부 부자연스러움')
    score += 0.5

print()
print(f'📊 최종 품질 점수: {score:.1f}/{max_score} ({score/max_score*100:.0f}%)')
print()

if score >= 4.5:
    print('🎉 데이터 품질이 매우 우수합니다!')
elif score >= 3.5:
    print('✓ 데이터 품질이 양호합니다. 사용 가능합니다.')
elif score >= 2.5:
    print('⚠️ 데이터 품질이 보통입니다. 일부 개선이 필요합니다.')
else:
    print('❌ 데이터 품질이 부족합니다. 재생성을 권장합니다.')

print('=' * 70)
