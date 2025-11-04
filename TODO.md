# ContentCraft AI - 개발 TODO

개발 및 구현 작업 체크리스트

## 프로젝트 정보

- 프로젝트명: ContentCraft AI
- 개발 기간: 7주
- 현재 주차: 4주차 (Vector DB + RAG 완료)
- 기술 스택: FastAPI, React, PostgreSQL, Redis, Qdrant, Gemini API, Replicate, Voyage AI
- 배포: Vercel (프론트엔드) + Render (백엔드)

---

## 1주차: 프로젝트 이해 및 환경 설정

### 기획 및 설계
- [x] 프로젝트 기획서 작성
- [x] 기능 정의서 작성
- [x] 시스템 아키텍처 설계
- [x] 데이터베이스 스키마 설계
- [x] API 명세서 작성

### 개발 환경 설정
- [x] 프로젝트 디렉토리 구조 생성
- [x] Git 저장소 초기화
- [x] .gitignore 설정
- [x] 백엔드 초기 설정 (FastAPI)
- [x] 프론트엔드 초기 설정 (React + Vite)
- [x] 환경 변수 파일 템플릿 생성
- [x] README.md 작성

### 다음 작업
- [x] Git 저장소 커밋 및 푸시
- [x] API 키 발급
  - [x] Gemini API
  - [x] Supabase
  - [x] Upstash Redis
  - [x] Qdrant Cloud
  - [x] Replicate (3주차에 필요)
  - [x] Voyage AI (4주차 완료)
- [x] 클라우드 서비스 가입
- [x] AI 모델 사용 전략 구현 (Mock, Replicate - SDXL, Ideogram v3 Turbo)
- [x] 백엔드 개발 환경 테스트
- [x] API 키 발급 가이드 문서 작성

### 1주차 완료
Week 1 Complete: 환경 설정 및 API 키 발급 완료

---

## 2주차: 데이터 수집 및 고객 세분화

### 데이터 수집
- [x] Kaggle API 설정
- [x] Kaggle 마케팅 데이터셋 다운로드
  - [x] "jackdaoud/marketing-data" (iFood 데이터)
  - [x] "vjchoudhary7/customer-segmentation-tutorial-in-python"
- [x] 데이터 수집 스크립트 작성 (`scripts/collect_data.py`)
- [x] 수집된 데이터 검증 및 정제 (`scripts/verify_data.py`)

### Gemini API 합성 데이터 생성
- [x] Gemini API 키 설정
- [x] Gemini API 연동 테스트
- [x] Gemini 2.5 Flash 모델 업데이트
- [x] 합성 데이터 생성 프롬프트 작성
- [x] 테스트 데이터 생성 성공 (5개 프로필)
- [x] 합성 데이터 생성 스크립트 작성 (`scripts/generate_synthetic_data.py`)
- [x] 전체 합성 데이터 생성 실행 (1,000개)
- [x] 데이터 품질 검증 (품질 점수: 4.7/5)

### 데이터 세분화 모듈
- [x] 세분화 기준 정의
  - [x] 나이대: 10대, 20대, 30대, 40대, 50대, 60대 이상
  - [x] 성별: 남성, 여성, 무관
  - [x] 관심사: 829개 고유 관심사 (자동 추출)
  - [x] 소득: 저소득, 중소득, 중상소득, 고소득
  - [x] 카테고리: 화장품, 식품, 패션, 전자제품, 서비스
- [x] 세분화 로직 구현 (`backend/app/services/segmentation_service.py`)
  - [x] 필터링 기능 (나이대, 성별, 소득, 관심사, 카테고리)
  - [x] 키워드 검색 기능
  - [x] 인사이트 자동 추출 (고충, 채널, 톤앤매너, 메시지 전략)
  - [x] 성별 필터링 시 "무관" 프로필 항상 포함
