"""
챗봇 API
사용자 대화를 분석하여 폼 데이터를 추출하고 대화 응답 생성
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import logging

from app.services.gemini_service import gemini_service
from app.models.user import User
from app.utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chatbot"])


class ChatMessage(BaseModel):
    """챗봇 메시지"""
    role: str = Field(..., description="user | assistant")
    content: str = Field(..., description="메시지 내용")


class ChatRequest(BaseModel):
    """챗봇 요청"""
    message: str = Field(..., description="사용자 메시지")
    conversation_history: List[ChatMessage] = Field(default=[], description="대화 히스토리 (최근 5개)")


class ChatResponse(BaseModel):
    """챗봇 응답"""
    response: str = Field(..., description="어시스턴트 응답")
    form_updates: Dict = Field(default={}, description="폼 업데이트 데이터")
    confidence: float = Field(default=0.0, description="추출 신뢰도 (0-1)")
    next_question: Optional[str] = Field(None, description="다음 질문 (필요한 정보가 있을 때)")


@router.post("/analyze", response_model=ChatResponse)
async def analyze_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    사용자 메시지 분석 및 폼 데이터 추출

    **동작:**
    1. 사용자 메시지에서 제품 정보, 타겟 정보 추출
    2. 추출된 정보를 폼 데이터 형식으로 변환
    3. 부족한 정보가 있으면 추가 질문 생성
    4. 자연스러운 대화 응답 생성
    """
    try:
        logger.info(f"챗봇 분석 시작: {request.message[:100]}...")

        # Gemini로 메시지 분석 및 데이터 추출
        result = await gemini_service.analyze_chat_message(
            message=request.message,
            conversation_history=[msg.dict() for msg in request.conversation_history]
        )

        logger.info(f"추출된 폼 데이터: {result.get('form_updates', {})}")
        logger.info(f"신뢰도: {result.get('confidence', 0)}")

        return ChatResponse(
            response=result.get('response', '정보 감사합니다!'),
            form_updates=result.get('form_updates', {}),
            confidence=result.get('confidence', 0.0),
            next_question=result.get('next_question')
        )

    except Exception as e:
        logger.error(f"챗봇 분석 실패: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"챗봇 처리 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/suggestions")
async def get_suggestions(
    request: Dict,
    current_user: User = Depends(get_current_user)
):
    """
    스마트 제안 생성

    - 트렌드 키워드
    - 인기 타겟층
    - 추천 전략
    """
    suggestion_type = request.get("type", "trends")

    try:
        if suggestion_type == "trends":
            # 트렌드 키워드 생성
            result = await gemini_service.generate_trend_keywords()
            return {"suggestions": result}

        elif suggestion_type == "targets":
            # 인기 타겟층 추천
            category = request.get("category")
            result = await gemini_service.suggest_target_audiences(category)
            return {"suggestions": result}

        elif suggestion_type == "strategies":
            # 추천 전략
            product_info = request.get("product_info", {})
            result = await gemini_service.suggest_strategies(product_info)
            return {"suggestions": result}

        else:
            raise HTTPException(status_code=400, detail="Invalid suggestion type")

    except Exception as e:
        logger.error(f"제안 생성 실패: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"제안 생성 중 오류가 발생했습니다: {str(e)}"
        )
