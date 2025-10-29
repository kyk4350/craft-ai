"""
Performance analysis API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from app.models.base import get_db
from app.services.performance_service import PerformanceService

router = APIRouter(prefix="/api/performance", tags=["Performance"])
logger = logging.getLogger(__name__)


@router.post("/predict/{content_id}")
async def predict_performance(
    content_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    콘텐츠 성과 예측 (AI 시뮬레이션)

    Args:
        content_id: 콘텐츠 ID

    Returns:
        예측된 성과 데이터
    """
    try:
        service = PerformanceService(db)

        # 기존 예측 데이터가 있는지 확인
        existing = service.get_performance(content_id)
        if existing:
            logger.info(f"기존 성과 데이터 반환 - Content ID: {content_id}")
            return {
                "success": True,
                "message": "기존 성과 데이터를 반환합니다.",
                "data": service.get_performance_summary(content_id),
                "is_new_prediction": False
            }

        # 새로운 예측 실행
        logger.info(f"새로운 성과 예측 시작 - Content ID: {content_id}")
        performance = await service.predict_performance(content_id)

        if not performance:
            raise HTTPException(
                status_code=500,
                detail="성과 예측에 실패했습니다."
            )

        return {
            "success": True,
            "message": "성과 예측이 완료되었습니다.",
            "data": service.get_performance_summary(content_id),
            "is_new_prediction": True
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"성과 예측 API 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"성과 예측 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/{content_id}")
def get_performance(
    content_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    콘텐츠의 성과 데이터 조회

    Args:
        content_id: 콘텐츠 ID

    Returns:
        성과 데이터
    """
    try:
        service = PerformanceService(db)
        summary = service.get_performance_summary(content_id)

        if not summary["exists"]:
            raise HTTPException(
                status_code=404,
                detail="성과 데이터가 없습니다. /predict/{content_id}로 예측을 먼저 실행하세요."
            )

        return {
            "success": True,
            "data": summary
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"성과 조회 API 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"성과 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/{content_id}/detailed")
def get_detailed_performance(
    content_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    콘텐츠의 상세 성과 데이터 조회 (페르소나 반응 포함)

    Args:
        content_id: 콘텐츠 ID

    Returns:
        상세 성과 데이터
    """
    try:
        service = PerformanceService(db)
        performance = service.get_performance(content_id)

        if not performance:
            raise HTTPException(
                status_code=404,
                detail="성과 데이터가 없습니다."
            )

        return {
            "success": True,
            "data": {
                "id": performance.id,
                "content_id": performance.content_id,
                "data_source": performance.data_source.value,
                "metrics": {
                    "impressions": performance.impressions,
                    "clicks": performance.clicks,
                    "ctr": performance.ctr,
                    "engagement_rate": performance.engagement_rate,
                    "conversion_rate": performance.conversion_rate,
                    "brand_recall_score": performance.brand_recall_score
                },
                "personas_data": performance.personas_data,
                "confidence_score": performance.confidence_score,
                "created_at": performance.created_at.isoformat() if performance.created_at else None
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"상세 성과 조회 API 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"상세 성과 조회 중 오류가 발생했습니다: {str(e)}"
        )