- [x] 세분화 데이터 저장 (data/processed/target_profiles.json)
- [x] 세분화 API 엔드포인트 구현 (`backend/app/api/segmentation.py`)
  - [x] POST /api/segmentation/filter (필터링)
  - [x] POST /api/segmentation/search (키워드 검색)
  - [x] GET /api/segmentation/summary (전체 요약)
  - [x] GET /api/segmentation/insights (인사이트만 조회)
- [x] 세분화 결과 시각화 스크립트 (visualize_segmentation.py)
  - [x] 나이대 분포 차트 (data/processed/age_distribution.png)
  - [x] 성별 분포 파이 차트 (data/processed/gender_distribution.png)
  - [x] 소득 분포 차트 (data/processed/income_distribution.png)
  - [x] 카테고리 분포 차트 (data/processed/category_distribution.png)
  - [x] 상위 관심사 차트 (data/processed/top_interests.png)
  - [x] 상위 고충 차트 (data/processed/top_pain_points.png)
  - [x] 나이대×성별 히트맵 (data/processed/age_gender_heatmap.png)
- [x] 실제 사용자 시나리오 10개 테스트 완료 (test_real_scenarios.py)

### 데이터베이스 설정
- [x] PostgreSQL (Supabase) 데이터베이스 생성
- [x] Alembic 마이그레이션 설정
- [x] 데이터베이스 모델 정의
  - [x] User 모델 (`backend/app/models/user.py`)
  - [x] Project 모델 (`backend/app/models/project.py`)
  - [x] Target 모델 (`backend/app/models/target.py`)
  - [x] Content 모델 (`backend/app/models/content.py`)
  - [x] Segment 모델 (`backend/app/models/segment.py`) - 필터 결과 캐싱용
- [x] 초기 마이그레이션 생성 및 실행
- [x] 타겟 프로필 데이터베이스 임포트 (990개, 10대 성별 분포 개선)

---

## 3주차: 맞춤형 콘텐츠 생성

### Gemini API 통합
- [x] Gemini 서비스 모듈 구현 (`backend/app/services/gemini_service.py`)
- [x] API 호출 에러 핸들링 (재시도 로직, 지수 백오프)
- [x] JSON 파싱 로직 완성
- [ ] 응답 캐싱 (Redis)
- [ ] Rate limiting 구현

### 마케팅 전략 제안
- [x] 전략 제안 프롬프트 엔지니어링
- [x] 제품/타겟 정보 기반 전략 생성 로직
- [x] 3가지 전략 생성 (감성적, 이성적, 사회적)
- [x] 전략 API 엔드포인트 (`POST /api/content/strategy`)
- [x] 전략 응답 스키마 정의 (`backend/app/schemas/content.py`)

### 텍스트 카피 생성
- [x] 카피 생성 프롬프트 엔지니어링
  - [x] 프로페셔널 톤 (40-50자)
  - [x] 캐주얼 톤 (30-40자)
  - [x] 임팩트 톤 (15-25자)
- [x] 카피 생성 로직 구현
- [x] 해시태그 자동 생성
- [x] 카피 길이 제한 및 검증
- [x] 카피 API 엔드포인트 (`POST /api/content/copy`)
- [x] 이미지 프롬프트 변환 API (`POST /api/content/image-prompt`)

### Replicate 이미지 생성
- [x] Replicate 서비스 모듈 (`backend/app/services/replicate_service.py`)
- [x] 카피 → 이미지 프롬프트 변환 로직 (Gemini API)
- [x] Replicate API 연동 (SDXL + Ideogram v3 Turbo)
- [x] 환경별 모델 분기 로직 (IMAGE_MODE: development/production)
- [x] 이미지 생성 API 엔드포인트 (`POST /api/content/image`)
- [x] 에러 핸들링 및 재시도 로직 (지수 백오프)
- [x] 모델별 파라미터 자동 변환
- [x] Replicate API 토큰 인증 (Client 명시적 전달)
- [x] 이미지 스토리지 설정 (개발: 로컬)
  - [x] ImageStorageService 구현 (`backend/app/services/image_storage.py`)
  - [x] 이미지 다운로드 및 저장 (`aiohttp`, `aiofiles`)
  - [x] FastAPI static files 마운트 (`/static/images/`)
