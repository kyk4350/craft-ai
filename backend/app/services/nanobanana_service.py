"""
Gemini 2.5 Flash Image 생성 서비스 (Nanobanana)
Google의 Gemini 2.5 Flash Image를 사용한 이미지 생성
"""

import google.genai as genai
from typing import Optional, Dict
import logging
import time
import base64
from PIL import Image
from io import BytesIO
from app.config import settings
from app.services.image_storage import image_storage

logger = logging.getLogger(__name__)


class NanobananaService:
    """Gemini 2.5 Flash Image 생성 서비스 (Nano Banana)"""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key:
            # Gemini Client 초기화
            self.client = genai.Client(api_key=self.api_key)
            logger.info("Gemini 2.5 Flash Image (Nano Banana) 클라이언트 초기화 완료")
        else:
            self.client = None
            logger.warning("Gemini API 키가 설정되지 않았습니다")

    async def generate_image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        max_retries: int = 3,
        save_local: bool = True
    ) -> Optional[Dict[str, str]]:
        """
        Gemini 2.5 Flash로 이미지 생성

        Args:
            prompt: 이미지 프롬프트 (영어 권장)
            width: 이미지 너비 (무시됨, Gemini는 자동으로 크기 결정)
            height: 이미지 높이 (무시됨, Gemini는 자동으로 크기 결정)
            max_retries: 최대 재시도 횟수
            save_local: 로컬에 저장 여부

        Returns:
            {
                "original_url": "base64 data URL",
                "local_url": "로컬 저장된 이미지 URL (save_local=True인 경우)",
                "file_path": "로컬 파일 경로 (save_local=True인 경우)"
            }
        """
        if not self.client:
            raise ValueError("Gemini API 키가 설정되지 않았습니다")

        last_error = None

        for attempt in range(max_retries):
            try:
                logger.info(f"이미지 생성 시작 (모델: gemini-2.5-flash-image, 시도: {attempt + 1}/{max_retries})")
                logger.info(f"프롬프트: {prompt[:100]}...")

                # Gemini 2.5 Flash Image API 호출
                import asyncio

                response = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model="gemini-2.5-flash-image",
                    contents=prompt
                )

                logger.info(f"응답 수신 완료")

                # 응답에서 이미지 추출
                if response and hasattr(response, 'candidates'):
                    for candidate in response.candidates:
                        if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                            for part in candidate.content.parts:
                                if hasattr(part, 'inline_data') and part.inline_data is not None:
                                    # 이미지 데이터 추출
                                    image_data = part.inline_data.data

                                    logger.info(f"✓ 이미지 생성 완료 (크기: {len(image_data)} bytes)")

                                    result = {
                                        "original_url": f"data:image/png;base64,{base64.b64encode(image_data).decode()}"
                                    }

                                    # 로컬 저장
                                    if save_local:
                                        logger.info("로컬 스토리지에 이미지 저장 중...")

                                        storage_result = await image_storage.save_from_bytes(
                                            image_bytes=image_data,
                                            optimize=True
                                        )

                                        if storage_result:
                                            result["local_url"] = storage_result["public_url"]
                                            result["file_path"] = storage_result["file_path"]
                                            logger.info(f"✓ 로컬 저장 완료: {storage_result['public_url']}")
                                        else:
                                            logger.warning("로컬 저장 실패, Base64 URL만 반환")

                                    return result

                # 이미지 데이터를 찾지 못한 경우
                logger.warning(f"응답에서 이미지를 찾을 수 없음")
                raise ValueError("Gemini 2.5 Flash Image 응답에 이미지가 없습니다")

            except Exception as e:
                last_error = e
                logger.warning(f"이미지 생성 시도 {attempt + 1}/{max_retries} 실패: {str(e)}")

                if attempt < max_retries - 1:
                    # 지수 백오프: 3초, 6초, 12초
                    wait_time = 3 * (2 ** attempt)
                    logger.info(f"{wait_time}초 후 재시도...")
                    time.sleep(wait_time)

        logger.error(f"이미지 생성 최종 실패 (재시도 {max_retries}회): {str(last_error)}")
        raise last_error

    async def generate_from_product_image(
        self,
        product_image_path: str,
        prompt: str,
        max_retries: int = 3,
        save_local: bool = True
    ) -> Optional[Dict[str, str]]:
        """
        제품 이미지를 활용한 마케팅 이미지 생성 (Image + Text → Image)

        Gemini는 제품 이미지를 보고 자연스럽게 합성된 마케팅 이미지를 생성합니다.
        예: 핸드크림 이미지 → 누군가 핸드크림을 들고 있는 마케팅 이미지

        Args:
            product_image_path: 제품 이미지 파일 경로
            prompt: 마케팅 이미지 생성 프롬프트
            max_retries: 최대 재시도 횟수
            save_local: 로컬에 저장 여부

        Returns:
            생성된 이미지 정보
        """
        if not self.client:
            raise ValueError("Gemini API 키가 설정되지 않았습니다")

        last_error = None

        for attempt in range(max_retries):
            try:
                logger.info(f"제품 이미지 기반 마케팅 이미지 생성 시작 (시도: {attempt + 1}/{max_retries})")
                logger.info(f"제품 이미지: {product_image_path}")
                logger.info(f"프롬프트: {prompt[:100]}...")

                # 제품 이미지 읽기
                with open(product_image_path, "rb") as f:
                    product_image_bytes = f.read()

                # PIL Image로 변환
                product_image = Image.open(BytesIO(product_image_bytes))

                logger.info(f"제품 이미지 로드 완료: {product_image.size}")

                # Gemini 2.5 Flash Image API 호출 (이미지 + 텍스트)
                import asyncio

                response = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model="gemini-2.5-flash-image",
                    contents=[
                        product_image,  # 제품 이미지
                        prompt  # 생성할 마케팅 이미지에 대한 설명
                    ]
                )

                logger.info(f"응답 수신 완료")

                # 응답에서 이미지 추출
                if response and hasattr(response, 'candidates'):
                    for candidate in response.candidates:
                        if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                            for part in candidate.content.parts:
                                if hasattr(part, 'inline_data') and part.inline_data is not None:
                                    # 이미지 데이터 추출
                                    image_data = part.inline_data.data

                                    logger.info(f"✓ 제품 이미지 기반 마케팅 이미지 생성 완료 (크기: {len(image_data)} bytes)")

                                    result = {
                                        "original_url": f"data:image/png;base64,{base64.b64encode(image_data).decode()}",
                                        "is_product_based": True
                                    }

                                    # 로컬 저장
                                    if save_local:
                                        logger.info("로컬 스토리지에 이미지 저장 중...")

                                        storage_result = await image_storage.save_from_bytes(
                                            image_bytes=image_data,
                                            optimize=True
                                        )

                                        if storage_result:
                                            result["local_url"] = storage_result["public_url"]
                                            result["file_path"] = storage_result["file_path"]
                                            logger.info(f"✓ 로컬 저장 완료: {storage_result['public_url']}")
                                        else:
                                            logger.warning("로컬 저장 실패, Base64 URL만 반환")

                                    return result

                # 이미지 데이터를 찾지 못한 경우
                logger.warning(f"응답에서 이미지를 찾을 수 없음")
                raise ValueError("Gemini 2.5 Flash Image 응답에 이미지가 없습니다")

            except Exception as e:
                last_error = e
                logger.warning(f"제품 이미지 기반 생성 시도 {attempt + 1}/{max_retries} 실패: {str(e)}")

                if attempt < max_retries - 1:
                    wait_time = 3 * (2 ** attempt)
                    logger.info(f"{wait_time}초 후 재시도...")
                    time.sleep(wait_time)

        logger.error(f"제품 이미지 기반 생성 최종 실패 (재시도 {max_retries}회): {str(last_error)}")
        raise last_error


# 싱글톤 인스턴스
nanobanana_service = NanobananaService()
