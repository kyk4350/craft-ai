#!/bin/bash

# 콘텐츠 생성 API 테스트 스크립트

BASE_URL="http://localhost:8000"

echo "=========================================="
echo "TEST 1: 전략 생성 API"
echo "=========================================="

curl -X POST "$BASE_URL/api/content/strategy" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "비타민C 세럼",
    "product_description": "피부 톤 개선 및 미백 효과가 있는 고농축 비타민C 세럼",
    "category": "화장품",
    "target_age": "20대",
    "target_gender": "여성",
    "target_interests": ["뷰티", "스킨케어", "패션"]
  }' | python3 -m json.tool

echo ""
echo ""
echo "=========================================="
echo "TEST 2: 카피 생성 API"
echo "=========================================="

curl -X POST "$BASE_URL/api/content/copy" \
  -H "Content-Type: application/json" \
  -d '{
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
  }' | python3 -m json.tool

echo ""
echo ""
echo "=========================================="
echo "TEST 3: 이미지 프롬프트 생성 API"
echo "=========================================="

curl -X POST "$BASE_URL/api/content/image-prompt" \
  -H "Content-Type: application/json" \
  -d '{
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
  }' | python3 -m json.tool

echo ""
echo ""
echo "=========================================="
echo "✅ 모든 API 테스트 완료!"
echo "=========================================="
