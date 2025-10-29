"""
Replicate API 서비스 모듈
이미지 생성 (SDXL, Ideogram v3 Turbo)
"""

import replicate
from typing import Optional, Dict
import logging
import time
from app.config import settings
from app.services.image_storage import image_storage

logger = logging.getLogger(__name__)


class ReplicateService:
    """Replicate API 이미지 생성 서비스"""

    def __init__(self):
        self.api_token = settings.REPLICATE_API_TOKEN
        # Replicate Client 생성 (토큰 명시적 전달)
        if self.api_token:
            self.client = replicate.Client(api_token=self.api_token)
            logger.info("Replicate API 클라이언트 초기화 완료")
        else:
            self.client = None
            logger.warning("Replicate API 토큰이 설정되지 않았습니다")

    async def generate_image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        num_outputs: int = 1,
        guidance_scale: float = 7.5,
        num_inference_steps: int = 50,
        max_retries: int = 3,
        save_local: bool = True
    ) -> Optional[Dict[str, str]]:
        """
        이미지 생성 (환경별 모델 자동 선택)

        Args:
            prompt: 이미지 프롬프트 (영어)
            width: 이미지 너비
            height: 이미지 높이
            num_outputs: 생성할 이미지 수
            guidance_scale: 프롬프트 가이던스 강도
            num_inference_steps: 추론 스텝 수
            max_retries: 최대 재시도 횟수
            save_local: 로컬에 저장 여부

        Returns:
            {
                "original_url": "Replicate 원본 URL",
                "local_url": "로컬 저장된 이미지 URL (save_local=True인 경우)",
                "file_path": "로컬 파일 경로 (save_local=True인 경우)"
            }
        """
        # 환경별 모델 선택
        model = self._get_model()

        last_error = None

        for attempt in range(max_retries):
            try:
                logger.info(f"이미지 생성 시작 (모델: {model}, 시도: {attempt + 1}/{max_retries})")
                logger.info(f"프롬프트: {prompt[:100]}...")

                # 모델별 입력 파라미터 구성
                input_params = self._build_input_params(
                    model=model,
                    prompt=prompt,
                    width=width,
                    height=height,
                    num_outputs=num_outputs,
                    guidance_scale=guidance_scale,
                    num_inference_steps=num_inference_steps
                )

                # Replicate API 호출
                output = self.client.run(model, input=input_params)

                # 결과 처리
                if isinstance(output, list) and len(output) > 0:
                    # FileOutput 객체를 문자열로 변환
                    original_url = str(output[0])
                    logger.info(f"✓ 이미지 생성 완료: {original_url}")

                    result = {"original_url": original_url}

                    # 로컬 저장
                    if save_local:
                        logger.info("로컬 스토리지에 이미지 저장 중...")
                        storage_result = await image_storage.download_and_save(
                            image_url=original_url,
                            optimize=True
                        )

                        if storage_result:
                            result["local_url"] = storage_result["public_url"]
                            result["file_path"] = storage_result["file_path"]
                            logger.info(f"✓ 로컬 저장 완료: {storage_result['public_url']}")
                        else:
                            logger.warning("로컬 저장 실패, 원본 URL만 반환")

                    return result
                else:
                    logger.warning(f"응답 형식 오류: {output}")
                    raise ValueError(f"예상치 못한 응답 형식: {type(output)}")

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

    def _get_model(self) -> str:
        """
        환경별 모델 선택

        개발 환경: SDXL (빠르고 저렴)
        프로덕션: Ideogram v3 Turbo (고품질)
        """
        image_mode = getattr(settings, 'IMAGE_MODE', 'development')

        if image_mode == 'production':
            # Ideogram v3 Turbo
            model = "ideogram-ai/ideogram-v2-turbo"
            logger.info("프로덕션 모드: Ideogram v3 Turbo 사용")
        else:
            # SDXL (개발 모드)
            model = "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"
            logger.info("개발 모드: SDXL 사용")

        return model

    def _build_input_params(
        self,
        model: str,
        prompt: str,
        width: int,
        height: int,
        num_outputs: int,
        guidance_scale: float,
        num_inference_steps: int
    ) -> dict:
        """
        모델별 입력 파라미터 구성

        각 모델은 파라미터 이름과 허용 값이 다르므로 적절히 변환
        """
        # SDXL
        if "sdxl" in model.lower():
            return {
                "prompt": prompt,
                "width": width,
                "height": height,
                "num_outputs": num_outputs,
                "guidance_scale": guidance_scale,
                "num_inference_steps": num_inference_steps,
                "scheduler": "K_EULER",
                "refine": "expert_ensemble_refiner",
                "high_noise_frac": 0.8,
            }

        # Ideogram v3 Turbo
        elif "ideogram" in model.lower():
            return {
                "prompt": prompt,
                "aspect_ratio": self._get_aspect_ratio(width, height),
                "magic_prompt_option": "Auto",  # 프롬프트 자동 향상
                "style_type": "Auto",
            }

        # 기본값
        else:
            return {
                "prompt": prompt,
                "width": width,
                "height": height,
            }

    def _get_aspect_ratio(self, width: int, height: int) -> str:
        """
        Ideogram용 aspect ratio 계산

        Ideogram은 width/height 대신 aspect_ratio 문자열 사용
        """
        ratio = width / height

        if abs(ratio - 1.0) < 0.1:
            return "1:1"
        elif abs(ratio - 16/9) < 0.1:
            return "16:9"
        elif abs(ratio - 9/16) < 0.1:
            return "9:16"
        elif abs(ratio - 4/3) < 0.1:
            return "4:3"
        elif abs(ratio - 3/4) < 0.1:
            return "3:4"
        else:
            return "1:1"  # 기본값


# 싱글톤 인스턴스
replicate_service = ReplicateService()
