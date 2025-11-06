#!/usr/bin/env python3
"""RAG 기능 테스트 스크립트"""
import requests
import json
import time

API_URL = "http://127.0.0.1:8000/api/content/generate"

# 첫 번째 콘텐츠 생성
print("=" * 60)
print("첫 번째 콘텐츠 생성 중...")
print("=" * 60)

payload1 = {
    "product_name": "비타민C 세럼",
    "product_description": "순수 비타민C 20% 함유, 피부 톤 개선 및 잡티 완화",
    "category": "뷰티",
    "target_ages": ["20대", "30대"],
    "target_gender": "여성",
    "target_interests": ["스킨케어", "미백"]
}

try:
    response1 = requests.post(API_URL, json=payload1, timeout=120)
    print(f"상태 코드: {response1.status_code}")

    if response1.status_code == 200:
        result1 = response1.json()
        print(f"✓ 첫 번째 콘텐츠 생성 성공")
        print(f"  - Content ID: {result1['data'].get('content_id')}")
        print(f"  - 카피: {result1['data'].get('copy_text', '')[:100]}...")
        if result1['data'].get('performance_prediction'):
            print(f"  - 성과 예측: {result1['data']['performance_prediction']}")
    else:
        print(f"✗ 실패: {response1.text}")
except Exception as e:
    print(f"✗ 오류: {e}")

# 잠시 대기
print("\n대기 중 (5초)...")
time.sleep(5)

# 두 번째 콘텐츠 생성 (유사한 제품)
print("\n" + "=" * 60)
print("두 번째 콘텐츠 생성 중... (RAG가 첫 번째 콘텐츠를 찾아야 함)")
print("=" * 60)

payload2 = {
    "product_name": "비타민C 앰플",
    "product_description": "고농축 비타민C 15% 함유, 피부 톤 균일화 및 미백",
    "category": "뷰티",
    "target_ages": ["20대", "30대"],
    "target_gender": "여성",
    "target_interests": ["스킨케어", "미백"]
}

try:
    response2 = requests.post(API_URL, json=payload2, timeout=120)
    print(f"상태 코드: {response2.status_code}")

    if response2.status_code == 200:
        result2 = response2.json()
        print(f"✓ 두 번째 콘텐츠 생성 성공")
        print(f"  - Content ID: {result2['data'].get('content_id')}")
        print(f"  - 카피: {result2['data'].get('copy_text', '')[:100]}...")
        if result2['data'].get('performance_prediction'):
            print(f"  - 성과 예측: {result2['data']['performance_prediction']}")
    else:
        print(f"✗ 실패: {response2.text}")
except Exception as e:
    print(f"✗ 오류: {e}")

print("\n" + "=" * 60)
print("테스트 완료! 백엔드 로그를 확인하여 RAG 검색 로그를 확인하세요.")
print("=" * 60)
