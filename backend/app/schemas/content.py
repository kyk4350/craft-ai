"""
콘텐츠 생성 관련 스키마
"""

from pydantic import BaseModel, Field
from typing import List, Optional


# === 전략 생성 ===

class StrategyRequest(BaseModel):
    """전략 생성 요청"""
    product_name: str = Field(..., description="제품명")
    product_description: str = Field(..., description="제품 설명")
    category: str = Field(..., description="제품 카테고리")
    target_age: str = Field(..., description="타겟 연령대 (예: 20대)")
    target_gender: str = Field(..., description="타겟 성별 (남성/여성/무관)")
    target_interests: List[str] = Field(..., description="타겟 관심사 리스트")


class Strategy(BaseModel):
    """마케팅 전략"""
    id: int = Field(..., description="전략 ID")
    name: str = Field(..., description="전략명")
    core_message: str = Field(..., description="핵심 메시지")
    emotion: str = Field(..., description="감성 유형 (감성적/이성적/사회적)")
    expected_effect: str = Field(..., description="예상 효과")


class StrategyResponse(BaseModel):
    """전략 생성 응답"""
    success: bool = Field(True, description="성공 여부")
    data: List[Strategy] = Field(..., description="생성된 전략 리스트")
    message: str = Field("전략 생성 완료", description="응답 메시지")


# === 카피 생성 ===

class CopyRequest(BaseModel):
    """카피 생성 요청"""
    product_name: str = Field(..., description="제품명")
    product_description: str = Field(..., description="제품 설명")
    strategy: Strategy = Field(..., description="선택한 마케팅 전략")
    target_age: str = Field(..., description="타겟 연령대")
    target_gender: str = Field(..., description="타겟 성별")
    target_interests: List[str] = Field(..., description="타겟 관심사 리스트")


class Copy(BaseModel):
    """광고 카피"""
    id: int = Field(..., description="카피 ID")
    tone: str = Field(..., description="톤 (professional/casual/impact)")
    text: str = Field(..., description="카피 텍스트")
    hashtags: List[str] = Field(..., description="해시태그 리스트")
    length: int = Field(..., description="글자 수")


class CopyResponse(BaseModel):
    """카피 생성 응답"""
    success: bool = Field(True, description="성공 여부")
    data: List[Copy] = Field(..., description="생성된 카피 리스트")
    message: str = Field("카피 생성 완료", description="응답 메시지")


# === 이미지 프롬프트 변환 ===

class ImagePromptRequest(BaseModel):
    """이미지 프롬프트 변환 요청"""
    copy_text: str = Field(..., description="광고 카피")
    product_name: str = Field(..., description="제품명")
    target_age: str = Field(..., description="타겟 연령대")
    target_gender: str = Field(..., description="타겟 성별")
    strategy: Strategy = Field(..., description="마케팅 전략")


class ImagePromptResponse(BaseModel):
    """이미지 프롬프트 변환 응답"""
    success: bool = Field(True, description="성공 여부")
    data: str = Field(..., description="생성된 이미지 프롬프트 (영어)")
    message: str = Field("이미지 프롬프트 생성 완료", description="응답 메시지")


# === 이미지 생성 ===

class ImageGenerationRequest(BaseModel):
    """이미지 생성 요청"""
    image_prompt: str = Field(..., description="이미지 프롬프트 (영어)")
    width: int = Field(1024, description="이미지 너비")
    height: int = Field(1024, description="이미지 높이")


class ImageGenerationResponse(BaseModel):
    """이미지 생성 응답"""
    success: bool = Field(True, description="성공 여부")
    data: str = Field(..., description="생성된 이미지 URL")
    message: str = Field("이미지 생성 완료", description="응답 메시지")


# === 에러 응답 ===

class ErrorResponse(BaseModel):
    """에러 응답"""
    success: bool = Field(False, description="성공 여부")
    data: Optional[dict] = Field(None, description="데이터")
    message: str = Field(..., description="에러 메시지")
    error: str = Field(..., description="에러 상세")


# ============================================
# 통합 콘텐츠 생성 API
# ============================================

class FullContentGenerationRequest(BaseModel):
    """전체 콘텐츠 생성 요청"""
    # 제품 정보
    product_name: str = Field(..., description="제품명")
    product_description: str = Field(..., description="제품 설명")
    category: str = Field(..., description="카테고리 (화장품/식품/패션/전자제품/서비스)")

    # 타겟 정보
    target_age: str = Field(..., description="타겟 나이대 (10대/20대/30대/40대/50대/60대 이상)")
    target_gender: str = Field(..., description="타겟 성별 (남성/여성/무관)")
    target_interests: List[str] = Field(..., description="타겟 관심사")
    target_income_level: Optional[str] = Field(None, description="소득 수준 (저소득/중소득/중상소득/고소득)")

    # 생성 옵션
    strategy_id: Optional[int] = Field(None, description="선택한 전략 ID (1-3). None이면 자동 선택")
    copy_tone: Optional[str] = Field("professional", description="카피 톤 (professional/casual/impact)")

    # 프로젝트 정보 (옵션)
    project_id: Optional[int] = Field(None, description="프로젝트 ID (저장 시 필요)")
    save_to_db: bool = Field(True, description="데이터베이스에 저장 여부")


class FullContentGenerationResponse(BaseModel):
    """전체 콘텐츠 생성 응답"""
    success: bool = Field(True, description="성공 여부")
    data: dict = Field(..., description="생성된 콘텐츠")
    message: str = Field("콘텐츠 생성 완료", description="응답 메시지")
    generation_time: int = Field(..., description="총 생성 시간 (초)")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "content_id": 123,
                    "strategies": [
                        {"id": 1, "name": "감성적 접근", "core_message": "..."}
                    ],
                    "selected_strategy_id": 1,
                    "copy": {
                        "text": "피부가 달라지는 비타민C 세럼",
                        "tone": "professional",
                        "hashtags": ["#비타민C", "#세럼"]
                    },
                    "image": {
                        "prompt": "Vitamin C serum bottle...",
                        "url": "https://replicate.delivery/...",
                        "local_url": "/static/images/..."
                    }
                },
                "message": "콘텐츠 생성 완료",
                "generation_time": 35
            }
        }
