"""
통합 콘텐츠 생성 API
전략 → 카피 → 이미지 프롬프트 → 이미지 생성을 한 번에 처리
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import logging
import time
import json
import asyncio
from typing import AsyncGenerator

from app.schemas.content import (
    FullContentGenerationRequest,
    FullContentGenerationResponse
)
from app.services.gemini_service import gemini_service
from app.services.nanobanana_service import nanobanana_service
from app.services.replicate_service import replicate_service
from app.services.vector_service import vector_service
from app.models.content import Content, ContentStatus
from app.models.user import User
from app.models.base import get_db
from app.utils.auth import get_current_user
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    전체 콘텐츠 생성 파이프라인

    **인증 필요**: 로그인한 사용자만 사용 가능

    1. 마케팅 전략 3가지 생성
    2. 선택된 전략으로 카피 생성
    3. 카피를 이미지 프롬프트로 변환
    4. 이미지 생성 및 저장
    5. 데이터베이스에 저장 (사용자 ID 포함)

    **예상 시간**: 30-40초
    """
    start_time = time.time()

    try:
        logger.info(f"통합 콘텐츠 생성 시작: {request.product_name}")

        # === regenerate_type 처리 ===
        if request.regenerate_type:
            logger.info(f"재생성 요청: {request.regenerate_type}")

            # auto인 경우 사용자 의도 분석
            if request.regenerate_type == "auto" and request.custom_request:
                logger.info(f"사용자 요청 분석 중: {request.custom_request}")
                intent_analysis = await gemini_service.analyze_user_intent(request.custom_request)
                logger.info(f"분석 결과: {intent_analysis}")

                # 분석 결과에 따라 regenerate_type 변경
                request.regenerate_type = intent_analysis.get("type", "all")
                logger.info(f"재생성 타입 결정: {request.regenerate_type}")

        # 다중 타겟을 문자열로 변환 (빈 배열이면 "AI 자동 분석"으로 표시)
        if len(request.target_ages) > 1:
            target_age_str = ", ".join(request.target_ages)
        elif len(request.target_ages) == 1:
            target_age_str = request.target_ages[0]
        else:
            target_age_str = "AI 자동 분석"

        if len(request.target_genders) > 1:
            target_gender_str = ", ".join(request.target_genders)
        elif len(request.target_genders) == 1:
            target_gender_str = request.target_genders[0]
        else:
            target_gender_str = "무관"

        logger.info(f"카테고리: {request.category} / 타겟: {target_age_str} / {target_gender_str}")

        # === 0단계: AI 타겟 인사이트 분석 ===
        logger.info("0/5 AI 타겟 인사이트 분석 중...")
        target_insights = await gemini_service.analyze_target_insights(
            product_name=request.product_name,
            product_description=request.product_description,
            category=request.category,
            target_ages=request.target_ages,
            target_genders=request.target_genders,
            target_interests=request.target_interests
        )
        logger.info(f"✓ 타겟 인사이트 분석 완료")
        logger.info(f"  - Target Ages: {len(target_insights.get('target_ages', []))}개")
        logger.info(f"  - Target Interests: {len(target_insights.get('target_interests', []))}개")
        logger.info(f"  - Pain Points: {len(target_insights.get('pain_points', []))}개")
        logger.info(f"  - Preferred Channels: {len(target_insights.get('preferred_channels', []))}개")

        # AI가 생성한 연령대 사용 (비어있었다면)
        final_target_ages = target_insights.get('target_ages', request.target_ages) if not request.target_ages or len(request.target_ages) == 0 else request.target_ages
        # AI가 생성한 관심사를 사용 (비어있었다면)
        final_target_interests = target_insights.get('target_interests', request.target_interests) if not request.target_interests or len(request.target_interests) == 0 else request.target_interests

        # 연령대 문자열 생성 (AI가 생성한 연령대 사용)
        target_age_str = ", ".join(final_target_ages) if len(final_target_ages) > 1 else final_target_ages[0] if final_target_ages else "20-29"

        # === RAG: 과거 유사 콘텐츠 성과 검색 ===
        past_performance = []
        try:
            logger.info("📊 RAG: 유사 콘텐츠 성과 검색 중...")
            # 검색 쿼리 생성 (제품 설명 + 카테고리)
            query_text = f"제품: {request.product_name}\n설명: {request.product_description}\n카테고리: {request.category}"

            past_performance = vector_service.get_performance_reference(
                query_text=query_text,
                target_age=target_age_str if len(final_target_ages) == 1 else None,  # 단일 연령대만 필터링
                target_gender=target_gender_str if target_gender_str != "무관" else None,
                category=request.category,
                limit=3  # 최대 3개 참조
            )

            if past_performance:
                logger.info(f"✓ RAG: {len(past_performance)}개 유사 콘텐츠 발견")
                for i, perf in enumerate(past_performance, 1):
                    logger.info(f"  {i}. 유사도: {perf['similarity_score']:.2f}, 성과: 도달 {perf['performance']['impressions']:,}명")
            else:
                logger.info("  RAG: 유사 콘텐츠 없음 (첫 콘텐츠 또는 유사도 낮음)")
        except Exception as e:
            logger.warning(f"⚠️  RAG 검색 실패 (계속 진행): {str(e)}")
            past_performance = []

        # === 1단계: 마케팅 전략 생성 (RAG 활용) ===
        logger.info("1/5 마케팅 전략 생성 중...")
        strategies = await gemini_service.generate_marketing_strategies(
            product_name=request.product_name,
            product_description=request.product_description,
            category=request.category,
            target_age=target_age_str,
            target_gender=target_gender_str,
            target_interests=final_target_interests,
            past_performance=past_performance  # RAG 데이터 전달
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

        # === 2단계: 카피 생성 (regenerate_type이 'image'가 아닐 때만) ===
        if request.regenerate_type != "image":
            logger.info(f"2/5 카피 생성 중... (톤: {request.copy_tone})")
            copies = await gemini_service.generate_copies(
                product_name=request.product_name,
                product_description=request.product_description,
                strategy=selected_strategy,
                target_age=target_age_str,
                target_gender=target_gender_str,
                target_interests=final_target_interests,
                copy_tone=request.copy_tone  # 요청된 톤 전달
            )

            # 첫 번째 카피 사용 (이제 하나만 생성됨)
            selected_copy = copies[0]

            logger.info(f"✓ 카피 생성 완료 ({selected_copy['tone']})")
        else:
            # 이미지만 재생성 - 기존 카피 유지 (임시로 빈 카피)
            logger.info("2/5 카피 생성 스킵 (이미지만 재생성)")
            selected_copy = {"text": "", "tone": request.copy_tone, "hashtags": [], "length": 0}

        # === 3단계: 이미지 프롬프트 변환 (regenerate_type이 'copy'가 아닐 때만) ===
        if request.regenerate_type != "copy":
            logger.info("3/5 이미지 프롬프트 변환 중...")
            image_prompt = await gemini_service.convert_to_image_prompt(
                copy_text=selected_copy["text"] if selected_copy["text"] else request.product_description,
                product_name=request.product_name,
                target_age=target_age_str,
                target_gender=target_gender_str,
                strategy=selected_strategy
            )

            logger.info(f"✓ 이미지 프롬프트 생성 완료")
        else:
            # 카피만 재생성 - 이미지 생성 스킵
            logger.info("3/5 이미지 프롬프트 변환 스킵 (카피만 재생성)")
            image_prompt = None

        # === 4단계: 이미지 생성 (regenerate_type이 'copy'가 아닐 때만) ===
        if request.regenerate_type != "copy" and image_prompt:
            logger.info("4/5 이미지 생성 중...")

            # IMAGE_PROVIDER 환경변수에 따라 이미지 생성 서비스 선택
            image_provider = settings.IMAGE_PROVIDER.lower()

            # 제품 이미지가 있으면 제품 기반 마케팅 이미지 생성
            if request.product_image_path:
                import os
                if os.path.exists(request.product_image_path):
                    logger.info(f"제품 이미지 기반 마케팅 이미지 생성 모드")
                    logger.info(f"제품 이미지 경로: {request.product_image_path}")

                    # 제품 이미지 기반 마케팅 프롬프트 생성
                    marketing_prompt = await gemini_service.generate_text(
                        f"""You will see a product image. Create a new marketing image that includes this EXACT product.

Product: {request.product_name}
Description: {request.product_description}
Target Audience: {target_age_str}, {target_gender_str}
Marketing Strategy: {selected_strategy.get('name', '')} - {selected_strategy.get('core_message', '')}

CRITICAL RULE: The product itself (design, color, shape, branding) MUST remain EXACTLY as shown in the provided image. Do not change the product at all.

Generate a complete marketing scene that features this product:
- A person holding, wearing, or using the product
- The product placed in an attractive lifestyle setting
- A professional product showcase with appropriate background

Focus on:
- Keeping the product identical to the reference image
- Natural composition and lighting
- Authentic human features (hands, face) if people are included
- Professional photography style
- Matching the target audience's preferences

Generate a photorealistic marketing scene with the EXACT product from the image.""",
                        temperature=0.5
                    )

                    logger.info(f"마케팅 프롬프트: {marketing_prompt[:100]}...")

                    # Gemini로 제품 이미지 기반 마케팅 이미지 생성
                    image_result = await nanobanana_service.generate_from_product_image(
                        product_image_path=request.product_image_path,
                        prompt=marketing_prompt,
                        save_local=True
                    )
                    provider_name = "nanobanana (product-based)"
                    logger.info(f"✓ 제품 이미지 기반 마케팅 이미지 생성 완료")
                else:
                    logger.warning(f"제품 이미지 파일을 찾을 수 없음: {request.product_image_path}")
                    logger.info("일반 이미지 생성으로 대체")
                    # 파일이 없으면 일반 이미지 생성으로 대체
                    if image_provider == "nanobanana":
                        image_result = await nanobanana_service.generate_image(
                            prompt=image_prompt,
                            width=1024,
                            height=1024,
                            save_local=True
                        )
                        provider_name = "nanobanana"
                    else:
                        image_result = await replicate_service.generate_image(
                            prompt=image_prompt,
                            width=1024,
                            height=1024,
                            save_local=True
                        )
                        provider_name = "replicate"
            else:
                # 제품 이미지가 없으면 일반 이미지 생성
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
        else:
            # 카피만 재생성 - 이미지 없음 (임시 데이터)
            logger.info("4/5 이미지 생성 스킵 (카피만 재생성)")
            image_result = {"original_url": "", "local_url": None}
            provider_name = "none"

        # === 생성 시간 계산 ===
        generation_time = int(time.time() - start_time)

        # === 5단계: 데이터베이스 저장 (항상 저장) ===
        content_id = None
        try:
            content = Content(
                user_id=current_user.id,  # 로그인한 사용자 ID
                project_id=request.project_id,
                product_name=request.product_name,
                product_description=request.product_description,
                category=request.category,
                target_age_group=target_age_str,
                target_gender=target_gender_str,
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

            # === Vector DB 저장 (임베딩 생성 및 저장) ===
            try:
                logger.info(f"Vector DB 저장 중... (content_id: {content_id})")
                vector_success = vector_service.save_content_embedding(
                    content_id=content_id,
                    copy_text=selected_copy["text"],
                    image_prompt=image_prompt,
                    metadata={
                        "target_age": target_age_str,
                        "target_gender": target_gender_str,
                        "category": request.category,
                        "product_name": request.product_name,
                        "strategy_name": selected_strategy.get("name", ""),
                        "copy_tone": selected_copy["tone"]
                    }
                )
                if vector_success:
                    logger.info(f"✓ Vector DB 저장 완료 (content_id: {content_id})")
                else:
                    logger.warning(f"⚠️  Vector DB 저장 실패 (content_id: {content_id})")
            except Exception as ve:
                logger.error(f"Vector DB 저장 에러: {str(ve)}")
                # Vector DB 저장 실패해도 전체 프로세스는 계속 진행

            # === 성과 예측 자동 실행 ===
            # 성과 예측 실행 및 결과 가져오기
            performance_data = None
            try:
                logger.info(f"성과 예측 시작... (content_id: {content_id})")
                from app.services.performance_service import PerformanceService
                performance_service = PerformanceService(db)

                # 비동기로 성과 예측 실행
                performance = await performance_service.predict_performance(content_id)

                if performance:
                    logger.info(f"✓ 성과 예측 완료 (content_id: {content_id})")
                    # 성과 예측 결과를 딕셔너리로 변환
                    performance_data = {
                        "impressions": performance.impressions,
                        "clicks": performance.clicks,
                        "ctr": performance.ctr,
                        "engagement_rate": performance.engagement_rate,
                        "conversion_rate": performance.conversion_rate,
                        "brand_recall_score": performance.brand_recall_score,
                        "confidence_score": performance.confidence_score
                    }
                else:
                    logger.warning(f"⚠️  성과 예측 실패 (content_id: {content_id})")
            except Exception as pe:
                logger.error(f"성과 예측 에러: {str(pe)}")
                # 성과 예측 실패해도 전체 프로세스는 계속 진행

        except Exception as e:
            logger.error(f"데이터베이스 저장 실패: {str(e)}")
            db.rollback()
            # 저장 실패해도 생성된 콘텐츠는 반환

        # === 응답 구성 ===
        response_data = {
            "content_id": content_id,
            "target_insights": target_insights,  # AI 분석 인사이트 추가
            # 타겟 세그먼트 정보 추가
            "target_age_group": target_age_str,
            "target_gender": target_gender_str,
            "target_ages": final_target_ages,  # AI가 생성한 연령대 또는 사용자 입력
            "target_genders": request.target_genders,
            "target_interests": final_target_interests,  # AI가 생성한 관심사 또는 사용자 입력
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
            },
            "performance_prediction": performance_data  # 성과 예측 데이터 추가
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
                # target_age_str와 target_gender_str이 정의되지 않았을 수 있으므로 체크
                try:
                    age_str = target_age_str
                    gender_str = target_gender_str
                except NameError:
                    age_str = ", ".join(request.target_ages) if len(request.target_ages) > 1 else request.target_ages[0]
                    gender_str = ", ".join(request.target_genders) if len(request.target_genders) > 1 else request.target_genders[0]

                failed_content = Content(
                    project_id=request.project_id,
                    target_age_group=age_str,
                    target_gender=gender_str,
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


@router.post(
    "/regenerate/image",
    response_model=FullContentGenerationResponse,
    summary="이미지만 재생성",
    description="기존 콘텐츠의 카피는 유지하고 이미지만 새로 생성합니다"
)
async def regenerate_image_only(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    이미지만 재생성
    - 기존 카피, 전략, 타겟 정보 유지
    - 이미지만 새로 생성
    """
    start_time = time.time()

    try:
        logger.info(f"=== 이미지 재생성 시작 (사용자: {current_user.email}) ===")

        # 사용자의 커스텀 요청 확인
        custom_request = request.get('customPrompt') or request.get('custom_request')
        logger.info(f"🔍 받은 customPrompt: {custom_request}")

        # 기존 데이터 가져오기
        copy_data = request.get('copy', {})
        existing_copy = copy_data.get('text', '')
        product_name = request.get('product_name', '')

        # 전략 정보
        selected_strategy = request.get('selected_strategy', {})

        # 타겟 정보
        target_ages = request.get('target_ages', [])
        target_genders = request.get('target_genders', [])
        target_age_str = ", ".join(target_ages) if target_ages else "20-29"
        target_gender_str = ", ".join(target_genders) if target_genders else "여성"

        # 커스텀 요청이 있으면 기존 프롬프트 기반으로 수정
        if custom_request:
            logger.info(f"✓ 사용자 커스텀 요청: {custom_request}")

            # 기존 이미지 프롬프트 가져오기
            existing_image_prompt = request.get('image', {}).get('prompt', '')

            if existing_image_prompt:
                # 기존 프롬프트를 유지하면서 커스텀 요청만 반영
                logger.info(f"✓ 기존 이미지 프롬프트 활용: {existing_image_prompt[:100]}...")

                modification_instruction = f"""
You are an expert at modifying image generation prompts while maintaining consistency.

ORIGINAL PROMPT:
{existing_image_prompt}

USER'S MODIFICATION REQUEST (Korean):
{custom_request}

TASK:
Modify ONLY the specific elements mentioned in the user's request while keeping everything else EXACTLY the same.
- If the user wants to change the product design, modify only the product description
- If the user wants to change colors, modify only color-related terms
- Keep the same composition, lighting, background, model pose, and all other unchanged elements
- Maintain the same professional photography style and quality markers

OUTPUT:
Return the modified prompt in English, maintaining the same structure and detail level as the original.
DO NOT add explanations - output ONLY the modified prompt.
"""

                image_prompt = await gemini_service.generate_text(modification_instruction, temperature=0.3)
                logger.info(f"✓ 기존 프롬프트 기반 수정 완료")
            else:
                # 기존 프롬프트가 없으면 새로 생성
                logger.info(f"✓ 기존 프롬프트 없음 - 새로 생성")
                enhanced_copy = f"{existing_copy}. {custom_request}"
                image_prompt = await gemini_service.convert_to_image_prompt(
                    copy_text=enhanced_copy,
                    product_name=product_name,
                    target_age=target_age_str,
                    target_gender=target_gender_str,
                    strategy=selected_strategy
                )

            logger.info(f"✓ 커스텀 요청 반영한 프롬프트 생성 완료")
        else:
            # 커스텀 요청 없으면 기존 카피로 새 프롬프트 재생성 (품질 개선 적용)
            logger.info(f"✓ 기존 카피로 새 프롬프트 재생성 중...")

            image_prompt = await gemini_service.convert_to_image_prompt(
                copy_text=existing_copy,
                product_name=product_name,
                target_age=target_age_str,
                target_gender=target_gender_str,
                strategy=selected_strategy
            )
            logger.info(f"✓ 개선된 프롬프트 생성 완료")

        logger.info(f"✓ 이미지 생성 중...")

        # IMAGE_PROVIDER 환경변수에 따라 이미지 생성 서비스 선택
        image_provider = settings.IMAGE_PROVIDER.lower()

        # 제품 이미지 경로 확인
        product_image_path = request.get('product_image_path')

        # 제품 이미지가 있으면 제품 기반 마케팅 이미지 생성
        if product_image_path:
            import os
            if os.path.exists(product_image_path):
                logger.info(f"제품 이미지 기반 재생성 모드")
                logger.info(f"제품 이미지 경로: {product_image_path}")

                # 제품 이미지 기반 마케팅 프롬프트 생성
                marketing_prompt = await gemini_service.generate_text(
                    f"""You will see a product image. Create a new marketing image that includes this EXACT product.

Product: {product_name}
Target Audience: {target_age_str}, {target_gender_str}
Strategy: {selected_strategy.get('name', '')}

User's specific modification request:
{custom_request if custom_request else 'Create a natural marketing scene with this product'}

CRITICAL RULES:
1. The product itself (its design, color, shape, brand) MUST remain EXACTLY the same as in the provided image
2. You can ONLY modify the elements the user specifically requested to change
3. If the user didn't mention changing the product, DO NOT change it at all
4. Keep the product recognizable and identical to the reference image

What you CAN change (only if the user requested):
- Background/setting
- Model's other clothing (not the product itself)
- Lighting and atmosphere
- Camera angle or composition
- Additional props or elements

Generate a photorealistic marketing image following these rules.""",
                    temperature=0.3
                )

                logger.info(f"마케팅 프롬프트: {marketing_prompt[:100]}...")

                # Gemini로 제품 이미지 기반 마케팅 이미지 생성
                image_result = await nanobanana_service.generate_from_product_image(
                    product_image_path=product_image_path,
                    prompt=marketing_prompt,
                    save_local=True
                )
                logger.info(f"✓ 제품 이미지 기반 마케팅 이미지 재생성 완료")
            else:
                logger.warning(f"제품 이미지 파일을 찾을 수 없음: {product_image_path}")
                logger.info("일반 이미지 생성으로 대체")
                # 파일이 없으면 일반 이미지 생성으로 대체
                if image_provider == "nanobanana":
                    image_result = await nanobanana_service.generate_image(
                        prompt=image_prompt,
                        width=1024,
                        height=1024,
                        save_local=True
                    )
                else:
                    image_result = await replicate_service.generate_image(
                        prompt=image_prompt,
                        width=1024,
                        height=1024
                    )
        else:
            # 제품 이미지가 없으면 일반 이미지 생성
            if image_provider == "nanobanana":
                logger.info("이미지 생성 서비스: Nano Banana (Gemini 2.5 Flash Image)")
                image_result = await nanobanana_service.generate_image(
                    prompt=image_prompt,
                    width=1024,
                    height=1024,
                    save_local=True
                )
            else:
                # 기본값: replicate
                logger.info("이미지 생성 서비스: Replicate (SDXL/Ideogram)")
                image_result = await replicate_service.generate_image(
                    prompt=image_prompt,
                    width=1024,
                    height=1024
                )

        generation_time = int(time.time() - start_time)

        # === DB에 새로운 콘텐츠로 저장 ===
        content_id = None
        try:
            # 기존 데이터 파싱
            copy_data = request.get('copy', {})
            category = request.get('category', 'other')
            product_description = request.get('product_description', '')
            target_interests = request.get('target_interests', [])

            content = Content(
                user_id=current_user.id,
                project_id=request.get('project_id'),
                product_name=product_name,
                product_description=product_description,
                category=category,
                target_age_group=target_age_str,
                target_gender=target_gender_str,
                target_income_level=request.get('target_income_level'),
                target_interests=target_interests,
                strategy=selected_strategy,
                copy_text=existing_copy,
                copy_tone=copy_data.get('tone', 'professional'),
                hashtags=copy_data.get('hashtags', []),
                image_prompt=image_prompt,
                image_url=image_result.get("local_url") or image_result["original_url"],
                image_provider=request.get('image_provider', 'nanobanana'),
                status=ContentStatus.COMPLETED,
                generation_time=generation_time
            )

            db.add(content)
            db.commit()
            db.refresh(content)
            content_id = content.id

            logger.info(f"✓ 재생성 콘텐츠 DB 저장 완료 (ID: {content_id})")

            # === Vector DB 저장 ===
            try:
                logger.info(f"Vector DB 저장 중... (content_id: {content_id})")
                vector_success = vector_service.save_content_embedding(
                    content_id=content_id,
                    copy_text=existing_copy,
                    image_prompt=image_prompt,
                    metadata={
                        "target_age": target_age_str,
                        "target_gender": target_gender_str,
                        "category": category,
                        "product_name": product_name,
                        "strategy_name": selected_strategy.get("name", ""),
                        "copy_tone": copy_data.get('tone', 'professional')
                    }
                )
                if vector_success:
                    logger.info(f"✓ Vector DB 저장 완료 (content_id: {content_id})")
            except Exception as ve:
                logger.error(f"Vector DB 저장 에러: {str(ve)}")

            # === 성과 예측 자동 실행 ===
            # 성과 예측 실행 및 결과 가져오기
            performance_data = None
            try:
                logger.info(f"성과 예측 시작... (content_id: {content_id})")
                from app.services.performance_service import PerformanceService
                performance_service = PerformanceService(db)

                performance = await performance_service.predict_performance(content_id)

                if performance:
                    logger.info(f"✓ 성과 예측 완료 (content_id: {content_id})")
                    # 성과 예측 결과를 딕셔너리로 변환
                    performance_data = {
                        "impressions": performance.impressions,
                        "clicks": performance.clicks,
                        "ctr": performance.ctr,
                        "engagement_rate": performance.engagement_rate,
                        "conversion_rate": performance.conversion_rate,
                        "brand_recall_score": performance.brand_recall_score,
                        "confidence_score": performance.confidence_score
                    }
            except Exception as pe:
                logger.error(f"성과 예측 에러: {str(pe)}")

        except Exception as e:
            logger.error(f"DB 저장 실패: {str(e)}")
            db.rollback()

        # 기존 데이터 유지하면서 이미지만 업데이트
        response_data = {
            "content_id": content_id,  # 새로 생성된 content_id
            "target_insights": request.get('target_insights', {}),
            "target_age_group": request.get('target_age_group', ''),
            "target_gender": request.get('target_gender', ''),
            "target_ages": request.get('target_ages', []),
            "target_genders": request.get('target_genders', []),
            "target_interests": request.get('target_interests', []),
            "strategies": request.get('strategies', []),
            "selected_strategy_id": request.get('selected_strategy_id'),
            "selected_strategy": request.get('selected_strategy', {}),
            "copy": request.get('copy', {}),  # 기존 카피 유지
            "image": {  # 새로 생성된 이미지
                "prompt": image_prompt,
                "original_url": image_result["original_url"],
                "local_url": image_result.get("local_url"),
                "file_path": image_result.get("file_path")
            },
            "performance_prediction": performance_data  # 성과 예측 데이터 추가
        }

        logger.info(f"✅ 이미지 재생성 완료 (소요 시간: {generation_time}초)")

        return FullContentGenerationResponse(
            success=True,
            data=response_data,
            message="이미지 재생성 완료",
            generation_time=generation_time
        )

    except Exception as e:
        import traceback
        logger.error(f"이미지 재생성 실패: {str(e)}")
        logger.error(traceback.format_exc())

        raise HTTPException(
            status_code=500,
            detail=f"이미지 재생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.post(
    "/regenerate/copy",
    response_model=FullContentGenerationResponse,
    summary="카피만 재생성",
    description="기존 콘텐츠의 이미지는 유지하고 카피만 새로 생성합니다"
)
async def regenerate_copy_only(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    카피만 재생성
    - 기존 이미지, 타겟 정보 유지
    - 카피만 새로운 톤으로 재생성
    """
    start_time = time.time()

    try:
        logger.info(f"=== 카피 재생성 시작 (사용자: {current_user.email}) ===")

        product_name = request.get('product_name', '')
        product_description = request.get('product_description', '')
        copy_tone = request.get('copy_tone', 'professional')
        strategy_name = request.get('strategy_name', '')
        core_message = request.get('core_message', '')
        target_ages = request.get('target_ages', [])
        target_genders = request.get('target_genders', [])
        target_interests = request.get('target_interests', [])

        # 타겟 정보 문자열 생성
        target_age_str = ", ".join(target_ages) if len(target_ages) > 1 else target_ages[0] if target_ages else "20-29"
        target_gender_str = ", ".join(target_genders) if len(target_genders) > 1 else target_genders[0] if target_genders else "여성"

        logger.info(f"✓ 새로운 톤({copy_tone})으로 카피 생성 중...")

        # 기존 전략 정보로 strategy dict 구성
        strategy_dict = {
            "id": request.get('selected_strategy_id', 1),
            "name": strategy_name,
            "core_message": core_message,
            "emotion": request.get('selected_strategy', {}).get('emotion', '감성적'),
            "expected_effect": request.get('selected_strategy', {}).get('expected_effect', '')
        }

        # 카피 재생성
        copies_data = await gemini_service.generate_copies(
            product_name=product_name,
            product_description=product_description,
            strategy=strategy_dict,
            target_age=target_age_str,
            target_gender=target_gender_str,
            target_interests=target_interests,
            copy_tone=copy_tone
        )

        # 요청된 톤의 카피 선택
        selected_copy = next(
            (c for c in copies_data if c['tone'] == copy_tone),
            copies_data[0] if copies_data else None
        )

        if not selected_copy:
            raise ValueError(f"톤 '{copy_tone}'의 카피를 생성하지 못했습니다")

        generation_time = int(time.time() - start_time)

        # === DB에 새로운 콘텐츠로 저장 ===
        content_id = None
        try:
            # 기존 이미지 정보
            image_data = request.get('image', {})
            category = request.get('category', 'other')

            content = Content(
                user_id=current_user.id,
                project_id=request.get('project_id'),
                product_name=product_name,
                product_description=product_description,
                category=category,
                target_age_group=target_age_str,
                target_gender=target_gender_str,
                target_income_level=request.get('target_income_level'),
                target_interests=target_interests,
                strategy=strategy_dict,
                copy_text=selected_copy["text"],
                copy_tone=selected_copy["tone"],
                hashtags=selected_copy.get("hashtags", []),
                image_prompt=image_data.get('prompt', ''),
                image_url=image_data.get('local_url') or image_data.get('original_url', ''),
                image_provider=request.get('image_provider', 'nanobanana'),
                status=ContentStatus.COMPLETED,
                generation_time=generation_time
            )

            db.add(content)
            db.commit()
            db.refresh(content)
            content_id = content.id

            logger.info(f"✓ 재생성 콘텐츠 DB 저장 완료 (ID: {content_id})")

            # === Vector DB 저장 ===
            try:
                logger.info(f"Vector DB 저장 중... (content_id: {content_id})")
                vector_success = vector_service.save_content_embedding(
                    content_id=content_id,
                    copy_text=selected_copy["text"],
                    image_prompt=image_data.get('prompt', ''),
                    metadata={
                        "target_age": target_age_str,
                        "target_gender": target_gender_str,
                        "category": category,
                        "product_name": product_name,
                        "strategy_name": strategy_name,
                        "copy_tone": selected_copy["tone"]
                    }
                )
                if vector_success:
                    logger.info(f"✓ Vector DB 저장 완료 (content_id: {content_id})")
            except Exception as ve:
                logger.error(f"Vector DB 저장 에러: {str(ve)}")

            # === 성과 예측 자동 실행 ===
            # 성과 예측 실행 및 결과 가져오기
            performance_data = None
            try:
                logger.info(f"성과 예측 시작... (content_id: {content_id})")
                from app.services.performance_service import PerformanceService
                performance_service = PerformanceService(db)

                performance = await performance_service.predict_performance(content_id)

                if performance:
                    logger.info(f"✓ 성과 예측 완료 (content_id: {content_id})")
                    # 성과 예측 결과를 딕셔너리로 변환
                    performance_data = {
                        "impressions": performance.impressions,
                        "clicks": performance.clicks,
                        "ctr": performance.ctr,
                        "engagement_rate": performance.engagement_rate,
                        "conversion_rate": performance.conversion_rate,
                        "brand_recall_score": performance.brand_recall_score,
                        "confidence_score": performance.confidence_score
                    }
            except Exception as pe:
                logger.error(f"성과 예측 에러: {str(pe)}")

        except Exception as e:
            logger.error(f"DB 저장 실패: {str(e)}")
            db.rollback()

        # 기존 데이터 유지하면서 카피만 업데이트
        response_data = {
            "content_id": content_id,  # 새로 생성된 content_id
            "target_insights": request.get('target_insights', {}),
            "target_age_group": target_age_str,
            "target_gender": target_gender_str,
            "target_ages": target_ages,
            "target_genders": target_genders,
            "target_interests": target_interests,
            "strategies": request.get('strategies', []),
            "selected_strategy_id": request.get('selected_strategy_id'),
            "selected_strategy": request.get('selected_strategy', {}),
            "copy": {  # 새로 생성된 카피
                "text": selected_copy["text"],
                "tone": selected_copy["tone"],
                "hashtags": selected_copy.get("hashtags", []),
                "length": selected_copy.get("length")
            },
            "image": request.get('image', {}),  # 기존 이미지 유지
            "performance_prediction": performance_data  # 성과 예측 데이터 추가
        }

        logger.info(f"✅ 카피 재생성 완료 (소요 시간: {generation_time}초)")

        return FullContentGenerationResponse(
            success=True,
            data=response_data,
            message="카피 재생성 완료",
            generation_time=generation_time
        )

    except Exception as e:
        import traceback
        logger.error(f"카피 재생성 실패: {str(e)}")
        logger.error(traceback.format_exc())

        raise HTTPException(
            status_code=500,
            detail=f"카피 재생성 중 오류가 발생했습니다: {str(e)}"
        )



# ============================================================
# SSE 스트리밍 콘텐츠 생성
# ============================================================

@router.post("/generate-stream")
async def generate_content_with_stream(
    request: FullContentGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    SSE를 사용한 실시간 진행 상태 스트리밍 콘텐츠 생성
    
    프론트엔드에서 EventSource로 연결:
    const eventSource = new EventSource('/api/content/generate-stream');
    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        // data.type: 'progress' | 'complete' | 'error'
    };
    """
    
    async def generate_with_progress():
        """진행 상태를 SSE로 전송하며 콘텐츠 생성"""
        try:
            start_time = time.time()
            
            # 진행 상태 전송 헬퍼 함수
            def send_progress(step: int, total: int, message: str):
                data = {
                    "type": "progress",
                    "step": step,
                    "total": total,
                    "message": message
                }
                return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
            
            # 시작
            yield send_progress(0, 8, "🎯 제품 정보를 분석하고 있습니다...")
            
            logger.info(f"통합 콘텐츠 생성 시작: {request.product_name}")
            
            # 타겟 문자열 변환
            if len(request.target_ages) > 1:
                target_age_str = ", ".join(request.target_ages)
            elif len(request.target_ages) == 1:
                target_age_str = request.target_ages[0]
            else:
                target_age_str = "AI 자동 분석"
            
            if len(request.target_genders) > 1:
                target_gender_str = ", ".join(request.target_genders)
            elif len(request.target_genders) == 1:
                target_gender_str = request.target_genders[0]
            else:
                target_gender_str = "무관"
            
            # 0단계: AI 타겟 인사이트 분석
            yield send_progress(1, 8, "🧠 AI가 타겟 고객을 분석하고 있습니다...")
            await asyncio.sleep(0.1)  # 메시지 전송 시간 확보

            target_insights = await gemini_service.analyze_target_insights(
                product_name=request.product_name,
                product_description=request.product_description,
                category=request.category,
                target_ages=request.target_ages,
                target_genders=request.target_genders,
                target_interests=request.target_interests
            )

            final_target_ages = target_insights.get('target_ages', request.target_ages) if not request.target_ages or len(request.target_ages) == 0 else request.target_ages
            final_target_interests = target_insights.get('target_interests', request.target_interests) if not request.target_interests or len(request.target_interests) == 0 else request.target_interests

            # 1단계: RAG 검색 + 마케팅 전략 생성
            yield send_progress(2, 8, "💡 마케팅 전략을 수립하고 있습니다...")
            await asyncio.sleep(0.1)
            
            past_performance = []
            try:
                query_text = f"제품: {request.product_name}\n설명: {request.product_description}\n카테고리: {request.category}"
                past_performance = vector_service.get_performance_reference(
                    query_text=query_text,
                    target_age=target_age_str if len(final_target_ages) == 1 else None,
                    target_gender=target_gender_str if target_gender_str != "무관" else None,
                    category=request.category,
                    limit=3
                )
            except Exception as e:
                logger.warning(f"⚠️ RAG 검색 실패 (계속 진행): {str(e)}")
            
            # 2단계: 마케팅 전략 생성
            strategies = await gemini_service.generate_marketing_strategies(
                product_name=request.product_name,
                product_description=request.product_description,
                category=request.category,
                target_age=", ".join(final_target_ages),
                target_gender=target_gender_str,
                target_interests=final_target_interests,
                past_performance=past_performance
            )
            
            selected_strategy = strategies[0] if strategies else None
            
            # 3단계: 카피 생성
            yield send_progress(3, 8, "✍️ 매력적인 카피를 작성하고 있습니다...")
            await asyncio.sleep(0.1)

            copies = await gemini_service.generate_copies(
                product_name=request.product_name,
                product_description=request.product_description,
                strategy=selected_strategy,
                target_age=", ".join(final_target_ages),
                target_gender=target_gender_str,
                target_interests=final_target_interests,
                copy_tone=request.copy_tone
            )

            selected_copy = copies[0]
            
            # 4단계: 이미지 프롬프트 생성
            yield send_progress(4, 8, "🎨 이미지 프롬프트를 생성하고 있습니다...")
            await asyncio.sleep(0.1)

            image_prompt = await gemini_service.convert_to_image_prompt(
                copy_text=selected_copy["text"],
                product_name=request.product_name,
                target_age=", ".join(final_target_ages),
                target_gender=target_gender_str,
                strategy=selected_strategy
            )
            
            # 5단계: 이미지 생성
            yield send_progress(5, 8, "🖼️ 고품질 이미지를 생성하고 있습니다...")
            await asyncio.sleep(0.1)

            # 이미지 생성 서비스 선택 (settings.IMAGE_PROVIDER)
            image_provider = settings.IMAGE_PROVIDER.lower()

            # 제품 이미지가 있으면 제품 기반 생성 시도
            if request.product_image_path:
                import os
                if os.path.exists(request.product_image_path):
                    logger.info("제품 이미지 기반 마케팅 이미지 생성 시작...")

                    # 마케팅 프롬프트 생성
                    marketing_prompt = f"{image_prompt}\n\nMust include the actual product prominently in the image."

                    # nanobanana로 제품 이미지 기반 생성
                    image_result = await nanobanana_service.generate_from_product_image(
                        product_image_path=request.product_image_path,
                        prompt=marketing_prompt,
                        save_local=True
                    )
                    provider_name = "nanobanana (product-based)"
                else:
                    logger.warning(f"제품 이미지 파일 없음, 일반 이미지 생성으로 대체")
                    if image_provider == "nanobanana":
                        image_result = await nanobanana_service.generate_image(
                            prompt=image_prompt,
                            width=1024,
                            height=1024,
                            save_local=True
                        )
                        provider_name = "nanobanana"
                    else:
                        image_result = await replicate_service.generate_image(
                            prompt=image_prompt,
                            width=1024,
                            height=1024,
                            save_local=True
                        )
                        provider_name = "replicate"
            else:
                # 제품 이미지 없으면 일반 이미지 생성
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
                    logger.info("이미지 생성 서비스: Replicate (SDXL/Ideogram)")
                    image_result = await replicate_service.generate_image(
                        prompt=image_prompt,
                        width=1024,
                        height=1024,
                        save_local=True
                    )
                    provider_name = "replicate"

            logger.info(f"✓ 이미지 생성 완료 (provider: {provider_name})")
            
            # DB 저장
            content = Content(
                user_id=current_user.id,
                product_name=request.product_name,
                product_description=request.product_description,
                category=request.category,
                target_age_group=", ".join(final_target_ages),
                target_gender=target_gender_str,
                target_interests=final_target_interests,
                strategy=selected_strategy,
                copy_text=selected_copy["text"],
                copy_tone=request.copy_tone,
                image_url=image_result.get("local_url") or image_result["original_url"],
                image_prompt=image_prompt,
                image_provider=provider_name,
                status=ContentStatus.COMPLETED
            )
            db.add(content)
            db.commit()
            db.refresh(content)
            
            # 6단계: 성과 예측
            yield send_progress(6, 8, "📊 성과를 예측하고 있습니다...")
            await asyncio.sleep(0.1)

            from app.services.performance_service import PerformanceService
            performance_service = PerformanceService(db)
            performance = await performance_service.predict_performance(content.id)

            # 7단계: Vector DB 저장
            yield send_progress(7, 8, "✨ 최종 콘텐츠를 완성하고 있습니다...")
            await asyncio.sleep(0.1)
            
            try:
                vector_service.save_content(
                    content_id=content.id,
                    copy_text=content.copy_text,
                    image_prompt=content.image_prompt,
                    target_age=content.target_age_group,
                    target_gender=content.target_gender,
                    category=content.category
                )
            except Exception as e:
                logger.error(f"Vector DB 저장 실패: {str(e)}")
            
            # 완료 - 최종 데이터 전송
            generation_time = time.time() - start_time
            
            response_data = {
                "id": content.id,
                "product_name": content.product_name,
                "strategies": strategies,
                "selected_strategy": selected_strategy,
                "copy": {
                    "text": content.copy_text,
                    "tone": content.copy_tone
                },
                "image": {
                    "url": content.image_url,
                    "prompt": content.image_prompt
                },
                "target_ages": final_target_ages,
                "target_genders": [target_gender_str],
                "target_interests": final_target_interests,
                "created_at": content.created_at.isoformat() if content.created_at else None
            }
            
            if performance:
                response_data["performance_prediction"] = {
                    "impressions": performance.impressions,
                    "clicks": performance.clicks,
                    "ctr": performance.ctr,
                    "engagement_rate": performance.engagement_rate,
                    "conversion_rate": performance.conversion_rate,
                    "brand_recall_score": performance.brand_recall_score,
                    "confidence_score": performance.confidence_score
                }
            
            complete_data = {
                "type": "complete",
                "data": response_data,
                "generation_time": generation_time
            }
            yield f"data: {json.dumps(complete_data, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            logger.error(f"스트리밍 생성 실패: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            error_data = {
                "type": "error",
                "message": str(e)
            }
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate_with_progress(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
