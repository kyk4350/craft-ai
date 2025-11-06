"""
Performance analysis service
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import google.generativeai as genai
import json
import asyncio

from app.models.performance import Performance, DataSource
from app.models.content import Content
from app.config import settings
from app.services.vector_service import vector_service

logger = logging.getLogger(__name__)

# Gemini API 설정
genai.configure(api_key=settings.GEMINI_API_KEY)


class PerformanceService:
    """성과 분석 서비스"""

    def __init__(self, db: Session):
        self.db = db
        self.gemini_model = genai.GenerativeModel("gemini-2.0-flash-exp")

    async def generate_personas(
        self,
        target_age_group: str,
        target_gender: str,
        target_interests: List[str],
        count: int = 10
    ) -> List[Dict[str, Any]]:
        """타겟에 맞는 가상 페르소나 생성"""

        prompt = f"""
당신은 마케팅 전문가입니다. 아래 타겟 조건에 맞는 가상의 사용자 페르소나 {count}명을 생성하세요.

타겟 조건:
- 나이대: {target_age_group}
- 성별: {target_gender}
- 관심사: {', '.join(target_interests)}

각 페르소나는 다음 정보를 포함해야 합니다:
1. 이름 (가명)
2. 나이
3. 직업
4. 성격 특징 (2-3줄)
5. SNS 사용 패턴
6. 구매 성향
7. 광고 반응 성향

**출력 형식은 반드시 JSON 배열이어야 합니다:**

[
  {{
    "name": "김미래",
    "age": 25,
    "occupation": "직장인",
    "personality": "트렌드에 민감하고 새로운 것을 시도하길 좋아함.",
    "sns_usage": {{
      "platforms": ["Instagram", "YouTube"],
      "daily_hours": 3
    }},
    "purchase_behavior": "충동구매형",
    "ad_sensitivity": {{
      "level": "높음",
      "triggers": ["비주얼이 예쁜 광고", "인플루언서 추천"]
    }}
  }}
]
"""

        try:
            response = await asyncio.to_thread(
                self.gemini_model.generate_content,
                prompt
            )

            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()

            personas = json.loads(text)
            logger.info(f"✅ {len(personas)}명의 페르소나 생성 완료")
            return personas

        except Exception as e:
            logger.error(f"❌ 페르소나 생성 오류: {e}")
            return []

    async def simulate_reactions(
        self,
        personas: List[Dict[str, Any]],
        content_data: Dict[str, Any],
        similar_contents: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """페르소나별 콘텐츠 반응 시뮬레이션 (RAG 적용)"""

        # RAG: 유사 콘텐츠 성과 데이터를 참고 자료로 추가
        reference_section = ""
        if similar_contents:
            reference_section = "\n\n**참고: 유사 콘텐츠의 과거 성과 데이터**\n"
            reference_section += "아래는 타겟과 콘텐츠가 유사한 과거 콘텐츠들의 실제/예측 성과입니다. 이를 참고하여 더 정확한 예측을 하세요.\n\n"

            for i, similar in enumerate(similar_contents[:3], 1):  # 상위 3개만 사용
                reference_section += f"{i}. 유사도: {similar['score']:.2f}\n"
                reference_section += f"   카피: {similar['copy_text'][:100]}...\n"
                reference_section += f"   타겟: {similar['target_age']} {similar['target_gender']}\n"

                # 해당 콘텐츠의 성과 데이터가 있다면 포함
                perf = similar.get('performance')
                if perf:
                    reference_section += f"   성과: CTR {perf.get('ctr', 0):.1f}%, 참여율 {perf.get('engagement_rate', 0):.1f}%, "
                    reference_section += f"전환율 {perf.get('conversion_rate', 0):.1f}%, 브랜드 기억도 {perf.get('brand_recall_score', 0):.0f}\n"
                reference_section += "\n"

        prompt = f"""
당신은 마케팅 성과 분석 전문가입니다.
아래 페르소나들이 주어진 마케팅 콘텐츠를 봤을 때의 반응을 시뮬레이션하세요.