- [x] 이미지 최적화 (크기, 포맷)
  - [x] PIL/Pillow로 이미지 최적화
  - [x] RGBA → RGB 변환
  - [x] 크기 조정 (최대 2048x2048, 비율 유지)
  - [x] PNG 무손실 압징
- [x] 실제 이미지 생성 + 저장 + 서빙 테스트 완료

### Nano Banana (Gemini 2.5 Flash Image) 연동
- [x] google-genai 패키지 설치
- [x] Nano Banana 서비스 모듈 구현 (`backend/app/services/nanobanana_service.py`)
- [x] IMAGE_PROVIDER 환경변수 시스템 구축
  - [x] .env에서 replicate/nanobanana 전환 가능
  - [x] content_generation.py에서 자동 분기
- [x] 코드 일관성 개선 (os.getenv → settings 통일)
- [ ] Gemini API Tier 1 결제 버그 해결 대기 (12시간 후 재시도 예정)
- [ ] Nano Banana 실제 이미지 생성 테스트

### 콘텐츠 생성 통합
- [x] 전체 생성 파이프라인 구현
  - [x] 입력 → 전략 → 카피 → 이미지 프롬프트 → 이미지
- [x] 비동기 처리 구현
- [x] 에러 처리 및 재시도 로직
- [x] 진행 상황 추적 (로깅)
- [x] Content 모델 및 API (`backend/app/models/content.py`)
- [x] 생성 결과 데이터베이스 저장
- [x] 통합 콘텐츠 생성 API (`POST /api/content/generate`)
- [x] 통합 테스트 완료 (소요 시간: 37초)

### 프론트엔드 기본 UI
- [x] TypeScript 마이그레이션 완료
- [x] API 클라이언트 설정 (`frontend/src/utils/api.ts`)
- [x] 입력 폼 컴포넌트 (`frontend/src/components/InputForm.tsx`)
  - [x] 제품 정보 입력 (이름, 설명, 카테고리)
  - [x] 타겟 정보 입력 (나이대, 성별, 관심사)
  - [x] 카피 톤 선택
  - [x] 한글 입력 IME 버그 수정
- [x] 결과 표시 컴포넌트 (`frontend/src/components/ResultDisplay.tsx`)
  - [x] 전략 3가지 표시 및 선택
  - [x] 카피 및 해시태그 표시
  - [x] 이미지 표시
  - [x] 다운로드 및 복사 기능
