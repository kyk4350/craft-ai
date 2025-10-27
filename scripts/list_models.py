"""
사용 가능한 Gemini 모델 목록 확인
"""

import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / "backend" / ".env")

import os
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("사용 가능한 Gemini 모델:")
print("="*60)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"- {model.name}")
        print(f"  설명: {model.display_name}")
        print()
