"""
콘텐츠 성과 시뮬레이션 스크립트

Gemini API를 사용하여 가상 사용자 페르소나를 생성하고
각 페르소나의 콘텐츠 반응을 시뮬레이션합니다.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import google.generativeai as genai
from dotenv import load_dotenv

# 환경 변수 로드 (backend/.env)
load_dotenv(project_root / "backend" / ".env")

# Gemini API 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")

genai.configure(api_key=GEMINI_API_KEY)


class PerformanceSimulator:
    """성과 시뮬레이터"""

    def __init__(self):
        self.model = genai.GenerativeModel("gemini-2.0-flash-exp")

    async def generate_personas(
        self,
        target_age_group: str,
        target_gender: str,
        target_interests: List[str],
        count: int = 10
    ) -> List[Dict[str, Any]]:
        """
        타겟에 맞는 가상 페르소나 생성

        Args:
            target_age_group: 타겟 나이대 (예: "20대")
            target_gender: 타겟 성별 (예: "여성")
            target_interests: 타겟 관심사 리스트
            count: 생성할 페르소나 수

        Returns:
            페르소나 리스트
        """
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
5. SNS 사용 패턴 (어떤 플랫폼을 주로 사용하는지, 하루 평균 사용 시간)
6. 구매 성향 (충동구매형, 신중형, 가성비형 등)
7. 광고 반응 성향 (광고에 민감한 정도, 어떤 광고에 반응하는지)

**출력 형식은 반드시 JSON 배열이어야 합니다:**

[
  {{
    "name": "김미래",
    "age": 25,
    "occupation": "직장인",
    "personality": "트렌드에 민감하고 새로운 것을 시도하길 좋아함. SNS를 통해 정보를 빠르게 수집하는 편.",
    "sns_usage": {{
      "platforms": ["Instagram", "YouTube"],
      "daily_hours": 3
    }},
    "purchase_behavior": "충동구매형 - 마음에 들면 바로 구매하는 편",
    "ad_sensitivity": {{
      "level": "높음",
      "triggers": ["비주얼이 예쁜 광고", "인플루언서 추천", "한정판/프로모션"]
    }}
  }}
]
"""

        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )

            # JSON 파싱
            text = response.text.strip()
            # Markdown 코드 블록 제거
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()

            personas = json.loads(text)

            print(f"✅ {len(personas)}명의 페르소나 생성 완료")
            return personas

        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 오류: {e}")
            print(f"응답 텍스트: {text[:500]}")
            return []
        except Exception as e:
            print(f"❌ 페르소나 생성 오류: {e}")
            return []

    async def simulate_reactions(
        self,
        personas: List[Dict[str, Any]],
        content_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        페르소나별 콘텐츠 반응 시뮬레이션

        Args:
            personas: 페르소나 리스트
            content_data: 콘텐츠 정보 (전략, 카피, 이미지 프롬프트)

        Returns:
            시뮬레이션 결과
        """
        prompt = f"""
당신은 마케팅 성과 분석 전문가입니다.
아래 페르소나들이 주어진 마케팅 콘텐츠를 봤을 때의 반응을 시뮬레이션하세요.

**페르소나 정보:**
{json.dumps(personas, ensure_ascii=False, indent=2)}

**마케팅 콘텐츠:**
- 제품명: {content_data.get('product_name')}
- 제품 설명: {content_data.get('product_description')}
- 마케팅 전략: {content_data.get('strategy', {}).get('name')} - {content_data.get('strategy', {}).get('core_message')}
- 광고 카피: {content_data.get('copy_text')}
- 해시태그: {', '.join(content_data.get('hashtags', []))}
- 이미지 컨셉: {content_data.get('image_prompt', '')[:200]}

각 페르소나에 대해 다음을 예측하세요:
1. **will_click**: 이 광고를 클릭할 확률 (true/false)
2. **engagement_action**: 참여 행동 (null, "like", "comment", "share", "save" 중 하나)
3. **will_convert**: 구매/전환할 확률 (true/false)
4. **brand_recall**: 브랜드 기억도 점수 (0-100, 높을수록 잘 기억)
5. **reason**: 이렇게 반응하는 이유 (1-2줄)

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
                self.model.generate_content,
                prompt
            )

            # JSON 파싱
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()

            result = json.loads(text)

            print(f"✅ 성과 시뮬레이션 완료")
            print(f"   - CTR: {result['overall_metrics']['ctr']:.2f}%")
            print(f"   - 참여도: {result['overall_metrics']['engagement_rate']:.2f}%")
            print(f"   - 전환율: {result['overall_metrics']['conversion_rate']:.2f}%")
            print(f"   - 브랜드 기억도: {result['overall_metrics']['avg_brand_recall']:.1f}/100")

            return result

        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 오류: {e}")
            print(f"응답 텍스트: {text[:500]}")
            return None
        except Exception as e:
            print(f"❌ 반응 시뮬레이션 오류: {e}")
            return None


async def main():
    """메인 실행 함수"""

    print("=" * 60)
    print("콘텐츠 성과 시뮬레이션 테스트")
    print("=" * 60)

    simulator = PerformanceSimulator()

    # 테스트 데이터
    test_target = {
        "age_group": "20대",
        "gender": "여성",
        "interests": ["뷰티", "스킨케어", "자기관리"]
    }

    test_content = {
        "product_name": "센텔라 진정 크림",
        "product_description": "민감한 피부를 위한 저자극 보습 크림",
        "strategy": {
            "name": "감성적 공감",
            "core_message": "민감한 당신의 피부, 센텔라가 지켜줄게요"
        },
        "copy_text": "하루 종일 예민했던 피부,\n이제는 센텔라로 진정하세요.\n민감 피부 전용 저자극 크림",
        "hashtags": ["#센텔라크림", "#민감피부", "#진정크림"],
        "image_prompt": "Soft, calming skincare product in pastel green packaging, centered on a minimal table with natural morning light"
    }

    print(f"\n[1단계] 페르소나 생성")
    print(f"타겟: {test_target['age_group']} {test_target['gender']}, 관심사: {', '.join(test_target['interests'])}")
    print("-" * 60)

    personas = await simulator.generate_personas(
        target_age_group=test_target["age_group"],
        target_gender=test_target["gender"],
        target_interests=test_target["interests"],
        count=10
    )

    if not personas:
        print("페르소나 생성 실패. 종료합니다.")
        return

    print(f"\n생성된 페르소나 샘플:")
    print(json.dumps(personas[0], ensure_ascii=False, indent=2))

    print(f"\n[2단계] 콘텐츠 반응 시뮬레이션")
    print(f"제품: {test_content['product_name']}")
    print(f"카피: {test_content['copy_text'][:50]}...")
    print("-" * 60)

    result = await simulator.simulate_reactions(
        personas=personas,
        content_data=test_content
    )

    if not result:
        print("반응 시뮬레이션 실패. 종료합니다.")
        return

    # 결과 저장
    output_dir = project_root / "data" / "simulations"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "test_simulation.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "target": test_target,
            "content": test_content,
            "personas": personas,
            "simulation_result": result
        }, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 시뮬레이션 결과 저장: {output_file}")

    print("\n" + "=" * 60)
    print("성과 시뮬레이션 테스트 완료!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
