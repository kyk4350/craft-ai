"""
Analytics API endpoints for dashboard
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import logging

from app.models.base import get_db
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])
logger = logging.getLogger(__name__)


@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    대시보드 핵심 지표 요약

    Returns:
        총 콘텐츠 수, 평균 CTR, 최고 성과 등
    """
    try:
        service = AnalyticsService(db)
        summary = service.get_summary()

        return {
            "success": True,
            "data": summary
        }

    except Exception as e:
        logger.error(f"요약 통계 조회 API 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"요약 통계 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/by-strategy")
def get_performance_by_strategy(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    전략별 평균 성과 비교

    Returns:
        전략별 평균 CTR, 참여율, 전환율, 브랜드 기억도
    """
    try:
        service = AnalyticsService(db)
        strategy_stats = service.get_performance_by_strategy()

        return {
            "success": True,
            "data": strategy_stats
        }

    except Exception as e:
        logger.error(f"전략별 성과 조회 API 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"전략별 성과 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/by-target")
def get_performance_by_target(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    타겟별 평균 성과 비교

    Returns:
        타겟(나이대×성별)별 평균 성과
    """
    try:
        service = AnalyticsService(db)
        target_stats = service.get_performance_by_target()

        return {
            "success": True,
            "data": target_stats
        }

    except Exception as e:
        logger.error(f"타겟별 성과 조회 API 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"타겟별 성과 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/top-contents")
def get_top_contents(
    limit: int = 5,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    최고 성과 콘텐츠 목록

    Args:
        limit: 조회할 콘텐츠 수 (기본 5개)

    Returns:
        CTR 높은 순으로 콘텐츠 목록
    """
    try:
        service = AnalyticsService(db)
        top_contents = service.get_top_contents(limit=limit)

        return {
            "success": True,
            "data": top_contents
        }

    except Exception as e:
        logger.error(f"최고 성과 콘텐츠 조회 API 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"최고 성과 콘텐츠 조회 중 오류가 발생했습니다: {str(e)}"
        )
