"""
Vector DB 서비스 모듈 (Qdrant + Voyage AI)
콘텐츠 임베딩 생성, 저장, 유사도 검색
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, PayloadSchemaType
import voyageai
from typing import List, Dict, Optional
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class VectorService:
    """Vector DB 서비스 (Qdrant + Voyage AI)"""

    def __init__(self):
        # Qdrant 클라이언트 초기화
        if settings.QDRANT_URL and settings.QDRANT_API_KEY:
            self.qdrant_client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
            )
            logger.info("Qdrant 클라이언트 초기화 완료")
        else:
            self.qdrant_client = None
            logger.warning("Qdrant URL 또는 API 키가 설정되지 않았습니다")

        # Voyage AI 클라이언트 초기화
        if settings.VOYAGE_AI_API_KEY:
            self.voyage_client = voyageai.Client(api_key=settings.VOYAGE_AI_API_KEY)
            logger.info("Voyage AI 클라이언트 초기화 완료")
        else:
            self.voyage_client = None
            logger.warning("Voyage AI API 키가 설정되지 않았습니다")

        # 컬렉션 이름
        self.collection_name = "contents"

    def ensure_collection(self):
        """
        Qdrant 컬렉션 생성 (없으면)

        Voyage AI voyage-3-large 모델: 1024 차원
        """
        if not self.qdrant_client:
            logger.error("Qdrant 클라이언트가 초기화되지 않았습니다")
            return False

        try:
            # 컬렉션 존재 여부 확인
            collections = self.qdrant_client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name not in collection_names:
                # 컬렉션 생성
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=1024,  # Voyage AI voyage-3-large 차원
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(f"Qdrant 컬렉션 생성 완료: {self.collection_name}")

                # 필터링용 인덱스 생성
                self.qdrant_client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="target_age",
                    field_schema=PayloadSchemaType.KEYWORD
                )
                self.qdrant_client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="target_gender",
                    field_schema=PayloadSchemaType.KEYWORD
                )
                self.qdrant_client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="category",
                    field_schema=PayloadSchemaType.KEYWORD
                )
                logger.info("Qdrant 인덱스 생성 완료")
            else:
                logger.info(f"Qdrant 컬렉션 이미 존재: {self.collection_name}")

            return True

        except Exception as e:
            logger.error(f"컬렉션 생성 실패: {str(e)}")
            return False

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        텍스트를 임베딩 벡터로 변환 (Voyage AI)

        Args:
            text: 임베딩할 텍스트

        Returns:
            임베딩 벡터 (1024차원) 또는 None
        """
        if not self.voyage_client:
            logger.error("Voyage AI 클라이언트가 초기화되지 않았습니다")
            return None

        try:
            # Voyage AI API 호출
            result = self.voyage_client.embed(
                [text],
                model="voyage-3-large",  # 2048 차원
                input_type="document"  # 문서 저장용
            )

            embedding = result.embeddings[0]
            logger.info(f"임베딩 생성 완료 (차원: {len(embedding)})")
            return embedding

        except Exception as e:
            logger.error(f"임베딩 생성 실패: {str(e)}")
            return None

    def save_content_embedding(
        self,
        content_id: int,
        copy_text: str,
        image_prompt: str,
        metadata: Dict
    ) -> bool:
        """
        콘텐츠 임베딩 생성 및 Vector DB 저장

        Args:
            content_id: 콘텐츠 ID
            copy_text: 카피 텍스트
            image_prompt: 이미지 프롬프트
            metadata: 메타데이터 (target_age, target_gender, category 등)

        Returns:
            성공 여부
        """
        if not self.qdrant_client:
            logger.error("Qdrant 클라이언트가 초기화되지 않았습니다")
            return False

        try:
            # 컬렉션 생성 (없으면)
            self.ensure_collection()

            # 콘텐츠 텍스트 생성 (카피 + 이미지 프롬프트)
            content_text = f"카피: {copy_text}\n이미지 프롬프트: {image_prompt}"

            # 임베딩 생성
            embedding = self.generate_embedding(content_text)
            if not embedding:
                return False

            # Vector DB에 저장
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=content_id,
                        vector=embedding,
                        payload={
                            "content_id": content_id,
                            "copy_text": copy_text,
                            "image_prompt": image_prompt,
                            **metadata
                        }
                    )
                ]
            )

            logger.info(f"콘텐츠 임베딩 저장 완료: content_id={content_id}")
            return True

        except Exception as e:
            logger.error(f"콘텐츠 임베딩 저장 실패: {str(e)}")
            return False

    def search_similar_contents(
        self,
        query_text: str,
        target_age: Optional[str] = None,
        target_gender: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict]:
        """
        유사 콘텐츠 검색

        Args:
            query_text: 검색 쿼리 (카피 + 이미지 프롬프트)
            target_age: 타겟 나이대 필터
            target_gender: 타겟 성별 필터
            category: 카테고리 필터
            limit: 결과 개수

        Returns:
            유사 콘텐츠 목록 [{"content_id": 1, "score": 0.85, ...}, ...]
        """
        if not self.qdrant_client:
            logger.error("Qdrant 클라이언트가 초기화되지 않았습니다")
            return []

        try:
            # 쿼리 임베딩 생성
            query_embedding = self.generate_embedding(query_text)
            if not query_embedding:
                return []

            # 필터 조건 생성
            must_conditions = []
            if target_age:
                must_conditions.append({
                    "key": "target_age",
                    "match": {"value": target_age}
                })
            if target_gender:
                must_conditions.append({
                    "key": "target_gender",
                    "match": {"value": target_gender}
                })
            if category:
                must_conditions.append({
                    "key": "category",
                    "match": {"value": category}
                })

            # 검색 실행
            search_result = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                query_filter={"must": must_conditions} if must_conditions else None
            )

            # 결과 변환
            results = []
            for hit in search_result:
                results.append({
                    "content_id": hit.payload.get("content_id"),
                    "score": hit.score,
                    "copy_text": hit.payload.get("copy_text"),
                    "image_prompt": hit.payload.get("image_prompt"),
                    "target_age": hit.payload.get("target_age"),
                    "target_gender": hit.payload.get("target_gender"),
                    "category": hit.payload.get("category"),
                })

            logger.info(f"유사 콘텐츠 검색 완료: {len(results)}개 발견")
            return results

        except Exception as e:
            logger.error(f"유사 콘텐츠 검색 실패: {str(e)}")
            return []

    def get_performance_reference(
        self,
        query_text: str,
        target_age: Optional[str] = None,
        target_gender: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 3
    ) -> List[Dict]:
        """
        과거 유사 콘텐츠의 성과 데이터 참조 (RAG)

        Args:
            query_text: 검색 쿼리 (카피 + 이미지 프롬프트)
            target_age: 타겟 나이대 필터
            target_gender: 타겟 성별 필터
            category: 카테고리 필터
            limit: 참조할 과거 콘텐츠 개수

        Returns:
            과거 유사 콘텐츠 성과 목록
        """
        from app.models.base import get_db
        from app.models.performance import Performance

        try:
            # 유사 콘텐츠 검색
            similar_contents = self.search_similar_contents(
                query_text=query_text,
                target_age=target_age,
                target_gender=target_gender,
                category=category,
                limit=limit
            )

            if not similar_contents:
                return []

            # DB에서 성과 데이터 가져오기
            db_gen = get_db()
            db = next(db_gen)

            try:
                content_ids = [content["content_id"] for content in similar_contents]
                performances = db.query(Performance).filter(
                    Performance.content_id.in_(content_ids)
                ).all()

                # 성과 데이터를 딕셔너리로 매핑
                performance_map = {p.content_id: p for p in performances}

                # 유사 콘텐츠와 성과 데이터 결합
                results = []
                for content in similar_contents:
                    content_id = content["content_id"]
                    performance = performance_map.get(content_id)

                    if performance:
                        results.append({
                            "content_id": content_id,
                            "similarity_score": content["score"],
                            "copy_text": content["copy_text"],
                            "image_prompt": content["image_prompt"],
                            "performance": {
                                "impressions": performance.impressions,
                                "clicks": performance.clicks,
                                "ctr": performance.ctr,
                                "engagement_rate": performance.engagement_rate,
                                "conversion_rate": performance.conversion_rate,
                                "confidence_score": performance.confidence_score
                            }
                        })

                logger.info(f"RAG 성과 참조: {len(results)}개 발견")
                return results

            finally:
                db.close()

        except Exception as e:
            logger.error(f"성과 참조 실패: {str(e)}")
            return []


# 싱글톤 인스턴스
vector_service = VectorService()