- [x] 로딩 상태 표시 (`frontend/src/components/LoadingSpinner.tsx`)
- [x] 에러 처리 UI (`frontend/src/components/ErrorMessage.tsx`)
- [x] 메인 생성 페이지 (`frontend/src/pages/GeneratePage.tsx`)
- [x] 프론트엔드 테스트 완료 (http://localhost:5173)

---

## 4주차: 캠페인 성과 분석

### 가상 사용자 반응 데이터
- [x] 페르소나 생성 프롬프트 작성
- [x] Gemini API로 다양한 페르소나 생성
- [x] 페르소나별 콘텐츠 반응 시뮬레이션
- [x] 성과 지표 데이터 생성
  - [x] CTR (클릭률)
  - [x] Engagement (참여도)
  - [x] Conversion (전환율)
  - [x] Brand Recall (브랜드 기억도)

### 성과 분석 로직
- [x] 성과 분석 서비스 모듈 (`backend/app/services/performance_service.py`)
- [x] Performance 모델 구현 (`backend/app/models/performance.py`)
  - [x] AI 시뮬레이션 데이터 저장
  - [x] 실제 데이터 추적 지원 (data_source 필드)
  - [x] 페르소나 데이터 및 신뢰도 점수
- [x] 통계 집계 로직
- [x] 타겟별 성과 비교 (target_breakdown)
- [x] AI 기반 인사이트 생성 (Gemini 2.0 Flash)
- [x] 성과 예측 API 구현
  - [x] `POST /api/performance/predict/{content_id}` - 성과 예측
  - [x] `GET /api/performance/{content_id}` - 성과 조회
  - [x] `GET /api/performance/summary/{content_id}` - 요약 조회

### Vector DB 통합
- [x] Qdrant Cloud 계정 생성 및 API 키 발급
- [x] Qdrant 연결 설정 및 테스트
- [x] Vector 서비스 모듈 (`backend/app/services/vector_service.py`)
- [x] Voyage AI 임베딩 연동 (voyage-3-large, 1024차원)
- [x] 콘텐츠 임베딩 생성 및 저장
- [x] 유사 콘텐츠 검색 기능
- [x] 과거 성과 데이터 참조 로직 (RAG 구현)
- [x] 콘텐츠 생성 API에 Vector DB 저장 통합
- [x] Performance 예측에 RAG 적용
- [x] RAG 통합 테스트 완료

### 대시보드 (프론트엔드)
- [ ] 대시보드 페이지 구현 (`frontend/src/pages/Dashboard.tsx`)
- [ ] 주요 지표 카드 컴포넌트
- [ ] 타겟별 비교 차트 (Chart.js 또는 Recharts)
- [ ] 전략별 비교 차트
- [ ] AI 인사이트 텍스트 표시
- [ ] 성과 예측 요청 및 표시 로직

---

## 5주차: 기능 통합 및 서비스화

### 사용자 인증 (JWT) - 우선 구현
- [ ] User 모델 확인 및 수정 (필요시)
- [ ] 회원가입 API (`POST /api/auth/register`)
  - [ ] 이메일 중복 체크
  - [ ] 비밀번호 해싱 (bcrypt)
  - [ ] 사용자 생성
- [ ] 로그인 API (`POST /api/auth/login`)
  - [ ] 이메일/비밀번호 검증
  - [ ] JWT 토큰 발급 (access token)
  - [ ] Refresh token (선택)
- [ ] 인증 미들웨어
  - [ ] JWT 토큰 검증
  - [ ] 현재 사용자 정보 추출
  - [ ] Protected routes
- [ ] 프론트엔드 인증
  - [ ] 로그인 페이지 (`frontend/src/pages/Login.tsx`)
  - [ ] 회원가입 페이지 (`frontend/src/pages/Register.tsx`)
  - [ ] JWT 토큰 저장 (localStorage)
  - [ ] Axios 인터셉터 (토큰 자동 추가)
  - [ ] 로그아웃 기능
  - [ ] Protected routes (React Router)

### React 프론트엔드 본격 개발
- [ ] 라우팅 설정 (React Router)
- [ ] 전역 상태 관리 (Zustand)
  - [ ] 프로젝트 스토어
  - [ ] 콘텐츠 스토어
  - [ ] 사용자 스토어
- [ ] 메인 대시보드 페이지 (`frontend/src/pages/Dashboard.tsx`)
- [ ] 프로젝트 목록 페이지 (`frontend/src/pages/Projects.tsx`)
- [ ] 프로젝트 생성/수정 페이지 (`frontend/src/pages/ProjectForm.tsx`)
- [ ] 콘텐츠 생성 페이지 (`frontend/src/pages/Generate.tsx`)
- [ ] 히스토리 페이지 (`frontend/src/pages/History.tsx`)
- [ ] 상세 모달 컴포넌트 (`frontend/src/components/DetailModal.tsx`)

### 타겟 세분화 UI
- [ ] 타겟 필터링 페이지 (`frontend/src/pages/TargetFilter.tsx`)
  - [ ] 필터 옵션 UI (나이대, 성별, 소득, 관심사, 카테고리)
  - [ ] 필터 결과 표시 (매칭된 타겟 수, 프로필 목록)
  - [ ] 인사이트 자동 표시 (고충, 선호 채널, 톤앤매너, 메시지 전략)
- [ ] 타겟 검색 컴포넌트 (`frontend/src/components/TargetSearch.tsx`)
  - [ ] 키워드 검색
  - [ ] 검색 결과 표시
- [ ] 타겟 요약 대시보드 컴포넌트 (`frontend/src/components/TargetSummary.tsx`)
  - [ ] 전체 타겟 분포 차트
  - [ ] 주요 통계 카드
- [ ] 세분화 → 콘텐츠 생성 연동
  - [ ] 필터링된 타겟 정보를 콘텐츠 생성 폼에 자동 입력

### 백엔드 API 완성
- [ ] 프로젝트 CRUD API
  - [ ] `POST /api/projects` - 생성
  - [ ] `GET /api/projects` - 목록
  - [ ] `GET /api/projects/{id}` - 상세
  - [ ] `PUT /api/projects/{id}` - 수정
  - [ ] `DELETE /api/projects/{id}` - 삭제
- [ ] 콘텐츠 API
  - [ ] `GET /api/contents` - 목록
  - [ ] `GET /api/contents/{id}` - 상세
  - [ ] `DELETE /api/contents/{id}` - 삭제
- [ ] 타겟 API
  - [ ] `GET /api/targets` - 세그먼트 목록
  - [ ] `GET /api/targets/{id}` - 세그먼트 상세
- [ ] API 문서 자동 생성 (FastAPI Swagger)

### Redis 캐싱
- [ ] Redis 연결 설정
- [ ] 캐싱 유틸리티 (`backend/app/utils/cache.py`)
- [ ] API 응답 캐싱
- [ ] 세그먼트 데이터 캐싱
- [ ] 캐시 무효화 로직

### 통합 테스트
- [ ] 엔드투엔드 테스트 시나리오 작성
- [ ] 프로젝트 생성 → 콘텐츠 생성 → 결과 확인 플로우 테스트
- [ ] API 통합 테스트
- [ ] 프론트엔드 통합 테스트
- [ ] 버그 수정

---

## 6주차: 품질 개선 및 UX 강화

### 프롬프트 최적화
- [ ] 다양한 프롬프트 버전 실험
- [ ] A/B 테스트 수행
- [ ] Few-shot learning 프롬프트 적용
- [ ] 프롬프트 템플릿 관리 시스템
- [ ] 최적 프롬프트 선정 및 적용

### UI/UX 개선
- [ ] 사용자 피드백 수집
- [ ] 로딩 상태 개선 (스켈레톤 UI)
- [ ] 에러 메시지 개선
- [ ] 토스트 알림 추가
- [ ] 반응형 디자인 적용
  - [ ] 모바일 최적화
  - [ ] 태블릿 최적화
- [ ] 접근성 개선 (ARIA 속성)
- [ ] 다크 모드 (선택사항)

### 성능 최적화
- [ ] API 호출 최적화
- [ ] 이미지 레이지 로딩
- [ ] 컴포넌트 메모이제이션
- [ ] 번들 크기 최적화
- [ ] 데이터베이스 쿼리 최적화
- [ ] 인덱스 추가
- [ ] N+1 쿼리 해결

### 다양한 옵션 추가
- [ ] 더 많은 카피 톤 옵션
- [ ] 이미지 스타일 선택 옵션
  - [ ] 제품 사진
  - [ ] 라이프스타일
  - [ ] 그래픽 디자인
  - [ ] 일러스트
- [ ] 카피 길이 조절 옵션
- [ ] 해시태그 개수 설정

---

## 7주차: 기능 고도화 및 배포

### 부가 기능 개발 (최소 1개 선택)

#### 옵션 1: 다국어 지원
- [ ] 번역 서비스 모듈 구현
- [ ] Gemini API 번역 및 현지화
- [ ] 지원 언어: 영어, 일본어, 중국어
- [ ] 다국어 UI 구현
- [ ] 번역 API 엔드포인트

#### 옵션 2: 히스토리 고급 기능
- [ ] 날짜별 그룹핑
- [ ] 고급 검색 및 필터
- [ ] 정렬 옵션
- [ ] 즐겨찾기 기능
- [ ] 재사용 기능
- [ ] 일괄 삭제

#### 옵션 3: 템플릿 추천 (Vector DB)
- [ ] 유사도 검색 구현
- [ ] 추천 로직 구현
- [ ] 추천 UI 컴포넌트
- [ ] 추천 API 엔드포인트
- [ ] "이 스타일로 생성" 기능

#### 옵션 4: 대화형 이미지 편집 ⭐ 추천 (Ideogram v2 Inpainting)
- [ ] 사용자 이미지 업로드 기능
  - [ ] 이미지 업로드 API (`POST /api/content/upload-image`)
  - [ ] multipart/form-data 파일 처리
  - [ ] 업로드 이미지 저장 (로컬/S3)
  - [ ] 이미지 파일 검증 (형식, 크기, 해상도)
  - [ ] 업로드 UI 컴포넌트 (드래그 앤 드롭)
- [ ] 이미지 편집 서비스 모듈 (`backend/app/services/image_edit_service.py`)
- [ ] Gemini로 자연어 명령 분석 (편집 의도 파악)
- [ ] 마스크 생성 로직 (background/product/full)
- [ ] Replicate Ideogram v2 Inpainting 연동
- [ ] 편집 API (`POST /api/content/edit-image`)
- [ ] 멀티턴 대화 구현 (편집 히스토리 기반 연속 편집)
- [ ] 편집 히스토리 관리 (DB 저장)
- [ ] 빠른 명령 버튼 4개 (배경 밝게, 제품 크게, 색감 따뜻하게, 조명 개선)
- [ ] 편집 UI 컴포넌트 (편집 전/후 비교, 대화창)

#### 옵션 5: 브랜드 킷
- [ ] 브랜드 정보 모델
- [ ] 브랜드 설정 UI
- [ ] 브랜드 컬러 자동 적용
- [ ] 로고 오버레이 기능
- [ ] 금지 단어 필터링
- [ ] 브랜드 톤 적용

#### 옵션 6: 실제 성과 데이터 수집 (URL 추적)
- [ ] 제품 URL 입력 필드 추가
  - [ ] Content 모델에 product_url 필드 추가
  - [ ] 입력 폼(InputForm.tsx)에 제품 URL 필드 추가
  - [ ] 선택적 입력 (URL 없이도 콘텐츠 생성 가능)
- [ ] 추적 URL 생성 시스템
  - [ ] 단축 URL 생성 로직 (예: `/track/{content_id}`)
  - [ ] URL 리다이렉트 엔드포인트 구현
  - [ ] 클릭 카운트 로직
- [ ] Performance 테이블 실제 데이터 업데이트
  - [ ] 클릭 추적 및 CTR 계산
  - [ ] 조회수 카운트
  - [ ] data_source="real_data" 로 구분
- [ ] UI 개선
  - [ ] 결과 화면에 추적 URL 표시
  - [ ] "SNS에 사용하세요" 가이드 추가
  - [ ] 추적 링크 복사 버튼
- [ ] 대시보드에서 실제 vs AI 예측 비교
  - [ ] "AI 예측: 8.2%, 실제: 6.8%" 표시
  - [ ] AI 정확도 계산
- [ ] (선택) 광고 플랫폼 연동
  - [ ] Facebook Webhook 콜백 엔드포인트
  - [ ] Google Ads API 연동
  - [ ] 실시간 성과 데이터 수신

### 클라우드 배포

#### 프로덕션 이미지 스토리지 (S3/CDN)
- [ ] AWS S3 또는 Cloudflare R2 계정 설정
- [ ] 버킷 생성 및 권한 설정
- [ ] 환경별 스토리지 분기 로직 구현
  - [ ] 개발 환경: 로컬 스토리지 유지
  - [ ] 프로덕션 환경: S3 업로드로 전환
- [ ] S3 업로드 서비스 구현 (boto3 또는 SDK)
- [ ] CDN 설정 (CloudFront 또는 Cloudflare)
- [ ] CDN URL 반환 로직
- [ ] 환경 변수 설정 (S3_BUCKET, S3_REGION, S3_ACCESS_KEY 등)
- [ ] ImageStorageService 수정 (환경별 분기)
- [ ] 프로덕션 배포 시 테스트

#### Vercel (프론트엔드)
- [ ] Vercel 프로젝트 생성
- [ ] GitHub 저장소 연동
- [ ] 빌드 설정
- [ ] 환경 변수 설정
- [ ] 도메인 연결 (선택)
- [ ] 배포 확인

#### Render (백엔드)
- [ ] Render 계정 생성
- [ ] Web Service 생성
- [ ] GitHub 저장소 연동
- [ ] 빌드 설정 (Python 3.11+)
- [ ] Start Command 설정 (`uvicorn app.main:app --host 0.0.0.0 --port $PORT`)
- [ ] 환경 변수 설정
  - [ ] DATABASE_URL (Supabase)
  - [ ] REDIS_URL (Upstash)
  - [ ] QDRANT_URL, QDRANT_API_KEY
  - [ ] GEMINI_API_KEY
  - [ ] REPLICATE_API_TOKEN
  - [ ] 기타 설정 변수
- [ ] 데이터베이스 연결 확인
- [ ] 헬스체크 엔드포인트 설정 (`/health`)
- [ ] 배포 확인 및 테스트

#### 데이터베이스 설정
- [ ] Supabase PostgreSQL 프로덕션 설정
- [ ] 마이그레이션 실행
- [ ] 초기 데이터 임포트
- [ ] Qdrant Cloud 프로덕션 설정
- [ ] Upstash Redis 프로덕션 설정

### 최종 테스트
- [ ] 전체 시나리오 테스트
- [ ] 프로덕션 환경 테스트
- [ ] 성능 테스트 (부하 테스트)
- [ ] 보안 점검
  - [ ] API 키 하드코딩 제거 확인
  - [ ] CORS 설정 확인
  - [ ] SQL 인젝션 방지 확인
- [ ] 크로스 브라우저 테스트
- [ ] 모바일 테스트

### 문서화
- [ ] README.md 업데이트
- [ ] API 문서 정리
- [ ] 사용자 가이드 작성
- [ ] 설치 가이드 업데이트
- [ ] 아키텍처 다이어그램
- [ ] 발표 자료 준비
  - [ ] 프로젝트 개요
  - [ ] 주요 기능 시연
  - [ ] 기술 스택 설명
  - [ ] 결과 및 성과

---

## 추가 개선 사항 (시간 여유 시)

### 기능 개선
- [ ] 일괄 생성 기능 (여러 타겟 동시 생성)
- [ ] 콘텐츠 비교 기능
- [ ] 콘텐츠 내보내기 (PDF, ZIP)
- [ ] 협업 기능 (팀원 초대)
- [ ] 알림 시스템

### 개발 환경
- [ ] Docker Compose 설정
- [ ] CI/CD 파이프라인 (GitHub Actions)
- [ ] 자동화된 테스트 실행
- [ ] 코드 품질 도구 (Linter, Formatter)
- [ ] Pre-commit hooks

### 모니터링
- [ ] 로깅 시스템 구축
- [ ] 에러 트래킹 (Sentry)
- [ ] 성능 모니터링
- [ ] API 사용량 추적

---

## 주간 목표 체크

### 2주차 목표 (현재)
- [ ] 데이터 수집 완료 (1,000개 이상)
- [ ] 세분화 모듈 구현 완료
- [ ] 데이터베이스 설정 완료
- [ ] 세분화 API 작동 확인

### 3주차 목표 ✅ 완료
- [x] Gemini API 연동 완료
- [x] Replicate API 연동 완료 (SDXL, Ideogram v3 Turbo)
- [x] 콘텐츠 생성 API 작동 확인
- [x] 기본 UI에서 전체 플로우 테스트 성공
- [x] TypeScript 마이그레이션 완료

### 4주차 목표 ✅ 완료
- [x] 성과 분석 시스템 작동
- [x] Vector DB 통합 완료 (Qdrant + Voyage AI)
- [x] RAG 구현 및 테스트 완료
- [ ] 대시보드 프론트엔드 (남은 작업)

### 5주차 목표
- [ ] 모든 API 엔드포인트 완성
- [ ] 프론트엔드 주요 페이지 완성
- [ ] 전체 플로우 통합 테스트 통과

### 6주차 목표
- [ ] 사용자 경험 개선 완료
- [ ] 성능 최적화 완료
- [ ] 모바일 반응형 완성

### 7주차 목표
- [ ] 부가 기능 1개 이상 구현
- [ ] 클라우드 배포 완료
- [ ] 발표 준비 완료

---

## 참고 사항

### API 키 발급 필요
- [x] Google AI Studio (Gemini API)
- [x] Replicate (3주차 완료)
- [x] Voyage AI (4주차 완료)
- [x] Supabase
- [x] Upstash Redis
- [x] Qdrant Cloud

### 예상 비용 (50,000원 예산)
- Gemini API: 약 10,000원
- Replicate API:
  - 개발 단계 (SDXL): 4,800원
  - 최종 발표 (Ideogram v3 Turbo): 2,650원
  - 배포 후 (SDXL): 7,200원
- Ideogram v2 편집 (부가 기능): 8,000원
- 인프라 (Vercel, Render, Supabase 무료): 0원
- **총 예산: 24,650원 (예비비: 25,350원)**
- **예산 절감률: 50.7%**

### 중요 링크
- Gemini API: https://ai.google.dev/gemini-api/docs
- Replicate: https://replicate.com/docs
- SDXL on Replicate: https://replicate.com/stability-ai/sdxl
- Ideogram v3 Turbo: https://replicate.com/ideogram-ai/ideogram-v3-turbo
- Ideogram v2 (편집): https://replicate.com/ideogram-ai/ideogram-v2
- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/
- Qdrant: https://qdrant.tech/documentation/

---

## 마일스톤

- [x] Week 1 Complete: 환경 설정 완료
- [x] Week 2 Complete: 데이터 세분화 완료
- [x] Week 3 Complete: 콘텐츠 생성 기능 완료 ✅
  - [x] 백엔드 API (Gemini + Replicate 통합)
  - [x] 프론트엔드 UI (TypeScript + React)
  - [x] 전체 플로우 테스트 완료
- [x] Week 4 Complete: 성과 분석 완료 ✅
  - [x] 성과 예측 시스템 (AI 시뮬레이션)
  - [x] Vector DB 통합 (Qdrant + Voyage AI)
  - [x] RAG 구현 (유사 콘텐츠 기반 성과 예측)
  - [ ] 대시보드 프론트엔드 (남은 작업)
- [ ] Week 5 Complete: 서비스 통합 완료
- [ ] Week 6 Complete: 품질 개선 완료
- [ ] Week 7 Complete: 배포 및 발표 준비 완료 (Vercel + Render)

---

현재 진행 상황: 4주차 완료 ✅ → 5주차 시작 가능 (서비스 통합 및 프론트엔드 본격 개발)