**페르소나 정보:**
{json.dumps(personas, ensure_ascii=False, indent=2)}

**마케팅 콘텐츠:**
- 제품: {content_data.get('product_name')}
- 전략: {content_data.get('strategy', {}).get('name')} - {content_data.get('strategy', {}).get('core_message')}
- 카피: {content_data.get('copy_text')}
- 해시태그: {', '.join(content_data.get('hashtags', []))}
{reference_section}
각 페르소나의 반응을 예측하세요:
1. will_click: 클릭 여부 (true/false)
2. engagement_action: 참여 행동 (null, "like", "comment", "share", "save")
3. will_convert: 전환 여부 (true/false)
4. brand_recall: 브랜드 기억도 (0-100)
5. reason: 이유 (1-2줄)

**출력 형식은 JSON 객체여야 합니다:**

{{
  "reactions": [
    {{
      "persona_name": "김미래",
      "will_click": true,
      "engagement_action": "save",
      "will_convert": false,
      "brand_recall": 75,
      "reason": "비주얼이 예쁘고 트렌디해서 관심이 가지만, 당장 필요한 제품은 아니라 나중을 위해 저장만 함"
    }}
  ],
  "overall_metrics": {{
    "total_impressions": {len(personas)},
    "total_clicks": <클릭한 페르소나 수>,
    "ctr": <클릭률 %>,
    "engagement_rate": <참여한 페르소나 비율 %>,
    "conversion_rate": <전환한 페르소나 비율 %>,
    "avg_brand_recall": <평균 브랜드 기억도>
  }}
}}
"""

        try:
            response = await asyncio.to_thread(
                self.gemini_model.generate_content,
                prompt
            )

            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()

            result = json.loads(text)
            logger.info(f"✅ 성과 시뮬레이션 완료 - CTR: {result['overall_metrics']['ctr']:.2f}%")
            return result

        except Exception as e:
            logger.error(f"❌ 반응 시뮬레이션 오류: {e}")
            return None

    async def predict_performance(
        self,
        content_id: int
    ) -> Optional[Performance]:
        """
        콘텐츠 성과 예측 (AI 시뮬레이션)

        Args:
            content_id: 콘텐츠 ID

        Returns:
            Performance 객체
        """
        try:
            # 콘텐츠 조회
            content = self.db.query(Content).filter(Content.id == content_id).first()
            if not content:
                logger.error(f"콘텐츠 ID {content_id}를 찾을 수 없습니다.")
                return None

            # 콘텐츠 데이터 준비
            content_data = {
                "product_name": content.project.product_name if content.project else "제품",
                "product_description": content.project.product_description if content.project else "",
                "strategy": content.strategy if isinstance(content.strategy, dict) else {},
                "copy_text": content.copy_text,
                "hashtags": content.hashtags or [],
                "image_prompt": content.image_prompt
            }

            # 1. 페르소나 생성
            logger.info(f"[1/4] 페르소나 생성 중...")
            personas = await self.generate_personas(
                target_age_group=content.target_age_group or "20대",
                target_gender=content.target_gender or "무관",
                target_interests=content.target_interests or ["일반"],
                count=100  # 100명의 페르소나로 더 정확한 시뮬레이션
            )

            if not personas:
                logger.error("페르소나 생성 실패")
                return None

            # 2. RAG: 유사 콘텐츠 검색 및 성과 데이터 수집
            logger.info(f"[2/4] 유사 콘텐츠 검색 중... (RAG)")
            similar_contents = []
            try:
                # Vector DB에서 유사 콘텐츠 검색
                query_text = f"카피: {content_data['copy_text']}\n이미지 프롬프트: {content_data['image_prompt']}"
                similar_results = vector_service.search_similar_contents(
                    query_text=query_text,
                    target_age=content.target_age_group,
                    target_gender=content.target_gender,
                    limit=5
                )

                # 각 유사 콘텐츠의 성과 데이터 조회
                for similar in similar_results:
                    similar_content_id = similar.get('content_id')
                    if similar_content_id and similar_content_id != content_id:
                        # 해당 콘텐츠의 성과 데이터 조회
                        perf = self.db.query(Performance).filter(
                            Performance.content_id == similar_content_id
                        ).first()

                        if perf:
                            similar['performance'] = {
                                'ctr': perf.ctr,
                                'engagement_rate': perf.engagement_rate,
                                'conversion_rate': perf.conversion_rate,
                                'brand_recall_score': perf.brand_recall_score
                            }
                            similar_contents.append(similar)

                if similar_contents:
                    logger.info(f"✓ 유사 콘텐츠 {len(similar_contents)}개 발견 (성과 데이터 포함)")
                else:
                    logger.info("⚠️  유사 콘텐츠가 없거나 성과 데이터가 없습니다. 기본 예측으로 진행합니다.")

            except Exception as e:
                logger.warning(f"⚠️  유사 콘텐츠 검색 실패: {str(e)}. 기본 예측으로 진행합니다.")

            # 3. 반응 시뮬레이션 (RAG 적용)
            logger.info(f"[3/4] 반응 시뮬레이션 중... (RAG 적용)")
            simulation_result = await self.simulate_reactions(
                personas=personas,
                content_data=content_data,
                similar_contents=similar_contents if similar_contents else None
            )

            if not simulation_result:
                logger.error("반응 시뮬레이션 실패")
                return None

            # 4. Performance 객체 생성 (실제 캠페인 규모로 스케일업)
            logger.info(f"[4/4] 성과 데이터 저장 중...")
            metrics = simulation_result['overall_metrics']

            # 시뮬레이션 결과를 실제 캠페인 규모로 스케일업
            # 100명 시뮬레이션 → 20,000~50,000명 캠페인 규모
            import random
            scale_factor = random.randint(200, 500)  # 20,000~50,000명 규모

            scaled_impressions = metrics['total_impressions'] * scale_factor
            scaled_clicks = int(metrics['total_clicks'] * scale_factor)

            performance = Performance(
                content_id=content_id,
                data_source=DataSource.AI_SIMULATION,
                impressions=scaled_impressions,
                clicks=scaled_clicks,
                ctr=metrics['ctr'],  # 비율은 동일
                engagement_rate=metrics['engagement_rate'],  # 비율은 동일
                conversion_rate=metrics['conversion_rate'],  # 비율은 동일
                brand_recall_score=metrics['avg_brand_recall'],
                personas_data={
                    "personas": personas[:10],  # 처음 10명만 저장 (용량 절약)
                    "reactions": simulation_result['reactions'][:10],
                    "simulation_scale": scale_factor
                },
                confidence_score=0.75  # AI 예측 신뢰도
            )

            self.db.add(performance)
            self.db.commit()
            self.db.refresh(performance)

            logger.info(f"✅ 성과 예측 완료 - Performance ID: {performance.id}")
            return performance

        except Exception as e:
            logger.error(f"❌ 성과 예측 오류: {e}")
            self.db.rollback()
            return None

    def get_performance(self, content_id: int) -> Optional[Performance]:
        """콘텐츠의 성과 데이터 조회"""
        return self.db.query(Performance).filter(
            Performance.content_id == content_id
        ).first()

    def get_performance_summary(self, content_id: int) -> Dict[str, Any]:
        """콘텐츠의 성과 요약 조회"""
        performance = self.get_performance(content_id)

        if not performance:
            return {
                "exists": False,
                "message": "성과 데이터가 없습니다."
            }

        return {
            "exists": True,
            "data_source": performance.data_source.value,
            "metrics": {
                "impressions": performance.impressions,
                "clicks": performance.clicks,
                "ctr": performance.ctr,
                "engagement_rate": performance.engagement_rate,
                "conversion_rate": performance.conversion_rate,
                "brand_recall_score": performance.brand_recall_score
            },
            "confidence_score": performance.confidence_score,
            "is_ai_prediction": performance.data_source == DataSource.AI_SIMULATION
        }
