"""
통합 콘텐츠 생성 API
전략 → 카피 → 이미지 프롬프트 → 이미지 생성을 한 번에 처리
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import logging
import time

from app.schemas.content import (
    FullContentGenerationRequest,
    FullContentGenerationResponse
)
from app.services.gemini_service import gemini_service
from app.services.nanobanana_service import nanobanana_service
from app.services.replicate_service import replicate_service
from app.models.content import Content, ContentStatus
from app.models.base import get_db
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/content", tags=["content-generation"])


@router.post(
    "/generate",
    response_model=FullContentGenerationResponse,
    summary="통합 콘텐츠 생성",
    description="전략, 카피, 이미지를 한 번에 생성합니다"
)
async def generate_full_content(
    request: FullContentGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    전체 콘텐츠 생성 파이프라인

    1. 마케팅 전략 3가지 생성
    2. 선택된 전략으로 카피 생성
    3. 카피를 이미지 프롬프트로 변환
    4. 이미지 생성 및 저장
    5. (옵션) 데이터베이스에 저장

    **예상 시간**: 30-40초
    """
    start_time = time.time()

    try:
        logger.info(f"통합 콘텐츠 생성 시작: {request.product_name}")

        # === 1단계: 마케팅 전략 생성 ===
        logger.info("1/4 마케팅 전략 생성 중...")
        strategies = await gemini_service.generate_marketing_strategies(
            product_name=request.product_name,
            product_description=request.product_description,
            category=request.category,
            target_age=request.target_age,
            target_gender=request.target_gender,
            target_interests=request.target_interests
        )

        # 전략 선택 (사용자 지정 또는 첫 번째 전략)
        selected_strategy_id = request.strategy_id or 1

        # 디버그: strategies 타입 확인
        logger.info(f"strategies 타입: {type(strategies)}, 길이: {len(strategies)}")

        selected_strategy = next(
            (s for s in strategies if s["id"] == selected_strategy_id),
            strategies[0]
        )

        # 디버그: selected_strategy 타입 확인
        logger.info(f"selected_strategy 타입: {type(selected_strategy)}")

        logger.info(f"✓ 전략 생성 완료 (선택: {selected_strategy.get('name', 'Unknown')})")

        # === 2단계: 카피 생성 ===
        logger.info("2/4 카피 생성 중...")
        copies = await gemini_service.generate_copies(
            product_name=request.product_name,
            product_description=request.product_description,
            strategy=selected_strategy,
            target_age=request.target_age,
            target_gender=request.target_gender,
            target_interests=request.target_interests
        )

        # 요청된 톤의 카피 선택
        selected_copy = next(
            (c for c in copies if c["tone"] == request.copy_tone),
            copies[0]  # 없으면 첫 번째
        )

        logger.info(f"✓ 카피 생성 완료 ({selected_copy['tone']})")

        # === 3단계: 이미지 프롬프트 변환 ===
        logger.info("3/4 이미지 프롬프트 변환 중...")
        image_prompt = await gemini_service.convert_to_image_prompt(
            copy_text=selected_copy["text"],
            product_name=request.product_name,
            target_age=request.target_age,
            target_gender=request.target_gender,
            strategy=selected_strategy
        )

        logger.info(f"✓ 이미지 프롬프트 생성 완료")

        # === 4단계: 이미지 생성 ===
        logger.info("4/4 이미지 생성 중...")

        # IMAGE_PROVIDER 환경변수에 따라 이미지 생성 서비스 선택
        image_provider = settings.IMAGE_PROVIDER.lower()

        if image_provider == "nanobanana":
            logger.info("이미지 생성 서비스: Nano Banana (Gemini 2.5 Flash Image)")
            image_result = await nanobanana_service.generate_image(
                prompt=image_prompt,
                width=1024,
                height=1024,
                save_local=True
            )
            provider_name = "nanobanana"
        else:
            # 기본값: replicate
            logger.info("이미지 생성 서비스: Replicate (SDXL/Ideogram)")
            image_result = await replicate_service.generate_image(
                prompt=image_prompt,
                width=1024,
                height=1024,
                save_local=True
            )
            provider_name = "replicate"

        logger.info(f"✓ 이미지 생성 완료 (provider: {provider_name})")

        # === 생성 시간 계산 ===
        generation_time = int(time.time() - start_time)

        # === 5단계: 데이터베이스 저장 (옵션) ===
        content_id = None
        if request.save_to_db:
            try:
                content = Content(
                    project_id=request.project_id,
                    target_age_group=request.target_age,
                    target_gender=request.target_gender,
                    target_income_level=request.target_income_level,
                    target_interests=request.target_interests,
                    strategy=selected_strategy,
                    copy_text=selected_copy["text"],
                    copy_tone=selected_copy["tone"],
                    hashtags=selected_copy.get("hashtags", []),
                    image_prompt=image_prompt,
                    image_url=image_result.get("local_url") or image_result["original_url"],
                    image_provider=provider_name,
                    status=ContentStatus.COMPLETED,
                    generation_time=generation_time
                )

                db.add(content)
                db.commit()
                db.refresh(content)
                content_id = content.id

                logger.info(f"✓ 데이터베이스 저장 완료 (ID: {content_id})")
            except Exception as e:
                logger.error(f"데이터베이스 저장 실패: {str(e)}")
                db.rollback()
                # 저장 실패해도 생성된 콘텐츠는 반환

        # === 응답 구성 ===
        response_data = {
            "content_id": content_id,
            "strategies": strategies,
            "selected_strategy_id": selected_strategy_id,
            "selected_strategy": selected_strategy,
            "copy": {
                "text": selected_copy["text"],
                "tone": selected_copy["tone"],
                "hashtags": selected_copy.get("hashtags", []),
                "length": selected_copy.get("length")
            },
            "image": {
                "prompt": image_prompt,
                "original_url": image_result["original_url"],
                "local_url": image_result.get("local_url"),
                "file_path": image_result.get("file_path")
            }
        }

        logger.info(f"✅ 통합 콘텐츠 생성 완료 (소요 시간: {generation_time}초)")

        return FullContentGenerationResponse(
            success=True,
            data=response_data,
            message=f"콘텐츠 생성 완료 (소요 시간: {generation_time}초)",
            generation_time=generation_time
        )

    except Exception as e:
        import traceback
        logger.error(f"통합 콘텐츠 생성 실패: {str(e)}")
        logger.error(traceback.format_exc())

        # 실패 시 DB에 오류 기록 (save_to_db=True인 경우)
        if request.save_to_db and request.project_id:
            try:
                failed_content = Content(
                    project_id=request.project_id,
                    target_age_group=request.target_age,
                    target_gender=request.target_gender,
                    status=ContentStatus.FAILED,
                    error_message=str(e),
                    generation_time=int(time.time() - start_time)
                )
                db.add(failed_content)
                db.commit()
            except:
                db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"콘텐츠 생성 중 오류가 발생했습니다: {str(e)}"
        )
