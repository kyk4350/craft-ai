"""
Ideogram AI 이미지 생성 서비스

제품 이미지를 활용한 마케팅 이미지 생성, 이미지 편집(remix, edit) 기능 제공
"""

import httpx
import logging
import base64
from typing import Dict, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class IdeogramService:
    """Ideogram AI API 서비스"""

    def __init__(self):
        self.api_key = settings.IDEOGRAM_API_KEY if hasattr(settings, 'IDEOGRAM_API_KEY') else None
        self.base_url = "https://api.ideogram.ai/v1"

        if not self.api_key:
            logger.warning("⚠️ IDEOGRAM_API_KEY가 설정되지 않았습니다")

    async def generate_from_product_image(
        self,
        product_image_path: str,
        prompt: str,
        style_type: str = "AUTO",
        aspect_ratio: str = "ASPECT_1_1",
        magic_prompt_option: str = "AUTO"
    ) -> Dict:
        """
        제품 이미지를 활용한 마케팅 이미지 생성 (Remix)

        Args:
            product_image_path: 제품 이미지 파일 경로
            prompt: 이미지 생성 프롬프트
            style_type: 스타일 (AUTO, GENERAL, REALISTIC, DESIGN, 3D, ANIME)
            aspect_ratio: 비율 (ASPECT_1_1, ASPECT_16_9, ASPECT_9_16 등)
            magic_prompt_option: Magic Prompt 옵션 (AUTO, ON, OFF)

        Returns:
            생성된 이미지 정보 (URL, local_path 등)
        """
        if not self.api_key:
            raise ValueError("IDEOGRAM_API_KEY가 설정되지 않았습니다")

        try:
            logger.info(f"=== Ideogram Remix 시작 ===")
            logger.info(f"제품 이미지: {product_image_path}")
            logger.info(f"프롬프트: {prompt[:100]}...")

            # 이미지를 base64로 인코딩
            with open(product_image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')

            # Ideogram API 요청
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/remix",
                    headers={
                        "Api-Key": self.api_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "image_request": {
                            "prompt": prompt,
                            "aspect_ratio": aspect_ratio,
                            "model": "V_2",  # Ideogram V2 (최신 버전)
                            "magic_prompt_option": magic_prompt_option,
                            "style_type": style_type
                        },
                        "image_file": {
                            "data": image_data,
                            "type": "image/png"
                        }
                    }
                )

                response.raise_for_status()
                result = response.json()

                logger.info(f"✅ Ideogram Remix 성공")

                # 첫 번째 이미지 URL 추출
                image_url = result['data'][0]['url']

                return {
                    "original_url": image_url,
                    "local_url": None,  # 나중에 다운로드 후 설정
                    "file_path": None,
                    "prompt": prompt,
                    "is_remix": True
                }

        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Ideogram API 오류: {e.response.status_code}")
            logger.error(f"응답: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"❌ Ideogram Remix 실패: {str(e)}")
            raise

    async def generate_image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        style_type: str = "AUTO",
        magic_prompt_option: str = "AUTO"
    ) -> Dict:
        """
        프롬프트로 이미지 생성 (Text-to-Image)

        Args:
            prompt: 이미지 생성 프롬프트
            width: 이미지 너비
            height: 이미지 높이
            style_type: 스타일
            magic_prompt_option: Magic Prompt 옵션

        Returns:
            생성된 이미지 정보
        """
        if not self.api_key:
            raise ValueError("IDEOGRAM_API_KEY가 설정되지 않았습니다")

        try:
            logger.info(f"=== Ideogram 이미지 생성 시작 ===")
            logger.info(f"프롬프트: {prompt[:100]}...")

            # 비율 계산
            aspect_ratio = self._get_aspect_ratio(width, height)

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/generate",
                    headers={
                        "Api-Key": self.api_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "image_request": {
                            "prompt": prompt,
                            "aspect_ratio": aspect_ratio,
                            "model": "V_2",  # Ideogram V2
                            "magic_prompt_option": magic_prompt_option,
                            "style_type": style_type
                        }
                    }
                )

                response.raise_for_status()
                result = response.json()

                logger.info(f"✅ Ideogram 이미지 생성 성공")

                image_url = result['data'][0]['url']

                return {
                    "original_url": image_url,
                    "local_url": None,
                    "file_path": None,
                    "prompt": prompt
                }

        except Exception as e:
            logger.error(f"❌ Ideogram 이미지 생성 실패: {str(e)}")
            raise

    async def edit_image(
        self,
        original_image_path: str,
        mask_image_path: str,
        prompt: str,
        style_type: str = "AUTO"
    ) -> Dict:
        """
        이미지 편집 (Inpainting)
        특정 영역만 수정

        Args:
            original_image_path: 원본 이미지 경로
            mask_image_path: 마스크 이미지 경로 (편집할 영역)
            prompt: 편집 프롬프트
            style_type: 스타일

        Returns:
            편집된 이미지 정보
        """
        if not self.api_key:
            raise ValueError("IDEOGRAM_API_KEY가 설정되지 않았습니다")

        try:
            logger.info(f"=== Ideogram Edit (Inpainting) 시작 ===")

            # 이미지들을 base64로 인코딩
            with open(original_image_path, "rb") as f:
                original_data = base64.b64encode(f.read()).decode('utf-8')

            with open(mask_image_path, "rb") as f:
                mask_data = base64.b64encode(f.read()).decode('utf-8')

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/edit",
                    headers={
                        "Api-Key": self.api_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "image_request": {
                            "prompt": prompt,
                            "model": "V_2",
                            "style_type": style_type
                        },
                        "image_file": {
                            "data": original_data,
                            "type": "image/png"
                        },
                        "mask": {
                            "data": mask_data,
                            "type": "image/png"
                        }
                    }
                )

                response.raise_for_status()
                result = response.json()

                logger.info(f"✅ Ideogram Edit 성공")

                image_url = result['data'][0]['url']

                return {
                    "original_url": image_url,
                    "local_url": None,
                    "file_path": None,
                    "prompt": prompt,
                    "is_edited": True
                }

        except Exception as e:
            logger.error(f"❌ Ideogram Edit 실패: {str(e)}")
            raise

    def _get_aspect_ratio(self, width: int, height: int) -> str:
        """
        너비와 높이로 Ideogram aspect_ratio 값 계산

        Returns:
            ASPECT_1_1, ASPECT_16_9 등
        """
        ratio = width / height

        if abs(ratio - 1.0) < 0.1:
            return "ASPECT_1_1"
        elif abs(ratio - 16/9) < 0.1:
            return "ASPECT_16_9"
        elif abs(ratio - 9/16) < 0.1:
            return "ASPECT_9_16"
        elif abs(ratio - 4/3) < 0.1:
            return "ASPECT_4_3"
        elif abs(ratio - 3/4) < 0.1:
            return "ASPECT_3_4"
        else:
            return "ASPECT_1_1"  # 기본값


# 싱글톤 인스턴스
ideogram_service = IdeogramService()
