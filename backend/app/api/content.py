"""
콘텐츠 생성 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException
from app.schemas.content import (
    StrategyRequest, StrategyResponse,
    CopyRequest, CopyResponse,
    ImagePromptRequest, ImagePromptResponse,
    ImageGenerationRequest, ImageGenerationResponse,
    ErrorResponse, Strategy, Copy
)
from app.services.gemini_service import gemini_service
from app.services.replicate_service import replicate_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/content", tags=["content"])


@router.post(
    "/strategy",
    response_model=StrategyResponse,
    summary="마케팅 전략 생성",
    description="제품과 타겟 정보를 기반으로 3가지 마케팅 전략을 생성합니다."
)
async def generate_strategy(request: StrategyRequest):
    """
    마케팅 전략 3가지 생성

    - **감성적 전략**: 감정에 호소하는 스토리텔링
    - **이성적 전략**: 기능과 효능 강조
    - **사회적 전략**: 트렌드와 사회적 가치 강조
    """
    try:
        logger.info(f"전략 생성 요청: {request.product_name}")

        strategies = await gemini_service.generate_marketing_strategies(
            product_name=request.product_name,
            product_description=request.product_description,
            category=request.category,
            target_age=request.target_age,
            target_gender=request.target_gender,
            target_interests=request.target_interests
        )

        # Pydantic 모델로 변환
        strategy_models = [Strategy(**s) for s in strategies]

        return StrategyResponse(
            success=True,
            data=strategy_models,
            message="전략 생성 완료"
        )

    except Exception as e:
        logger.error(f"전략 생성 실패: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"전략 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.post(
    "/copy",
    response_model=CopyResponse,
    summary="광고 카피 생성",
    description="전략을 기반으로 3가지 톤의 광고 카피를 생성합니다."
)
async def generate_copy(request: CopyRequest):
    """
    광고 카피 3가지 톤으로 생성

    - **Professional**: 격식 있고 전문적인 톤 (40-50자)
    - **Casual**: 친근하고 편안한 톤 (30-40자)
    - **Impact**: 짧고 강렬한 톤 (15-25자)
    """
    try:
        logger.info(f"카피 생성 요청: {request.product_name}")

        copies = await gemini_service.generate_copies(
            product_name=request.product_name,
            product_description=request.product_description,
            strategy=request.strategy.model_dump(),
            target_age=request.target_age,
            target_gender=request.target_gender,
            target_interests=request.target_interests
        )

        # Pydantic 모델로 변환
        copy_models = [Copy(**c) for c in copies]

        return CopyResponse(
            success=True,
            data=copy_models,
            message="카피 생성 완료"
        )

    except Exception as e:
        logger.error(f"카피 생성 실패: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"카피 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.post(
    "/image-prompt",
    response_model=ImagePromptResponse,
    summary="이미지 프롬프트 생성",
    description="광고 카피를 이미지 생성 프롬프트로 변환합니다."
)
async def generate_image_prompt(request: ImagePromptRequest):
    """
    카피를 이미지 생성 프롬프트로 변환

    반환되는 프롬프트는 영어로 작성되며,
    Replicate API(SDXL, Ideogram)에서 바로 사용 가능합니다.
    """
    try:
        logger.info(f"이미지 프롬프트 생성 요청: {request.copy_text[:30]}...")

        image_prompt = await gemini_service.convert_to_image_prompt(
            copy_text=request.copy_text,
            product_name=request.product_name,
            target_age=request.target_age,
            target_gender=request.target_gender,
            strategy=request.strategy.model_dump()
        )

        return ImagePromptResponse(
            success=True,
            data=image_prompt,
            message="이미지 프롬프트 생성 완료"
        )

    except Exception as e:
        logger.error(f"이미지 프롬프트 생성 실패: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"이미지 프롬프트 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.post(
    "/image",
    response_model=ImageGenerationResponse,
    summary="이미지 생성",
    description="Replicate API를 사용하여 이미지를 생성합니다 (SDXL 또는 Ideogram v3 Turbo)"
)
async def generate_image(request: ImageGenerationRequest):
    """
    이미지 생성

    환경별 모델 자동 선택:
    - **개발 모드**: SDXL (빠르고 저렴)
    - **프로덕션**: Ideogram v3 Turbo (고품질)
    """
    try:
        logger.info(f"이미지 생성 요청: {request.image_prompt[:50]}...")

        result = await replicate_service.generate_image(
            prompt=request.image_prompt,
            width=request.width,
            height=request.height,
            save_local=True  # 로컬에 저장
        )

        return ImageGenerationResponse(
            success=True,
            data=result,
            message="이미지 생성 및 저장 완료"
        )

    except Exception as e:
        logger.error(f"이미지 생성 실패: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"이미지 생성 중 오류가 발생했습니다: {str(e)}"
        )
