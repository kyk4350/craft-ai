"""
Gemini API 서비스 모듈
텍스트 생성 (전략, 카피, 프롬프트 변환, 분석)
"""

import google.generativeai as genai
from typing import Dict, List, Optional
import logging
import json
import time
from app.config import settings

logger = logging.getLogger(__name__)

# Gemini API 설정
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)


class GeminiService:
    """Gemini API 텍스트 생성 서비스"""

    def __init__(self):
        self.model_name = settings.GEMINI_MODEL
        self.model = genai.GenerativeModel(self.model_name)

    async def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        max_retries: int = 3
    ) -> str:
        """
        텍스트 생성 (재시도 로직 포함)

        Args:
            prompt: 입력 프롬프트
            temperature: 창의성 조절 (0.0-1.0)
            max_tokens: 최대 토큰 수
            max_retries: 최대 재시도 횟수

        Returns:
            생성된 텍스트
        """
        last_error = None

        for attempt in range(max_retries):
            try:
                generation_config = {
                    "temperature": temperature,
                }
                if max_tokens:
                    generation_config["max_output_tokens"] = max_tokens

                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config
                )

                # finish_reason 확인
                if not response.parts:
                    logger.error(f"응답 없음. finish_reason: {response.candidates[0].finish_reason}")
                    raise Exception(f"텍스트 생성 실패: finish_reason={response.candidates[0].finish_reason}")

                return response.text

            except Exception as e:
                last_error = e
                logger.warning(f"Gemini 텍스트 생성 시도 {attempt + 1}/{max_retries} 실패: {str(e)}")

                if attempt < max_retries - 1:
                    # 지수 백오프: 2초, 4초, 8초
                    wait_time = 2 ** (attempt + 1)
                    logger.info(f"{wait_time}초 후 재시도...")
                    time.sleep(wait_time)

        logger.error(f"Gemini 텍스트 생성 최종 실패 (재시도 {max_retries}회): {str(last_error)}")
        raise last_error

    async def generate_marketing_strategies(
        self,
        product_name: str,
        product_description: str,
        category: str,
        target_age: str,
        target_gender: str,
        target_interests: List[str],
        past_performance: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """
        마케팅 전략 3가지 제안 (RAG 활용)

        Args:
            past_performance: 과거 유사 콘텐츠 성과 데이터 (RAG)

        Returns:
            [
                {
                    "id": 1,
                    "name": "전략명",
                    "core_message": "핵심 메시지",
                    "emotion": "감성적|이성적|사회적",
                    "expected_effect": "예상 효과"
                }
            ]
        """
        interests_str = ", ".join(target_interests)

        # RAG 데이터 포함 여부에 따라 프롬프트 구성
        rag_section = ""
        if past_performance and len(past_performance) > 0:
            rag_section = "\n\n**과거 유사 콘텐츠 성과 데이터 (참고용):**\n"
            for i, perf in enumerate(past_performance, 1):
                rag_section += f"""
{i}. 유사도: {perf['similarity_score']:.2f}
   - 카피: "{perf['copy_text'][:100]}..."
   - 성과: 도달 {perf['performance']['impressions']:,}명, 참여율 {perf['performance']['engagement_rate']:.1f}%, CTR {perf['performance']['ctr']:.2f}%, 전환율 {perf['performance']['conversion_rate']:.2f}%
"""
            rag_section += "\n위 데이터를 참고하여 더 현실적이고 효과적인 전략을 수립해주세요.\n"

        prompt = f"""
당신은 전문 마케팅 전략가입니다.

제품 정보:
- 제품명: {product_name}
- 설명: {product_description}
- 카테고리: {category}

타겟 고객:
- 나이: {target_age}
- 성별: {target_gender}
- 관심사: {interests_str}
{rag_section}
위 제품을 타겟 고객에게 판매하기 위한 3가지 서로 다른 마케팅 전략을 제안해주세요.

각 전략은 다음 JSON 형식으로 작성하고, 각 전략의 예상 성과도 함께 제공해주세요:
{{
  "strategies": [
    {{
      "id": 1,
      "name": "전략명 (예: 감성적 스토리텔링)",
      "core_message": "핵심 메시지 (한 문장)",
      "emotion": "감성적|이성적|사회적",
      "expected_effect": "예상 효과 설명",
      "performance_prediction": {{
        "estimated_reach": 10000,
        "estimated_engagement_rate": 3.5,
        "estimated_conversions": 150,
        "confidence_score": 0.75
      }}
    }}
  ]
}}

성과 예측 설명:
- estimated_reach: 예상 도달 수 (명)
- estimated_engagement_rate: 예상 참여율 (%)
- estimated_conversions: 예상 전환 수 (명)
- confidence_score: 예측 신뢰도 (0-1)

타겟 고객 특성과 제품 특성을 고려하여 현실적인 수치를 제공해주세요.

JSON만 출력해주세요.
"""

        try:
            response_text = await self.generate_text(prompt, temperature=0.8)

            # JSON 파싱
            parsed_data = self._parse_json_response(response_text)

            if "strategies" not in parsed_data:
                raise ValueError("응답에 'strategies' 키가 없습니다.")

            strategies = parsed_data["strategies"]

            # 검증: 3개의 전략이 있는지 확인
            if len(strategies) != 3:
                logger.warning(f"전략 개수가 3개가 아닙니다: {len(strategies)}개")

            return strategies

        except Exception as e:
            logger.error(f"전략 생성 실패: {str(e)}")
            raise

    async def generate_copies(
        self,
        product_name: str,
        product_description: str,
        strategy: Dict,
        target_age: str,
        target_gender: str,
        target_interests: List[str],
        copy_tone: str = "professional"  # 요청된 톤
    ) -> List[Dict]:
        """
        요청된 톤의 광고 카피 생성

        Args:
            copy_tone: "professional", "casual", "impact" 중 하나

        Returns:
            [
                {
                    "id": 1,
                    "tone": "professional|casual|impact",
                    "text": "카피 텍스트",
                    "hashtags": ["#태그1", "#태그2", "#태그3"],
                    "length": 45
                }
            ]
        """
        interests_str = ", ".join(target_interests)

        # 톤별 설명
        tone_descriptions = {
            "professional": "격식 있고 전문적인 톤, 40-50자",
            "casual": "친근하고 편안한 톤, 30-40자",
            "impact": "짧고 강렬한 톤, 15-25자"
        }

        tone_desc = tone_descriptions.get(copy_tone, tone_descriptions["professional"])

        prompt = f"""
당신은 전문 카피라이터이자 SNS 마케팅 전문가입니다.

제품: {product_name}
설명: {product_description}
전략: {strategy.get('name')} - {strategy.get('core_message')}
타겟: {target_age} {target_gender}, 관심사: {interests_str}
요청된 톤: {copy_tone} ({tone_desc})

**카피 작성 원칙:**
1. **강력한 후크**: 첫 3초 안에 타겟의 관심을 사로잡아야 합니다
2. **감정 유발**: 공감, 설렘, 궁금증, 욕구 중 하나를 강하게 자극하세요
3. **차별화된 가치**: 경쟁사와 구별되는 핵심 베네핏을 명확하게 전달하세요
4. **행동 유도**: 클릭, 구매, 저장 등 구체적인 행동을 유도하세요
5. **타겟 언어 사용**: 타겟이 일상에서 쓰는 표현과 말투를 사용하세요

**성과 높은 카피의 특징:**
- 타겟의 pain point를 정확히 짚어냅니다
- 구체적인 숫자나 사실을 포함합니다
- 호기심을 자극하는 질문이나 문장을 사용합니다
- 타겟이 원하는 결과를 명확히 제시합니다
- 긴급성이나 희소성을 암시합니다

위 전략을 기반으로 **{copy_tone}** 톤의 광고 카피를 작성해주세요.

**해시태그 생성 가이드 (15-20개):**
1. **제품 관련** (5-7개): 제품명, 카테고리, 주요 특징
2. **타겟 관련** (3-5개): 연령대, 라이프스타일, 관심사
3. **트렌드 키워드** (3-5개): 인기 검색어, 시즌, 트렌드
4. **감성 키워드** (2-3개): 감정, 분위기, 느낌
5. **실용 키워드** (2-3개): 용도, 장소, 상황

해시태그는 다음 원칙을 따라주세요:
- 실제 SNS에서 검색량이 많은 키워드 우선
- 너무 일반적이거나 너무 구체적이지 않게
- 한글과 영문 적절히 혼합
- # 기호 포함

JSON 형식으로 출력:
{{
  "copies": [
    {{
      "id": 1,
      "tone": "{copy_tone}",
      "text": "카피 내용",
      "hashtags": ["#태그1", "#태그2", ... 15-20개],
      "length": 글자수
    }}
  ]
}}

JSON만 출력해주세요.
"""

        try:
            response_text = await self.generate_text(prompt, temperature=0.9)

            # JSON 파싱
            parsed_data = self._parse_json_response(response_text)

            if "copies" not in parsed_data:
                raise ValueError("응답에 'copies' 키가 없습니다.")

            copies = parsed_data["copies"]

            return copies

        except Exception as e:
            logger.error(f"카피 생성 실패: {str(e)}")
            raise

    async def convert_to_image_prompt(
        self,
        copy_text: str,
        product_name: str,
        target_age: str,
        target_gender: str,
        strategy: Dict
    ) -> str:
        """
        카피를 이미지 생성 프롬프트로 변환

        Returns:
            영어 이미지 프롬프트
        """
        prompt = f"""
You are an expert at creating highly detailed image generation prompts for high-converting marketing and advertising visuals.

Create a professional, detailed image generation prompt that will maximize engagement, clicks, and conversion rates.

Copy: "{copy_text}"
Product: {product_name}
Target Audience: {target_age} {target_gender}
Marketing Strategy: {strategy.get('name')}

**CRITICAL: The image must be eye-catching, scroll-stopping, and highly shareable.**

REQUIREMENTS for a HIGH-PERFORMING visual:

1. COMPOSITION & SUBJECT:
   - Clearly describe the main subject (product, person, or scene)
   - Specify exact positioning, angles, and framing
   - Include product details (packaging, texture, materials)

2. LIGHTING & ATMOSPHERE:
   - Professional studio lighting or natural lighting setup
   - Specific mood (bright, warm, moody, fresh, luxurious, etc.)
   - Time of day if relevant

3. COLOR PALETTE:
   - Specific color schemes that match the brand/product
   - Color harmony and complementary colors
   - Saturation levels (vibrant, muted, pastel, etc.)

4. STYLE & QUALITY:
   - Photography style: commercial product photography, lifestyle photography, flat lay, etc.
   - Camera details: shallow depth of field, bokeh, sharp focus
   - Quality markers: 8K, ultra detailed, professional, award-winning

5. BACKGROUND & CONTEXT:
   - Specific background elements
   - Props or supporting elements
   - Environmental context

6. BRAND ALIGNMENT:
   - Match the visual style to target demographic
   - Align with the marketing strategy emotion

OUTPUT FORMAT:
Write a single, detailed English prompt (100-200 words) that combines all these elements.
Use professional photography and advertising terminology.
Focus on visual impact and commercial appeal.
DO NOT include any explanations - output ONLY the prompt.

Example structure:
"Professional commercial photography of [product], [key features], [composition], [lighting setup], [color palette], [background], [mood], [camera settings], [quality markers], [style references]"
"""

        try:
            image_prompt = await self.generate_text(prompt, temperature=0.8)

            # 후처리: 따옴표나 설명 제거
            image_prompt = image_prompt.strip()
            image_prompt = image_prompt.replace('"', '').replace("'", "")

            # "professional" 등의 키워드가 없으면 추가
            quality_keywords = ['professional', '8k', 'ultra detailed', 'high quality']
            if not any(keyword in image_prompt.lower() for keyword in quality_keywords):
                image_prompt = f"Professional commercial photography, {image_prompt}, ultra detailed, 8K, award-winning quality"

            logger.info(f"생성된 이미지 프롬프트: {image_prompt[:200]}...")
            return image_prompt

        except Exception as e:
            logger.error(f"이미지 프롬프트 변환 실패: {str(e)}")
            raise

    async def analyze_target_insights(
        self,
        product_name: str,
        product_description: str,
        category: str,
        target_ages: List[str],
        target_genders: List[str],
        target_interests: List[str]
    ) -> Dict:
        """
        타겟 고객 인사이트 AI 실시간 분석

        사용자가 입력한 제품 정보와 타겟 정보를 바탕으로
        AI가 실시간으로 타겟 고객의 페인 포인트, 선호 채널,
        메시지 전략 등을 분석하여 제공합니다.

        Returns:
            {
                "pain_points": ["통증 포인트1", "통증 포인트2", ...],
                "preferred_channels": ["선호 채널1", "선호 채널2", ...],
                "tone_preferences": ["톤 선호도1", "톤 선호도2", ...],
                "message_strategies": ["메시지 전략1", "메시지 전략2", ...],
                "lifestyle_traits": ["라이프스타일 특징1", "라이프스타일 특징2", ...],
                "purchase_motivations": ["구매 동기1", "구매 동기2", ...]
            }
        """
        # 타겟 연령이 비어있으면 자동 분석
        if not target_ages or len(target_ages) == 0:
            ages_note = " (사용자가 연령대를 지정하지 않았으므로, 제품 카테고리와 설명을 기반으로 가장 적합한 타겟 연령대를 2-3개 선정해주세요. 예: ['20-29', '30-39'])"
            ages_str = "자동 분석 필요"
        else:
            ages_note = ""
            ages_str = ", ".join(target_ages)

        genders_str = ", ".join(target_genders)

        # 관심사가 비어있으면 자동 분석 안내 추가
        if not target_interests or len(target_interests) == 0:
            interests_note = " (사용자가 관심사를 지정하지 않았으므로, 제품 카테고리와 타겟 연령/성별을 기반으로 가장 적합한 관심사 키워드를 7-10개 생성해주세요)"
            interests_str = "자동 분석 필요"
        else:
            interests_note = ""
            interests_str = ", ".join(target_interests)

        prompt = f"""
당신은 마케팅 인사이트 전문가입니다.

다음 제품과 타겟 고객 정보를 분석하여 마케팅에 필요한 핵심 인사이트를 제공해주세요.

제품 정보:
- 제품명: {product_name}
- 설명: {product_description}
- 카테고리: {category}

타겟 고객:
- 나이: {ages_str}{ages_note}
- 성별: {genders_str}
- 관심사: {interests_str}{interests_note}

**중요**: 제품 카테고리({category})를 필수적으로 고려하여 분석해주세요.
예를 들어, 패션/의류 제품이라면 패션, 스타일, 트렌드 등 패션 관련 키워드를 중심으로 분석해야 합니다.

위 타겟 고객을 위한 마케팅 인사이트를 JSON 형식으로 제공해주세요:

{{
  "target_ages": ["타겟 연령대 2-3개 (형식: '20-29', '30-39' 등)"],
  "target_interests": ["제품 카테고리와 가장 관련성 높은 관심사 키워드 7-10개 (패션이면 패션 관련, 뷰티면 뷰티 관련)"],
  "pain_points": ["이 타겟 고객이 겪는 주요 고민/문제점 5-7가지"],
  "preferred_channels": ["이 타겟이 자주 사용하는 미디어/SNS 채널 5-7가지"],
  "tone_preferences": ["이 타겟이 선호하는 커뮤니케이션 톤 3가지"],
  "message_strategies": ["효과적인 메시지 전략 5-7가지"],
  "lifestyle_traits": ["이 타겟의 라이프스타일 특징 5-7가지"],
  "purchase_motivations": ["구매를 결정하는 주요 동기 5-7가지"]
}}

**반드시 지켜야 할 원칙**:
1. target_ages는 사용자가 지정하지 않은 경우에만 생성 (지정된 경우 해당 연령대 그대로 사용)
2. target_interests는 제품 카테고리({category})와 직접적으로 연관된 키워드로만 구성
3. 각 배열은 최소 5개, 최대 10개의 항목을 포함
4. 구체적이고 실행 가능한 인사이트로 작성

JSON만 출력하고 다른 설명은 하지 마세요.
"""

        try:
            response_text = await self.generate_text(prompt, temperature=0.7)
            parsed_data = self._parse_json_response(response_text)

            # 필수 키 검증
            required_keys = [
                "pain_points", "preferred_channels", "tone_preferences",
                "message_strategies", "lifestyle_traits", "purchase_motivations"
            ]

            for key in required_keys:
                if key not in parsed_data:
                    logger.warning(f"인사이트 응답에 '{key}' 키가 없습니다")
                    parsed_data[key] = []

            logger.info(f"✓ 타겟 인사이트 분석 완료")
            return parsed_data

        except Exception as e:
            logger.error(f"타겟 인사이트 분석 실패: {str(e)}")
            raise

    async def analyze_chat_message(
        self,
        message: str,
        conversation_history: List[Dict]
    ) -> Dict:
        """
        챗봇 메시지 분석 및 폼 데이터 추출

        사용자 메시지에서 제품 정보, 타겟 정보를 추출하고
        자연스러운 대화 응답을 생성합니다.

        Returns:
            {
                "form_updates": {
                    "product_name": "...",
                    "product_description": "...",
                    "category": "beauty",
                    "target_ages": ["20-29", "30-39"],
                    "target_genders": ["여성"],
                    "target_interests": ["뷰티", "자기관리"],
                    "copy_tone": "casual"
                },
                "response": "어시스턴트 응답 메시지",
                "confidence": 0.85,
                "next_question": "추가 질문 (옵션)"
            }
        """
        # 대화 히스토리를 문자열로 변환
        history_str = ""
        for msg in conversation_history[-5:]:  # 최근 5개만
            role = "사용자" if msg["role"] == "user" else "어시스턴트"
            history_str += f"{role}: {msg['content']}\n"

        prompt = f"""
당신은 마케팅 콘텐츠 생성 어시스턴트입니다.
사용자와 대화하면서 콘텐츠 생성에 필요한 정보를 수집합니다.

이전 대화:
{history_str}

현재 사용자 메시지:
"{message}"

위 메시지를 분석하여 다음 JSON 형식으로 응답해주세요:

{{
  "form_updates": {{
    "product_name": "제품명 (추출되면)",
    "product_description": "제품 설명 (추출되면)",
    "category": "beauty|food|fashion|electronics|service 중 하나 (추출되면)",
    "target_ages": ["10-19", "20-29", "30-39", "40-49", "50-59", "60+"] 중에서 (추출되면),
    "target_genders": ["남성", "여성", "무관"] 중에서 (추출되면),
    "target_interests": ["뷰티", "건강", "여행" 등] (추출되면),
    "copy_tone": "professional|casual|impact 중 하나 (추출되면)"
  }},
  "response": "사용자에게 보낼 자연스러운 응답 메시지. 추출한 정보를 확인하고, 부족한 정보가 있으면 질문하세요.",
  "confidence": 0.0~1.0 사이의 추출 신뢰도,
  "next_question": "다음에 물어볼 질문 (부족한 정보가 있으면)"
}}

**중요 규칙:**
1. 메시지에서 확실하게 추출된 정보만 form_updates에 포함하세요
2. 불확실한 정보는 포함하지 마세요
3. response는 친근하고 자연스럽게 작성하세요
4. 필요한 정보가 모두 모이면 "왼쪽 폼을 확인하시고, 콘텐츠 생성 버튼을 눌러주세요!"라고 안내하세요
5. 나이대는 "20대" → ["20-29"], "20대 30대" → ["20-29", "30-39"]로 변환
6. 성별은 "여성" → ["여성"], "남녀" → ["남성", "여성"]으로 변환

JSON만 출력하고 다른 설명은 하지 마세요.
"""

        try:
            response_text = await self.generate_text(prompt, temperature=0.7)
            parsed_data = self._parse_json_response(response_text)

            # 기본값 설정
            if "form_updates" not in parsed_data:
                parsed_data["form_updates"] = {}
            if "response" not in parsed_data:
                parsed_data["response"] = "정보 감사합니다!"
            if "confidence" not in parsed_data:
                parsed_data["confidence"] = 0.5

            logger.info(f"✓ 챗봇 메시지 분석 완료 (confidence: {parsed_data['confidence']})")
            return parsed_data

        except Exception as e:
            logger.error(f"챗봇 메시지 분석 실패: {str(e)}")
            # 에러 시 기본 응답
            return {
                "form_updates": {},
                "response": "죄송합니다, 다시 한 번 말씀해주시겠어요?",
                "confidence": 0.0
            }

    def _parse_json_response(self, response_text: str) -> Dict:
        """
        Gemini 응답에서 JSON 추출 및 파싱

        Args:
            response_text: Gemini API 응답 텍스트

        Returns:
            파싱된 JSON 딕셔너리
        """
        # Gemini가 ```json ``` 으로 감쌀 수 있으므로 제거
        cleaned_text = response_text.strip()

        # 코드 블록 제거
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        elif cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[3:]

        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]

        cleaned_text = cleaned_text.strip()

        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 실패: {str(e)}")
            logger.error(f"응답 내용 (처음 500자): {cleaned_text[:500]}")
            raise ValueError(f"JSON 파싱 실패: {str(e)}")

    async def analyze_user_intent(self, user_request: str) -> Dict:
        """
        사용자의 콘텐츠 수정 요청을 분석하여 의도를 파악

        Args:
            user_request: 사용자가 입력한 수정 요청 (예: "알아서 해줘", "이미지 더 밝게")

        Returns:
            {
                "type": "all" | "image" | "copy",
                "intent": "구체적인 의도 설명",
                "modifications": ["적용할 수정사항들"]
            }
        """
        prompt = f"""
당신은 마케팅 콘텐츠 수정 요청을 분석하는 AI입니다.

사용자 요청: "{user_request}"

위 요청을 분석하여 다음 중 하나로 분류하고, JSON 형식으로 답변해주세요.

**분류 기준:**
- "all": 전체 콘텐츠를 다시 생성 (애매한 요청, "알아서", "마음대로", "전체 다시" 등)
- "image": 이미지만 수정/재생성 ("이미지", "사진", "그림", "비주얼" 키워드 포함)
- "copy": 카피(텍스트)만 수정/재생성 ("카피", "문구", "텍스트", "글" 키워드 포함)

**JSON 형식:**
{{
  "type": "all 또는 image 또는 copy",
  "intent": "사용자 의도에 대한 1줄 요약",
  "modifications": ["구체적인 수정사항1", "구체적인 수정사항2"]
}}

**예시:**
요청: "알아서 해줘"
→ {{"type": "all", "intent": "전체 재생성 요청", "modifications": ["모든 요소 새롭게 생성"]}}

요청: "이미지를 더 밝고 생동감있게"
→ {{"type": "image", "intent": "이미지 밝기와 생동감 개선", "modifications": ["밝기 증가", "채도 높임", "생동감 강조"]}}

요청: "카피를 짧고 임팩트있게"
→ {{"type": "copy", "intent": "카피 길이 축소 및 임팩트 강화", "modifications": ["문장 축약", "임팩트 있는 표현 사용"]}}

이제 위 사용자 요청을 분석하여 JSON만 출력하세요.
"""

        try:
            response = await self.generate_text(prompt, temperature=0.3)
            result = self._parse_json_response(response)

            logger.info(f"사용자 의도 분석 완료: {result}")
            return result

        except Exception as e:
            logger.error(f"사용자 의도 분석 실패: {str(e)}")
            # 실패 시 기본값으로 전체 재생성
            return {
                "type": "all",
                "intent": "분석 실패로 전체 재생성",
                "modifications": ["전체 재생성"]
            }


# 싱글톤 인스턴스
gemini_service = GeminiService()
