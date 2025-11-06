"""
Contents CRUD API endpoints
콘텐츠 목록 조회, 상세 조회, 삭제
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import logging

from app.models.base import get_db
from app.models.content import Content
from app.models.user import User
from app.models.performance import Performance
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/contents", tags=["Contents"])
logger = logging.getLogger(__name__)


@router.get("")
def get_contents(
    project_id: Optional[int] = Query(None, description="프로젝트 ID로 필터링"),
    limit: int = Query(20, ge=1, le=100, description="조회할 콘텐츠 수"),
    offset: int = Query(0, ge=0, description="건너뛸 콘텐츠 수"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    콘텐츠 목록 조회 (로그인 필요)

    - 본인이 생성한 콘텐츠만 조회 가능

    Args:
        project_id: 특정 프로젝트의 콘텐츠만 조회 (선택)
        limit: 한 번에 조회할 콘텐츠 수 (기본 20, 최대 100)
        offset: 페이지네이션을 위한 offset (기본 0)

    Returns:
        콘텐츠 목록 및 총 개수
    """
    try:
        # 기본 쿼리 (본인의 콘텐츠만 조회)
        query = db.query(Content).filter(Content.user_id == current_user.id)

        # 프로젝트 필터링
        if project_id is not None:
            query = query.filter(Content.project_id == project_id)

        # 전체 개수 (필터 적용 후)
        total = query.count()

        # 콘텐츠 조회 (최신순)
        contents = query.order_by(Content.created_at.desc()).offset(offset).limit(limit).all()

        # 응답 데이터 구성
        content_list = []
        for content in contents:
            # 성과 데이터 조회
            performance = db.query(Performance).filter(
                Performance.content_id == content.id
            ).first()

            # product_name 우선순위: Content 테이블 -> Project -> None
            product_name = content.product_name
            if not product_name and content.project:
                product_name = content.project.product_name

            content_data = {
                "id": content.id,
                "project_id": content.project_id,
                "product_name": product_name,
                "category": content.category,
                "target_age_group": content.target_age_group,
                "target_gender": content.target_gender,
                "target_interests": content.target_interests,
                "strategy": content.strategy,
                "copy_text": content.copy_text,
                "copy_tone": content.copy_tone,
                "hashtags": content.hashtags,
                "image_url": content.image_url,
                "image_provider": content.image_provider,
                "status": content.status.value,
                "created_at": content.created_at.isoformat() if content.created_at else None,
                "generation_time": content.generation_time,
            }

            # 성과 데이터가 있으면 포함
            if performance:
                content_data["performance"] = {
                    "ctr": performance.ctr,
                    "engagement_rate": performance.engagement_rate,
                    "conversion_rate": performance.conversion_rate,
                    "brand_recall_score": performance.brand_recall_score,
                    "is_prediction": performance.data_source.value == "ai_simulation"
                }
            else:
                content_data["performance"] = None

            content_list.append(content_data)

        return {
            "success": True,
            "data": {
                "contents": content_list,
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total
            }
        }

    except Exception as e:
        logger.error(f"콘텐츠 목록 조회 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"콘텐츠 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/{content_id}")
def get_content(
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    콘텐츠 상세 조회 (로그인 필요)

    - 본인이 생성한 콘텐츠만 조회 가능

    Args:
        content_id: 콘텐츠 ID

    Returns:
        콘텐츠 상세 정보 (성과 데이터 포함)
    """
    try:
        # 콘텐츠 조회 (본인 콘텐츠만)
        content = db.query(Content).filter(
            Content.id == content_id,
            Content.user_id == current_user.id
        ).first()

        if not content:
            raise HTTPException(
                status_code=404,
                detail=f"콘텐츠 ID {content_id}를 찾을 수 없습니다."
            )

        # 성과 데이터 조회
        performance = db.query(Performance).filter(
            Performance.content_id == content.id
        ).first()

        # product_name 우선순위: Content 테이블 -> Project -> None
        product_name = content.product_name
        product_description = content.product_description
        if not product_name and content.project:
            product_name = content.project.product_name
            product_description = content.project.product_description

        content_data = {
            "id": content.id,
            "project_id": content.project_id,
            "product_name": product_name,
            "product_description": product_description,
            "category": content.category,
            "target_age_group": content.target_age_group,
            "target_gender": content.target_gender,
            "target_income_level": content.target_income_level,
            "target_interests": content.target_interests,
            "strategy": content.strategy,
            "copy_text": content.copy_text,
            "copy_tone": content.copy_tone,
            "hashtags": content.hashtags,
            "image_prompt": content.image_prompt,
            "image_url": content.image_url,
            "image_provider": content.image_provider,
            "status": content.status.value,
            "generation_time": content.generation_time,
            "created_at": content.created_at.isoformat() if content.created_at else None,
            "updated_at": content.updated_at.isoformat() if content.updated_at else None,
        }

        # 성과 데이터가 있으면 포함
        if performance:
            content_data["performance"] = {
                "id": performance.id,
                "ctr": performance.ctr,
                "engagement_rate": performance.engagement_rate,
                "conversion_rate": performance.conversion_rate,
                "brand_recall_score": performance.brand_recall_score,
                "impressions": performance.impressions,
                "clicks": performance.clicks,
                "data_source": performance.data_source.value,
                "confidence_score": performance.confidence_score,
                "created_at": performance.created_at.isoformat() if performance.created_at else None
            }
        else:
            content_data["performance"] = None

        return {
            "success": True,
            "data": content_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"콘텐츠 상세 조회 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"콘텐츠 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.delete("/{content_id}")
def delete_content(
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    콘텐츠 삭제 (로그인 필요)

    - 본인이 생성한 콘텐츠만 삭제 가능

    Args:
        content_id: 삭제할 콘텐츠 ID

    Returns:
        삭제 성공 메시지
    """
    try:
        # 콘텐츠 조회 (본인 콘텐츠만)
        content = db.query(Content).filter(
            Content.id == content_id,
            Content.user_id == current_user.id
        ).first()

        if not content:
            raise HTTPException(
                status_code=404,
                detail=f"콘텐츠 ID {content_id}를 찾을 수 없습니다."
            )

        # 콘텐츠 삭제 (CASCADE로 Performance도 함께 삭제됨)
        db.delete(content)
        db.commit()

        logger.info(f"콘텐츠 삭제 완료: ID {content_id}")

        return {
            "success": True,
            "message": f"콘텐츠 ID {content_id}가 삭제되었습니다."
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"콘텐츠 삭제 오류: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"콘텐츠 삭제 중 오류가 발생했습니다: {str(e)}"
        )
