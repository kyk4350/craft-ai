"""
이미지 스토리지 서비스
이미지 다운로드, 저장, 최적화

TODO: 프로덕션에서는 S3/CloudFlare R2 등 클라우드 스토리지로 교체
"""

import aiohttp
import aiofiles
from pathlib import Path
from typing import Optional
import logging
import hashlib
from datetime import datetime
from PIL import Image
import io

logger = logging.getLogger(__name__)


class ImageStorageService:
    """이미지 저장 및 최적화 서비스"""

    def __init__(self, storage_dir: str = "backend/storage/images"):
        """
        Args:
            storage_dir: 이미지 저장 디렉토리 (프로젝트 루트 기준)
        """
        # 프로젝트 루트 기준으로 경로 설정
        project_root = Path(__file__).parent.parent.parent.parent
        self.storage_dir = project_root / storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"이미지 스토리지 디렉토리: {self.storage_dir}")

    async def download_and_save(
        self,
        image_url: str,
        optimize: bool = True,
        max_size: tuple = (2048, 2048),
        quality: int = 85
    ) -> Optional[dict]:
        """
        이미지 다운로드 및 저장

        Args:
            image_url: 이미지 URL
            optimize: 최적화 여부
            max_size: 최대 크기 (width, height)
            quality: JPEG 품질 (1-100)

        Returns:
            {
                "file_path": "저장된 파일 경로",
                "public_url": "공개 URL",
                "original_url": "원본 URL",
                "size": 파일 크기 (bytes)
            }
        """
        try:
            logger.info(f"이미지 다운로드 시작: {image_url}")

            # 이미지 다운로드
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status != 200:
                        logger.error(f"이미지 다운로드 실패: HTTP {response.status}")
                        return None

                    image_data = await response.read()
                    logger.info(f"이미지 다운로드 완료: {len(image_data)} bytes (타입: {type(image_data)})")

            # 파일명 생성 (URL 해시 + 타임스탬프)
            url_hash = hashlib.md5(image_url.encode()).hexdigest()[:12]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{url_hash}.png"
            file_path = self.storage_dir / filename

            if optimize:
                # 이미지 최적화
                logger.info(f"이미지 최적화 시작...")
                optimized_data = self._optimize_image(
                    image_data,
                    max_size=max_size,
                    quality=quality
                )
                logger.info(f"이미지 최적화 완료: {len(optimized_data)} bytes")

                # 최적화된 이미지 저장
                async with aiofiles.open(str(file_path), 'wb') as f:
                    await f.write(optimized_data)

                file_size = len(optimized_data)
            else:
                # 원본 그대로 저장
                async with aiofiles.open(str(file_path), 'wb') as f:
                    await f.write(image_data)

                file_size = len(image_data)

            logger.info(f"✓ 이미지 저장 완료: {file_path} ({file_size:,} bytes)")

            return {
                "file_path": str(file_path),
                "public_url": self.get_public_url(filename),
                "original_url": image_url,
                "size": file_size
            }

        except Exception as e:
            logger.error(f"이미지 다운로드/저장 실패: {str(e)}")
            return None

    def _optimize_image(
        self,
        image_data: bytes,
        max_size: tuple = (2048, 2048),
        quality: int = 85
    ) -> bytes:
        """
        이미지 최적화

        - 크기 조정 (비율 유지)
        - PNG 최적화
        - 품질 조정

        Args:
            image_data: 원본 이미지 데이터
            max_size: 최대 크기
            quality: 압축 품질

        Returns:
            최적화된 이미지 데이터
        """
        try:
            logger.info(f"PIL 이미지 열기 시작... (데이터 타입: {type(image_data)}, 크기: {len(image_data)})")
            # PIL로 이미지 열기
            image = Image.open(io.BytesIO(image_data))
            logger.info(f"PIL 이미지 열기 완료: {image.size}, {image.mode}")

            # RGBA → RGB 변환 (필요 시)
            if image.mode == 'RGBA':
                # 흰색 배경 추가
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])  # alpha channel as mask
                image = background

            # 크기 조정 (비율 유지)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)

            # 최적화된 이미지를 bytes로 변환
            output = io.BytesIO()

            # PNG로 저장 (무손실, 최적화)
            image.save(output, format='PNG', optimize=True)

            optimized_data = output.getvalue()

            original_size = len(image_data)
            optimized_size = len(optimized_data)
            reduction = (1 - optimized_size / original_size) * 100

            logger.info(f"이미지 최적화: {original_size:,} → {optimized_size:,} bytes ({reduction:.1f}% 감소)")

            return optimized_data

        except Exception as e:
            logger.error(f"이미지 최적화 실패: {str(e)}")
            # 최적화 실패 시 원본 반환
            return image_data

    async def save_from_bytes(
        self,
        image_bytes: bytes,
        optimize: bool = True,
        max_size: tuple = (2048, 2048),
        quality: int = 85
    ) -> Optional[dict]:
        """
        bytes 데이터로부터 이미지 저장

        Args:
            image_bytes: 이미지 바이트 데이터
            optimize: 최적화 여부
            max_size: 최대 크기 (width, height)
            quality: JPEG 품질 (1-100)

        Returns:
            {
                "file_path": "저장된 파일 경로",
                "public_url": "공개 URL",
                "size": 파일 크기 (bytes)
            }
        """
        try:
            logger.info(f"이미지 저장 시작: {len(image_bytes)} bytes")

            # 파일명 생성 (바이트 해시 + 타임스탬프)
            data_hash = hashlib.md5(image_bytes).hexdigest()[:12]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{data_hash}.png"
            file_path = self.storage_dir / filename

            if optimize:
                # 이미지 최적화
                logger.info(f"이미지 최적화 시작...")
                optimized_data = self._optimize_image(
                    image_bytes,
                    max_size=max_size,
                    quality=quality
                )
                logger.info(f"이미지 최적화 완료: {len(optimized_data)} bytes")

                # 최적화된 이미지 저장
                async with aiofiles.open(str(file_path), 'wb') as f:
                    await f.write(optimized_data)

                file_size = len(optimized_data)
            else:
                # 원본 그대로 저장
                async with aiofiles.open(str(file_path), 'wb') as f:
                    await f.write(image_bytes)

                file_size = len(image_bytes)

            logger.info(f"✓ 이미지 저장 완료: {file_path} ({file_size:,} bytes)")

            return {
                "file_path": str(file_path),
                "public_url": self.get_public_url(filename),
                "size": file_size
            }

        except Exception as e:
            logger.error(f"이미지 저장 실패: {str(e)}")
            return None

    def get_public_url(self, filename: str) -> str:
        """
        저장된 파일의 공개 URL 생성

        개발 환경: FastAPI static files 경로
        프로덕션: TODO - S3/CDN URL로 교체 필요

        Args:
            filename: 파일명

        Returns:
            공개 URL
        """
        # 개발 환경: FastAPI static files 경로
        return f"/static/images/{filename}"


# 싱글톤 인스턴스
image_storage = ImageStorageService()
