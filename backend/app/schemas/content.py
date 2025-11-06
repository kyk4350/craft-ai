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
    category: str = Field(..., description="카테고리 (beauty/food/fashion/electronics/service)")
    product_image_path: Optional[str] = Field(None, description="업로드된 제품 이미지 파일 경로 (제품 기반 마케팅 이미지 생성 시 사용)")

    # 타겟 정보 (다중 선택 가능)
    target_ages: List[str] = Field(..., description="타겟 나이대 리스트 (10대/20대/30대/40대/50대/60대 이상)")
    target_genders: List[str] = Field(..., description="타겟 성별 리스트 (남성/여성/무관)")
    target_interests: List[str] = Field(..., description="타겟 관심사")
    target_income_level: Optional[str] = Field(None, description="소득 수준 (저소득/중소득/중상소득/고소득)")

    # 생성 옵션
    strategy_id: Optional[int] = Field(None, description="선택한 전략 ID (1-3). None이면 자동 선택")
    copy_tone: Optional[str] = Field("professional", description="카피 톤 (professional/casual/impact)")

    # 재생성 옵션 (수정 요청)
    regenerate_type: Optional[str] = Field(None, description="재생성 타입 (all/image/copy/auto). None이면 신규 생성")
    custom_request: Optional[str] = Field(None, description="사용자 자유 입력 수정 요청 (regenerate_type=auto일 때 사용)")

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


# === 부분 재생성 API ===

class RegenerateImageRequest(BaseModel):
    """이미지만 재생성 요청"""
    content_id: str = Field(..., description="기존 콘텐츠 ID")
    product_name: str = Field(..., description="제품명")
    product_description: str = Field(..., description="제품 설명")
    category: str = Field(..., description="카테고리")
    # 타겟 정보는 기존 콘텐츠에서 재사용하므로 필수 아님
    image_prompt: Optional[str] = Field(None, description="커스텀 이미지 프롬프트 (선택)")


class RegenerateCopyRequest(BaseModel):
    """카피만 재생성 요청"""
    content_id: str = Field(..., description="기존 콘텐츠 ID")
    product_name: str = Field(..., description="제품명")
    product_description: str = Field(..., description="제품 설명")
    category: str = Field(..., description="카테고리")
    target_ages: List[str] = Field(..., description="타겟 연령대")
    target_genders: List[str] = Field(..., description="타겟 성별")
    target_interests: List[str] = Field(..., description="타겟 관심사")
    copy_tone: str = Field(..., description="새로운 카피 톤")
    strategy_name: Optional[str] = Field(None, description="전략명 (기존 전략 재사용)")
    core_message: Optional[str] = Field(None, description="핵심 메시지 (기존 전략 재사용)")
