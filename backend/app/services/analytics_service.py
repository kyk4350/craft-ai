"""
Analytics service for dashboard statistics
"""

import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.content import Content
from app.models.performance import Performance

logger = logging.getLogger(__name__)


class AnalyticsService:
    """통계 및 분석 서비스"""

    def __init__(self, db: Session):
        self.db = db

    def get_summary(self) -> Dict[str, Any]:
        """
        대시보드 핵심 지표 요약

        Returns:
            총 콘텐츠 수, 평균 CTR, 최고 성과, 이번주 증감 등
        """
        try:
            # 총 콘텐츠 수
            total_contents = self.db.query(Content).count()

            # 성과 데이터가 있는 콘텐츠들의 평균 지표
            performance_stats = self.db.query(
                func.avg(Performance.ctr).label('avg_ctr'),
                func.avg(Performance.engagement_rate).label('avg_engagement'),
                func.avg(Performance.conversion_rate).label('avg_conversion'),
                func.avg(Performance.brand_recall_score).label('avg_brand_recall'),
                func.max(Performance.ctr).label('max_ctr'),
                func.count(Performance.id).label('total_performances')
            ).first()

            # 최고 성과 콘텐츠
            best_content = self.db.query(
                Content, Performance
            ).join(
                Performance, Content.id == Performance.content_id
            ).order_by(
                desc(Performance.ctr)
            ).first()

            best_content_info = None
            if best_content:
                content, perf = best_content
                # product_name 우선순위: Content 테이블 -> Project -> "Unknown"
                product_name = content.product_name or (content.project.product_name if content.project else "Unknown")
                best_content_info = {
                    "content_id": content.id,
                    "copy_text": content.copy_text[:50] + "..." if len(content.copy_text) > 50 else content.copy_text,
                    "ctr": perf.ctr,
                    "product_name": product_name
                }

            return {
                "total_contents": total_contents,
                "total_with_performance": performance_stats.total_performances if performance_stats else 0,
                "avg_ctr": round(performance_stats.avg_ctr, 2) if performance_stats and performance_stats.avg_ctr else 0,
                "avg_engagement_rate": round(performance_stats.avg_engagement, 2) if performance_stats and performance_stats.avg_engagement else 0,
                "avg_conversion_rate": round(performance_stats.avg_conversion, 2) if performance_stats and performance_stats.avg_conversion else 0,
                "avg_brand_recall": round(performance_stats.avg_brand_recall, 2) if performance_stats and performance_stats.avg_brand_recall else 0,
                "max_ctr": round(performance_stats.max_ctr, 2) if performance_stats and performance_stats.max_ctr else 0,
                "best_content": best_content_info
            }

        except Exception as e:
            logger.error(f"❌ 요약 통계 조회 오류: {e}")
            return {
                "total_contents": 0,
                "total_with_performance": 0,
                "avg_ctr": 0,
                "avg_engagement_rate": 0,
                "avg_conversion_rate": 0,
                "avg_brand_recall": 0,
                "max_ctr": 0,
                "best_content": None
            }

    def get_performance_by_strategy(self) -> List[Dict[str, Any]]:
        """
        전략별 평균 성과 비교

        Returns:
            전략별 평균 CTR, 참여율, 전환율, 브랜드 기억도
        """
        try:
            # Content의 strategy 필드에서 전략명 추출 (JSON 필드)
            results = self.db.query(
                Content.strategy,
                func.avg(Performance.ctr).label('avg_ctr'),
                func.avg(Performance.engagement_rate).label('avg_engagement'),
                func.avg(Performance.conversion_rate).label('avg_conversion'),
                func.avg(Performance.brand_recall_score).label('avg_brand_recall'),
                func.count(Performance.id).label('count')
            ).join(
                Performance, Content.id == Performance.content_id
            ).group_by(
                Content.strategy
            ).all()

            strategy_stats = []
            for result in results:
                strategy = result.strategy
                if isinstance(strategy, dict):
                    strategy_name = strategy.get('name', 'Unknown')
                else:
                    strategy_name = 'Unknown'

                strategy_stats.append({
                    "strategy_name": strategy_name,
                    "avg_ctr": round(result.avg_ctr, 2) if result.avg_ctr else 0,
                    "avg_engagement_rate": round(result.avg_engagement, 2) if result.avg_engagement else 0,
                    "avg_conversion_rate": round(result.avg_conversion, 2) if result.avg_conversion else 0,
                    "avg_brand_recall": round(result.avg_brand_recall, 2) if result.avg_brand_recall else 0,
                    "count": result.count
                })

            return strategy_stats

        except Exception as e:
            logger.error(f"❌ 전략별 성과 조회 오류: {e}")
            return []

    def _normalize_age_group(self, age_group: str) -> str:
        """나이대 표기 정규화 (20-29 -> 20대)"""
        if not age_group:
            return "미지정"

        # 이미 한글 형식이면 그대로 반환
        if age_group.endswith('대'):
            return age_group

        # 숫자 범위 형식을 한글로 변환
        age_mapping = {
            '10-19': '10대',
            '20-29': '20대',
            '30-39': '30대',
            '40-49': '40대',
            '50-59': '50대',
            '60+': '60대 이상',
        }

        return age_mapping.get(age_group, age_group)

    def get_performance_by_target(self) -> List[Dict[str, Any]]:
        """
        타겟별 평균 성과 비교

        Returns:
            타겟(나이대×성별)별 평균 성과
        """
        try:
            results = self.db.query(
                Content.target_age_group,
                Content.target_gender,
                func.avg(Performance.ctr).label('avg_ctr'),
                func.avg(Performance.engagement_rate).label('avg_engagement'),
                func.avg(Performance.conversion_rate).label('avg_conversion'),
                func.avg(Performance.brand_recall_score).label('avg_brand_recall'),
                func.count(Performance.id).label('count')
            ).join(
                Performance, Content.id == Performance.content_id
            ).group_by(
                Content.target_age_group,
                Content.target_gender
            ).all()

            # 정규화된 타겟별로 집계
            aggregated = {}
            for result in results:
                normalized_age = self._normalize_age_group(result.target_age_group)
                gender = result.target_gender or '미지정'
                key = f"{normalized_age}_{gender}"

                if key not in aggregated:
                    aggregated[key] = {
                        "target_label": f"{normalized_age} {gender}",
                        "target_age_group": normalized_age,
                        "target_gender": gender,
                        "total_ctr": 0,
                        "total_engagement": 0,
                        "total_conversion": 0,
                        "total_brand_recall": 0,
                        "count": 0
                    }

                # 가중 평균 계산을 위해 누적
                aggregated[key]["total_ctr"] += (result.avg_ctr or 0) * result.count
                aggregated[key]["total_engagement"] += (result.avg_engagement or 0) * result.count
                aggregated[key]["total_conversion"] += (result.avg_conversion or 0) * result.count
                aggregated[key]["total_brand_recall"] += (result.avg_brand_recall or 0) * result.count
                aggregated[key]["count"] += result.count

            # 평균 계산
            target_stats = []
            for key, data in aggregated.items():
                count = data["count"]
                target_stats.append({
                    "target_label": data["target_label"],
                    "target_age_group": data["target_age_group"],
                    "target_gender": data["target_gender"],
                    "avg_ctr": round(data["total_ctr"] / count, 2) if count > 0 else 0,
                    "avg_engagement_rate": round(data["total_engagement"] / count, 2) if count > 0 else 0,
                    "avg_conversion_rate": round(data["total_conversion"] / count, 2) if count > 0 else 0,
                    "avg_brand_recall": round(data["total_brand_recall"] / count, 2) if count > 0 else 0,
                    "count": count
                })

            return target_stats

        except Exception as e:
            logger.error(f"❌ 타겟별 성과 조회 오류: {e}")
            return []

    def get_top_contents(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        최고 성과 콘텐츠 목록

        Args:
            limit: 조회할 콘텐츠 수

        Returns:
            CTR 높은 순으로 콘텐츠 목록
        """
        try:
            results = self.db.query(
                Content, Performance
            ).join(
                Performance, Content.id == Performance.content_id
            ).order_by(
                desc(Performance.ctr)
            ).limit(limit).all()

            top_contents = []
            for content, perf in results:
                # product_name 우선순위: Content 테이블 -> Project -> "Unknown"
                product_name = content.product_name or (content.project.product_name if content.project else "Unknown")

                # 타겟 표시 정규화
                normalized_age = self._normalize_age_group(content.target_age_group)
                target = f"{normalized_age} {content.target_gender or '미지정'}"

                top_contents.append({
                    "content_id": content.id,
                    "copy_text": content.copy_text[:80] + "..." if len(content.copy_text) > 80 else content.copy_text,
                    "product_name": product_name,
                    "target": target,
                    "ctr": round(perf.ctr, 2),
                    "engagement_rate": round(perf.engagement_rate, 2),
                    "conversion_rate": round(perf.conversion_rate, 2),
                    "created_at": content.created_at.isoformat() if content.created_at else None
                })

            return top_contents

        except Exception as e:
            logger.error(f"❌ 최고 성과 콘텐츠 조회 오류: {e}")
            return []
