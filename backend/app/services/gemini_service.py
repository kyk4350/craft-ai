"""
Gemini API 서비스 모듈
텍스트 생성 (전략, 카피, 프롬프트 변환, 분석)
"""

import google.generativeai as genai
from typing import Dict, List, Optional
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# Gemini API 설정
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)


class GeminiService:
    """Gemini API 텍스트 생성 서비스"""

    def __init__(self):
        self.model_name = settings.GEMINI_MODEL
        self.model = genai.GenerativeModel(self.model_name)

    async def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        텍스트 생성

        Args:
            prompt: 입력 프롬프트
            temperature: 창의성 조절 (0.0-1.0)
            max_tokens: 최대 토큰 수

        Returns:
            생성된 텍스트
        """
        try:
            generation_config = {
                "temperature": temperature,
            }
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )

            return response.text

        except Exception as e:
            logger.error(f"Gemini 텍스트 생성 실패: {str(e)}")
            raise

    async def generate_marketing_strategies(
        self,
        product_name: str,
        product_description: str,
        category: str,
        target_age: str,
        target_gender: str,
        target_interests: List[str]
    ) -> List[Dict]:
        """
        마케팅 전략 3가지 제안

        Returns:
            [
                {
                    "id": 1,
                    "name": "전략명",
                    "core_message": "핵심 메시지",
                    "emotion": "감성적|이성적|사회적",
                    "expected_effect": "예상 효과"
                }
            ]
        """
        interests_str = ", ".join(target_interests)

        prompt = f"""
당신은 전문 마케팅 전략가입니다.

제품 정보:
- 제품명: {product_name}
- 설명: {product_description}
- 카테고리: {category}

타겟 고객:
- 나이: {target_age}
- 성별: {target_gender}
- 관심사: {interests_str}

위 제품을 타겟 고객에게 판매하기 위한 3가지 서로 다른 마케팅 전략을 제안해주세요.

각 전략은 다음 JSON 형식으로 작성해주세요:
{{
  "strategies": [
    {{
      "id": 1,
      "name": "전략명 (예: 감성적 스토리텔링)",
      "core_message": "핵심 메시지 (한 문장)",
      "emotion": "감성적|이성적|사회적",
      "expected_effect": "예상 효과 설명"
    }}
  ]
}}

JSON만 출력해주세요.
"""

        try:
            response_text = await self.generate_text(prompt, temperature=0.8)
            # JSON 파싱 로직 추가 필요
            return response_text
        except Exception as e:
            logger.error(f"전략 생성 실패: {str(e)}")
            raise

    async def generate_copies(
        self,
        product_name: str,
        product_description: str,
        strategy: Dict,
        target_age: str,
        target_gender: str,
        target_interests: List[str]
    ) -> List[Dict]:
        """
        3가지 톤의 광고 카피 생성

        Returns:
            [
                {
                    "id": 1,
                    "tone": "professional|casual|impact",
                    "text": "카피 텍스트",
                    "hashtags": ["#태그1", "#태그2", "#태그3"],
                    "length": 45
                }
            ]
        """
        interests_str = ", ".join(target_interests)

        prompt = f"""
당신은 전문 카피라이터입니다.

제품: {product_name}
설명: {product_description}
전략: {strategy.get('name')} - {strategy.get('core_message')}
타겟: {target_age} {target_gender}, 관심사: {interests_str}

위 전략을 기반으로 3가지 톤의 광고 카피를 작성해주세요:

1. Professional (프로페셔널): 격식 있고 전문적인 톤, 40-50자
2. Casual (캐주얼): 친근하고 편안한 톤, 30-40자
3. Impact (임팩트): 짧고 강렬한 톤, 15-25자

각 카피에는 관련 해시태그 3개를 포함해주세요.

JSON 형식으로 출력:
{{
  "copies": [
    {{
      "id": 1,
      "tone": "professional",
      "text": "카피 내용",
      "hashtags": ["#태그1", "#태그2", "#태그3"],
      "length": 글자수
    }}
  ]
}}

JSON만 출력해주세요.
"""

        try:
            response_text = await self.generate_text(prompt, temperature=0.9)
            # JSON 파싱 로직 추가 필요
            return response_text
        except Exception as e:
            logger.error(f"카피 생성 실패: {str(e)}")
            raise

    async def convert_to_image_prompt(
        self,
        copy_text: str,
        product_name: str,
        target_age: str,
        target_gender: str,
        strategy: Dict
    ) -> str:
        """
        카피를 이미지 생성 프롬프트로 변환

        Returns:
            영어 이미지 프롬프트
        """
        prompt = f"""
당신은 이미지 생성 전문가입니다.

다음 광고 카피를 시각화할 이미지 생성 프롬프트를 영어로 작성해주세요.

카피: "{copy_text}"
제품: {product_name}
타겟: {target_age} {target_gender}
전략: {strategy.get('name')}

프롬프트에 반드시 포함할 요소:
- 주요 피사체 (제품 또는 사람)
- 배경
- 분위기 (mood)
- 색감 (color palette)
- 스타일 (photography style, illustration, etc)

구체적이고 상세하게 영어로 작성해주세요.
프롬프트만 출력하고 다른 설명은 하지 마세요.
"""

        try:
            image_prompt = await self.generate_text(prompt, temperature=0.7)
            return image_prompt.strip()
        except Exception as e:
            logger.error(f"이미지 프롬프트 변환 실패: {str(e)}")
            raise


# 싱글톤 인스턴스
gemini_service = GeminiService()
