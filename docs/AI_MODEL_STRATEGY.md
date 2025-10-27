# AI 모델 사용 전략

예산 5만원 내에서 효율적으로 개발하기 위한 AI 모델 사용 전략

## 전략 개요

### 이미지 생성
- **Week 2-3 (개발 초기)**: Mock 이미지 (Unsplash) - 무료
- **Week 4-6 (개발 중)**: Stability AI SDXL - $0.004/이미지
- **Week 7 (최종 배포)**: 나노바나나 - $0.039/이미지

### 텍스트 생성
- **Week 2-6 (개발 중)**: Gemini 1.5 Flash 무료 tier - 1,500 requests/day
- **Week 7 또는 무료 초과 시**: Gemini 1.5 Flash 유료 - 매우 저렴

## 상세 전략

### 1. 이미지 생성

#### Mock (Unsplash API)
```
프로바이더: mock
사용 시기: Week 2-3
비용: 무료
목적: UI/UX 개발, API 구조 구축
품질: 실제 사진 (마케팅용으로 적합)
```

#### Stability AI SDXL
```
프로바이더: stability
사용 시기: Week 4-6
비용: $0.004/이미지 (약 5원)
예상 사용량: 500장 = $2 (약 2,600원)
목적: 실제 생성 로직 테스트, 프롬프트 최적화
품질: 좋음 (개발/테스트용으로 충분)
API: https://platform.stability.ai/
```

#### 나노바나나 (Gemini 2.5 Flash Image)
```
프로바이더: nanobanana
사용 시기: Week 7
비용: $0.039/이미지 (약 50원)
예상 사용량: 200장 = $7.8 (약 10,000원)
목적: 최종 배포, 고품질 이미지
품질: 최고 (프로덕션 레벨)
```

### 2. 텍스트 생성

#### Gemini 1.5 Flash (무료 tier)
```
모델: gemini-1.5-flash
사용 시기: Week 2-6
비용: 무료
제한: 1,500 requests/day, 15 RPM
목적: 전략 제안, 카피 생성, 프롬프트 변환
충분: 개발 단계에서 충분함
```

#### Gemini 1.5 Flash (유료)
```
모델: gemini-1.5-flash
사용 시기: Week 7 또는 무료 초과 시
비용: 매우 저렴
  - 입력: $0.075 / 1M tokens
  - 출력: $0.30 / 1M tokens
예상 비용: 약 5,000-10,000원
목적: 최종 배포, 안정적인 서비스
```

## 환경 변수 설정

### 개발 초기 (Week 2-3)
```bash
IMAGE_PROVIDER=mock
GEMINI_MODEL=gemini-1.5-flash
GEMINI_API_KEY=your_key
# STABILITY_API_KEY 불필요
```

### 개발 중기 (Week 4-6)
```bash
IMAGE_PROVIDER=stability
GEMINI_MODEL=gemini-1.5-flash
GEMINI_API_KEY=your_key
STABILITY_API_KEY=your_key
```

### 최종 배포 (Week 7)
```bash
IMAGE_PROVIDER=nanobanana
GEMINI_MODEL=gemini-1.5-flash
GEMINI_API_KEY=your_key
# STABILITY_API_KEY 불필요
```

## 예상 비용

```
Week 2-3 (Mock + Gemini 무료):
- 이미지: 0원
- 텍스트: 0원
- 소계: 0원

Week 4-6 (Stability + Gemini 무료):
- 이미지: 500장 x $0.004 = 2,600원
- 텍스트: 0원 (무료 tier 충분)
- 소계: 2,600원

Week 7 (나노바나나 + Gemini):
- 이미지: 200장 x $0.039 = 10,000원
- 텍스트: 5,000-10,000원
- 소계: 15,000-20,000원

총 예상 비용: 17,600-22,600원
예산 대비: 35-45% 사용
여유: 27,400-32,400원
```

## API 키 발급

### 필수 (지금 발급)
1. **Gemini API**
   - https://ai.google.dev/
   - Google AI Studio에서 발급
   - 무료 tier 사용

### 개발 중 필요 (Week 4 이후)
2. **Stability AI**
   - https://platform.stability.ai/
   - 신용카드 등록 필요
   - $10 크레딧으로 시작

### 선택 (필요 시)
3. **Voyage AI** - 임베딩용
4. **Supabase** - 데이터베이스
5. **Upstash** - Redis
6. **Qdrant Cloud** - Vector DB

## 코드 예시

### 이미지 생성 서비스 사용
```python
from app.services.image_service import image_service

# 환경 변수에 따라 자동으로 프로바이더 선택
image_url = await image_service.generate_image(
    prompt="Professional product photography of vitamin serum",
    category="화장품"
)
```

### 텍스트 생성 서비스 사용
```python
from app.services.gemini_service import gemini_service

# 마케팅 전략 제안
strategies = await gemini_service.generate_marketing_strategies(
    product_name="비타민 세럼",
    product_description="피부 미백 효과",
    category="화장품",
    target_age="20대",
    target_gender="여성",
    target_interests=["뷰티", "헬스케어"]
)
```

## 주의사항

1. **무료 tier 모니터링**
   - Gemini API 무료 제한 확인
   - 초과 시 유료로 자동 전환 (비용 발생)

2. **이미지 저장**
   - Stability/나노바나나 생성 이미지는 서버에 저장 필요
   - 스토리지 비용 고려 (S3, Cloudinary 등)

3. **캐싱 활용**
   - 동일한 요청은 Redis에 캐싱
   - API 비용 절감

4. **에러 처리**
   - API 실패 시 재시도 로직
   - Mock으로 폴백 옵션 고려

## 프로바이더 전환 가이드

### Mock → Stability
```bash
# .env 수정
IMAGE_PROVIDER=stability
STABILITY_API_KEY=sk-xxxxx

# 재시작
uvicorn app.main:app --reload
```

### Stability → 나노바나나
```bash
# .env 수정
IMAGE_PROVIDER=nanobanana

# STABILITY_API_KEY 삭제 가능
# 재시작
uvicorn app.main:app --reload
```

## 성능 비교

| 프로바이더 | 생성 시간 | 품질 | 비용 | 사용 시기 |
|-----------|---------|-----|------|----------|
| Mock | 즉시 | 실제 사진 | 무료 | 개발 초기 |
| Stability | 5-10초 | 좋음 | 5원/장 | 개발 중 |
| 나노바나나 | 10-15초 | 최고 | 50원/장 | 최종 배포 |

---

마지막 업데이트: 2025-10-27
