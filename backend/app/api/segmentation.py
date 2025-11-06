"""
타겟 세분화 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel, Field
import logging

from app.services.segmentation_service import get_segmentation_service

router = APIRouter(prefix="/api/segmentation", tags=["segmentation"])
logger = logging.getLogger(__name__)


class SegmentFilterRequest(BaseModel):
    """세그먼트 필터링 요청"""
    age_groups: Optional[List[str]] = Field(None, description="나이대 리스트 (10대, 20대, 30대, 40대, 50대, 60대 이상)")
    genders: Optional[List[str]] = Field(None, description="성별 리스트 (남성, 여성)")
    income_levels: Optional[List[str]] = Field(None, description="소득 수준 리스트 (저소득, 중소득, 중상소득, 고소득)")
    interests: Optional[List[str]] = Field(None, description="관심사 리스트")
    category: Optional[str] = Field(None, description="제품 카테고리 (화장품, 식품, 패션, 전자제품, 서비스)")
    limit: Optional[int] = Field(50, description="최대 반환 개수")


class SegmentFilterResponse(BaseModel):
    """세그먼트 필터링 응답"""
    success: bool
    message: str
    data: dict


class KeywordSearchRequest(BaseModel):
    """키워드 검색 요청"""
    keywords: List[str] = Field(..., description="검색 키워드 리스트")
    limit: int = Field(50, description="최대 반환 개수")


@router.post("/filter", response_model=SegmentFilterResponse)
async def filter_segments(request: SegmentFilterRequest):
    """
    조건에 맞는 타겟 프로필 필터링

    Example request:
    ```json
    {
        "age_groups": ["10대", "20대"],
        "genders": ["여성"],
        "income_levels": ["저소득", "중소득"],
        "interests": ["패션"],
        "category": "화장품",
        "limit": 10
    }
    ```
    """
    try:
        service = get_segmentation_service()

        # 필터링 실행
        profiles = service.filter_profiles(
            age_groups=request.age_groups,
            genders=request.genders,
            income_levels=request.income_levels,
            interests=request.interests,
            category=request.category,
            limit=request.limit
        )

        # 인사이트 추출
        raw_insights = service.extract_insights(profiles)

        # 프론트엔드 형식으로 변환
        frontend_insights = {
            "pain_points": [item['pain_point'] for item in raw_insights.get('psychographics', {}).get('top_pain_points', [])[:5]],
            "preferred_channels": [item['channel'] for item in raw_insights.get('channels', {}).get('top_channels', [])[:5]],
            "tone_preferences": [raw_insights.get('marketing_recommendations', {}).get('content_strategy', {}).get('tone_and_manner', '친근하고 트렌디한 톤')],
            "message_strategies": raw_insights.get('marketing_recommendations', {}).get('content_strategy', {}).get('message_strategy', [])
        }

        return SegmentFilterResponse(
            success=True,
            message=f"{len(profiles)}개의 타겟 프로필을 찾았습니다.",
            data={
                "profiles": profiles,
                "insights": frontend_insights
            }
        )

    except Exception as e:
        logger.error(f"세그먼트 필터링 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=SegmentFilterResponse)
async def search_by_keywords(request: KeywordSearchRequest):
    """
    키워드로 타겟 프로필 검색

    Example request:
    ```json
    {
        "keywords": ["시간 부족", "육아"],
        "limit": 20
    }
    ```
    """
    try:
        service = get_segmentation_service()

        # 키워드 검색 실행
        profiles = service.search_by_keywords(
            keywords=request.keywords,
            limit=request.limit
        )

        # 인사이트 추출
        insights = service.extract_insights(profiles)

        return SegmentFilterResponse(
            success=True,
            message=f"{len(profiles)}개의 타겟 프로필을 찾았습니다.",
            data={
                "profiles": profiles,
                "insights": insights
            }
        )

    except Exception as e:
        logger.error(f"키워드 검색 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_all_segments_summary():
    """
    전체 세그먼트 요약 정보 조회

    Returns:
        전체 프로필 수, 나이대/성별/소득/카테고리 분포, 고유 관심사 목록
    """
    try:
        service = get_segmentation_service()
        summary = service.get_all_segments()

        return {
            "success": True,
            "message": "전체 세그먼트 요약 정보를 조회했습니다.",
            "data": summary
        }

    except Exception as e:
        logger.error(f"세그먼트 요약 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights")
async def get_segment_insights(
    age_group: Optional[str] = Query(None, description="나이대"),
    gender: Optional[str] = Query(None, description="성별"),
    income_level: Optional[str] = Query(None, description="소득 수준"),
    category: Optional[str] = Query(None, description="제품 카테고리")
):
    """
    특정 세그먼트의 인사이트만 조회 (프로필 데이터 제외)

    프로필 데이터 없이 인사이트만 빠르게 확인하고 싶을 때 사용
    """
    try:
        service = get_segmentation_service()

        # 필터링 실행
        profiles = service.filter_profiles(
            age_group=age_group,
            gender=gender,
            income_level=income_level,
            category=category
        )

        # 인사이트만 추출
        insights = service.extract_insights(profiles)

        return {
            "success": True,
            "message": f"{len(profiles)}개 프로필 기반 인사이트입니다.",
            "data": insights
        }

    except Exception as e:
        logger.error(f"인사이트 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))
