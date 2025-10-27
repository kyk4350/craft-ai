"""
이미지 생성 서비스 모듈
Mock, Stability AI, 나노바나나 지원
"""

import os
import logging
from typing import Optional
from enum import Enum
import google.generativeai as genai
import requests
from app.config import settings

logger = logging.getLogger(__name__)

# Gemini API 설정 (나노바나나용)
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)


class ImageProvider(str, Enum):
    """이미지 생성 프로바이더"""
    MOCK = "mock"
    STABILITY = "stability"
    NANOBANANA = "nanobanana"


class ImageService:
    """이미지 생성 통합 서비스"""

    def __init__(self):
        self.provider = ImageProvider(settings.IMAGE_PROVIDER)
        logger.info(f"이미지 생성 프로바이더: {self.provider.value}")

    async def generate_image(self, prompt: str, category: str = "product") -> str:
        """
        이미지 생성

        Args:
            prompt: 이미지 생성 프롬프트 (영어)
            category: 카테고리 (mock용)

        Returns:
            이미지 URL
        """
        try:
            if self.provider == ImageProvider.MOCK:
                return await self._generate_mock(prompt, category)
            elif self.provider == ImageProvider.STABILITY:
                return await self._generate_stability(prompt)
            elif self.provider == ImageProvider.NANOBANANA:
                return await self._generate_nanobanana(prompt)
            else:
                raise ValueError(f"알 수 없는 프로바이더: {self.provider}")

        except Exception as e:
            logger.error(f"이미지 생성 실패 ({self.provider}): {str(e)}")
            raise

    async def _generate_mock(self, prompt: str, category: str) -> str:
        """
        Mock 이미지 생성 (Unsplash)
        완전 무료

        Args:
            prompt: 프롬프트 (사용하지 않음)
            category: 카테고리 (beauty, product, fashion, etc)

        Returns:
            Unsplash 이미지 URL
        """
        logger.info(f"Mock 이미지 생성: {category}")

        # 카테고리 매핑
        category_map = {
            "화장품": "beauty,skincare",
            "식품": "food,healthy",
            "패션": "fashion,style",
            "전자제품": "technology,gadget",
            "서비스": "business,office",
        }

        search_term = category_map.get(category, "product,marketing")

        # Unsplash Source API
        image_url = f"https://source.unsplash.com/800x600/?{search_term}"

        return image_url

    async def _generate_stability(self, prompt: str) -> str:
        """
        Stability AI (SDXL) 이미지 생성
        약 $0.004/이미지

        Args:
            prompt: 영어 프롬프트

        Returns:
            생성된 이미지 URL (저장 후)
        """
        if not settings.STABILITY_API_KEY:
            raise ValueError("STABILITY_API_KEY가 설정되지 않았습니다")

        logger.info(f"Stability AI 이미지 생성 중...")

        url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

        headers = {
            "Authorization": f"Bearer {settings.STABILITY_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        body = {
            "text_prompts": [
                {
                    "text": prompt,
                    "weight": 1
                }
            ],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 30,
        }

        response = requests.post(url, headers=headers, json=body)

        if response.status_code != 200:
            raise Exception(f"Stability AI API 오류: {response.text}")

        data = response.json()

        # 이미지 Base64 데이터
        image_data = data["artifacts"][0]["base64"]

        # TODO: 이미지를 파일로 저장하고 URL 반환
        # 현재는 base64 데이터 URL 반환
        image_url = f"data:image/png;base64,{image_data}"

        logger.info("Stability AI 이미지 생성 완료")
        return image_url

    async def _generate_nanobanana(self, prompt: str) -> str:
        """
        나노바나나 (Gemini 2.5 Flash Image) 이미지 생성
        약 $0.039/이미지

        Args:
            prompt: 영어 프롬프트

        Returns:
            생성된 이미지 URL
        """
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다")

        logger.info(f"나노바나나 이미지 생성 중...")

        try:
            model = genai.GenerativeModel('gemini-2.5-flash-image')

            response = model.generate_content([prompt])

            # 이미지 데이터 추출
            if response.parts:
                image_data = response.parts[0].data

                # TODO: 이미지를 파일로 저장하고 URL 반환
                # 현재는 임시로 처리
                image_url = "nanobanana_image_url"

                logger.info("나노바나나 이미지 생성 완료")
                return image_url
            else:
                raise Exception("이미지 생성 실패: 응답에 이미지 데이터가 없습니다")

        except Exception as e:
            logger.error(f"나노바나나 이미지 생성 실패: {str(e)}")
            raise

    def _extract_category(self, prompt: str) -> str:
        """
        프롬프트에서 카테고리 추출 (Mock용)

        Args:
            prompt: 프롬프트

        Returns:
            카테고리 키워드
        """
        keywords = {
            "beauty": ["beauty", "cosmetic", "makeup", "skincare", "serum"],
            "food": ["food", "cooking", "meal", "restaurant"],
            "fashion": ["fashion", "clothing", "style", "wear"],
            "technology": ["tech", "gadget", "device", "electronic"],
        }

        prompt_lower = prompt.lower()

        for category, words in keywords.items():
            for word in words:
                if word in prompt_lower:
                    return category

        return "product"


# 싱글톤 인스턴스
image_service = ImageService()
