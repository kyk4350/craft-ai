"""
타겟 고객 세분화 서비스

1,000개의 합성 타겟 프로필 데이터를 기반으로
사용자 요청에 맞는 타겟을 필터링하고 인사이트를 추출합니다.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Set
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)


class SegmentationService:
    """타겟 세분화 서비스"""

    def __init__(self, data_path: Optional[str] = None):
        """
        Args:
            data_path: 합성 데이터 JSON 파일 경로
        """
        if data_path is None:
            # 기본 경로: data/processed/target_profiles.json
            project_root = Path(__file__).parent.parent.parent.parent
            data_path = project_root / "data" / "processed" / "target_profiles.json"

        self.data_path = Path(data_path)
        self.profiles: List[Dict] = []
        self._load_data()

    def _load_data(self):
        """합성 데이터 로드"""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.profiles = json.load(f)
            logger.info(f"✓ 타겟 프로필 {len(self.profiles)}개 로드 완료")
        except FileNotFoundError:
            logger.error(f"데이터 파일을 찾을 수 없습니다: {self.data_path}")
            self.profiles = []
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 실패: {e}")
            self.profiles = []

    def filter_profiles(
        self,
        age_groups: Optional[List[str]] = None,
        genders: Optional[List[str]] = None,
        income_levels: Optional[List[str]] = None,
        interests: Optional[List[str]] = None,
        category: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        조건에 맞는 프로필 필터링 (OR 조건)

        Args:
            age_groups: 나이대 리스트 (10대, 20대, 30대, 40대, 50대, 60대+)
            genders: 성별 리스트 (남성, 여성)
            income_levels: 소득 수준 리스트 (저소득, 중소득, 중상소득, 고소득)
            interests: 관심사 리스트 (하나라도 포함되면 매칭)
            category: 제품 카테고리 (화장품, 식품, 패션, 전자제품, 서비스)
            limit: 최대 반환 개수

        Returns:
            필터링된 프로필 리스트
        """
        filtered = self.profiles.copy()

        # 나이대 필터 (OR 조건)
        if age_groups and len(age_groups) > 0:
            filtered = [p for p in filtered if p.get('age_group') in age_groups]
            logger.info(f"나이대 필터 ({age_groups}): {len(filtered)}개")

        # 성별 필터 (OR 조건, "무관"은 항상 포함)
        if genders and len(genders) > 0:
            filtered = [
                p for p in filtered
                if p.get('gender') in genders or p.get('gender') == "무관"
            ]
            logger.info(f"성별 필터 ({genders} + 무관): {len(filtered)}개")

        # 소득 필터 (OR 조건)
        if income_levels and len(income_levels) > 0:
            filtered = [p for p in filtered if p.get('income_level') in income_levels]
            logger.info(f"소득 필터 ({income_levels}): {len(filtered)}개")

        # 관심사 필터 (하나라도 포함)
        if interests and len(interests) > 0:
            filtered = [
                p for p in filtered
                if any(interest in p.get('interests', []) for interest in interests)
            ]
            logger.info(f"관심사 필터 ({interests}): {len(filtered)}개")

        # 카테고리 필터 (단일 선택)
        if category:
            filtered = [p for p in filtered if p.get('category') == category]
            logger.info(f"카테고리 필터 ({category}): {len(filtered)}개")

        # 개수 제한
        if limit and limit > 0:
            filtered = filtered[:limit]

        logger.info(f"✓ 최종 필터링 결과: {len(filtered)}개 프로필")
        return filtered

    def extract_insights(self, profiles: List[Dict]) -> Dict:
        """
        프로필 리스트에서 공통 인사이트 추출

        Args:
            profiles: 타겟 프로필 리스트

        Returns:
            인사이트 딕셔너리
        """
        if not profiles:
            return {
                "error": "프로필이 없습니다",
                "count": 0
            }

        # 기본 통계
        total_count = len(profiles)

        # 나이대 분포
        age_dist = Counter([p.get('age_group') for p in profiles])

        # 성별 분포
        gender_dist = Counter([p.get('gender') for p in profiles])

        # 소득 분포
        income_dist = Counter([p.get('income_level') for p in profiles])

        # 카테고리 분포
        category_dist = Counter([p.get('category') for p in profiles])

        # 관심사 집계 (전체)
        all_interests = []
        for p in profiles:
            all_interests.extend(p.get('interests', []))
        interest_counts = Counter(all_interests)
        top_interests = interest_counts.most_common(10)

        # 고충(Pain Points) 집계
        all_pain_points = []
        for p in profiles:
            all_pain_points.extend(p.get('pain_points', []))
        pain_counts = Counter(all_pain_points)
        top_pain_points = pain_counts.most_common(10)

        # 선호 채널 집계
        all_channels = []
        for p in profiles:
            all_channels.extend(p.get('preferred_channels', []))
        channel_counts = Counter(all_channels)
        top_channels = channel_counts.most_common(5)

        # 라이프스타일 키워드 추출
        all_lifestyles = [p.get('lifestyle', '') for p in profiles]
        lifestyle_keywords = self._extract_lifestyle_keywords(all_lifestyles)

        return {
            "count": total_count,
            "demographics": {
                "age_distribution": dict(age_dist),
                "gender_distribution": dict(gender_dist),
                "income_distribution": dict(income_dist),
                "category_distribution": dict(category_dist)
            },
            "psychographics": {
                "top_interests": [{"interest": k, "count": v} for k, v in top_interests],
                "top_pain_points": [{"pain_point": k, "count": v} for k, v in top_pain_points],
                "lifestyle_keywords": lifestyle_keywords
            },
            "channels": {
                "top_channels": [{"channel": k, "count": v} for k, v in top_channels]
            },
            "marketing_recommendations": self._generate_marketing_recommendations(
                top_interests, top_pain_points, top_channels, age_dist, income_dist
            )
        }

    def _extract_lifestyle_keywords(self, lifestyles: List[str]) -> List[str]:
        """라이프스타일 텍스트에서 키워드 추출"""
        # 모든 라이프스타일 텍스트를 합침
        combined = ", ".join(lifestyles)

        # 쉼표와 공백으로 분리
        words = [w.strip() for w in combined.replace(",", " ").split()]

        # 빈도수 계산
        word_counts = Counter(words)

        # 상위 10개 키워드
        top_keywords = [k for k, v in word_counts.most_common(10)]

        return top_keywords

    def _generate_marketing_recommendations(
        self,
        top_interests: List[tuple],
        top_pain_points: List[tuple],
        top_channels: List[tuple],
        age_dist: Counter,
        income_dist: Counter
    ) -> Dict:
        """마케팅 추천 사항 생성"""

        # 주요 관심사 (상위 3개)
        key_interests = [k for k, v in top_interests[:3]]

        # 주요 고충 (상위 3개)
        key_pain_points = [k for k, v in top_pain_points[:3]]

        # 주요 채널 (상위 2개)
        key_channels = [k for k, v in top_channels[:2]]

        # 주요 나이대
        dominant_age = age_dist.most_common(1)[0][0] if age_dist else "알 수 없음"

        # 주요 소득 수준
        dominant_income = income_dist.most_common(1)[0][0] if income_dist else "알 수 없음"

        # 톤앤매너 추천
        tone = self._recommend_tone(dominant_age, dominant_income)

        # 메시지 전략 추천
        message_strategy = self._recommend_message_strategy(key_pain_points, key_interests)

        return {
            "key_insights": {
                "dominant_age_group": dominant_age,
                "dominant_income_level": dominant_income,
                "key_interests": key_interests,
                "key_pain_points": key_pain_points,
                "key_channels": key_channels
            },
            "content_strategy": {
                "tone_and_manner": tone,
                "message_strategy": message_strategy,
                "recommended_channels": key_channels
            }
        }

    def _recommend_tone(self, age_group: str, income_level: str) -> str:
        """나이대와 소득 수준에 따른 톤앤매너 추천"""
        if age_group in ["10대", "20대"]:
            return "친근하고 트렌디한 톤, 이모티콘 활용, 반말 가능"
        elif age_group == "30대":
            if income_level in ["고소득", "중상소득"]:
                return "전문적이면서도 친근한 톤, 존댓말"
            else:
                return "실용적이고 공감형 톤, 존댓말"
        else:  # 40대+
            if income_level in ["고소득", "중상소득"]:
                return "프리미엄하고 품격 있는 톤, 존댓말"
            else:
                return "신뢰감 있고 따뜻한 톤, 존댓말"

    def _recommend_message_strategy(
        self,
        pain_points: List[str],
        interests: List[str]
    ) -> List[str]:
        """고충과 관심사 기반 메시지 전략 추천"""
        strategies = []

        # Pain point 기반 전략
        if pain_points:
            strategies.append(
                f"'{pain_points[0]}' 문제를 해결해주는 솔루션 강조"
            )

        # Interest 기반 전략
        if interests:
            strategies.append(
                f"'{interests[0]}' 관심사와 연결하여 공감 형성"
            )

        # 기본 전략
        if not strategies:
            strategies.append("제품의 핵심 가치와 차별점 강조")

        strategies.append("타겟의 라이프스타일에 자연스럽게 녹아드는 스토리텔링")
        strategies.append("구체적인 사용 시나리오와 결과 제시")

        return strategies

    def search_by_keywords(self, keywords: List[str], limit: int = 50) -> List[Dict]:
        """
        키워드로 프로필 검색 (관심사, 고충, 라이프스타일에서 검색)

        Args:
            keywords: 검색 키워드 리스트
            limit: 최대 반환 개수

        Returns:
            매칭된 프로필 리스트
        """
        matched = []

        for profile in self.profiles:
            # 관심사에서 검색
            interests = profile.get('interests', [])

            # 고충에서 검색
            pain_points = profile.get('pain_points', [])

            # 라이프스타일에서 검색
            lifestyle = profile.get('lifestyle', '')

            # 채널에서 검색
            channels = profile.get('preferred_channels', [])

            # 키워드 매칭
            for keyword in keywords:
                keyword_lower = keyword.lower()

                # 각 필드에서 부분 매칭
                if (any(keyword_lower in interest.lower() for interest in interests) or
                    any(keyword_lower in pain.lower() for pain in pain_points) or
                    keyword_lower in lifestyle.lower() or
                    any(keyword_lower in channel.lower() for channel in channels)):
                    matched.append(profile)
                    break  # 중복 추가 방지

            if len(matched) >= limit:
                break

        logger.info(f"키워드 검색 ({keywords}): {len(matched)}개 프로필 매칭")
        return matched

    def get_all_segments(self) -> Dict:
        """
        전체 세그먼트 요약 정보 반환

        Returns:
            세그먼트별 카운트
        """
        age_groups = Counter([p.get('age_group') for p in self.profiles])
        genders = Counter([p.get('gender') for p in self.profiles])
        income_levels = Counter([p.get('income_level') for p in self.profiles])
        categories = Counter([p.get('category') for p in self.profiles])

        # 모든 고유 관심사
        all_interests = set()
        for p in self.profiles:
            all_interests.update(p.get('interests', []))

        return {
            "total_profiles": len(self.profiles),
            "age_groups": dict(age_groups),
            "genders": dict(genders),
            "income_levels": dict(income_levels),
            "categories": dict(categories),
            "unique_interests": sorted(list(all_interests))
        }


# 싱글톤 인스턴스
_segmentation_service = None


def get_segmentation_service() -> SegmentationService:
    """세분화 서비스 싱글톤 인스턴스 반환"""
    global _segmentation_service
    if _segmentation_service is None:
        _segmentation_service = SegmentationService()
    return _segmentation_service
