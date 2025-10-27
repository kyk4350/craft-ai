# ContentCraft AI - 개발 TODO

개발 및 구현 작업 체크리스트

## 프로젝트 정보

- 프로젝트명: ContentCraft AI
- 개발 기간: 7주
- 현재 주차: 2주차
- 기술 스택: FastAPI, React, PostgreSQL, Redis, Qdrant, Gemini API, 나노바나나

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
  - [x] Stability AI
  - [x] Supabase
  - [x] Upstash Redis
  - [x] Qdrant Cloud
- [x] 클라우드 서비스 가입
- [x] AI 모델 사용 전략 구현 (Mock, Stability, 나노바나나)
- [x] 백엔드 개발 환경 테스트
- [x] API 키 발급 가이드 문서 작성

### 1주차 완료
Week 1 Complete: 환경 설정 및 API 키 발급 완료

---

## 2주차: 데이터 수집 및 고객 세분화

### 데이터 수집
- [ ] Kaggle API 설정
- [ ] Kaggle 마케팅 데이터셋 다운로드
  - [ ] "Social Media Marketing Dataset"
  - [ ] "Customer Segmentation Dataset"
- [ ] 공공데이터포털 API 연동
- [ ] 데이터 수집 스크립트 작성 (`scripts/collect_data.py`)
- [ ] 수집된 데이터 검증 및 정제

### Gemini API 합성 데이터 생성
- [ ] Gemini API 키 설정
- [ ] Gemini API 연동 테스트
- [ ] 합성 데이터 생성 프롬프트 작성
- [ ] 다양한 세그먼트별 합성 데이터 생성 (최소 1,000개)
- [ ] 데이터 품질 검증

### 데이터 세분화 모듈
- [ ] 세분화 기준 정의
  - [ ] 나이대: 10대, 20대, 30대, 40대+
  - [ ] 성별: 남성, 여성, 전체
  - [ ] 관심사: 패션, 뷰티, 음식, 여행, 테크, 반려동물, 게임, 독서, 영화, 육아
  - [ ] 플랫폼: Instagram, Facebook, 카카오톡, 네이버
- [ ] 세분화 로직 구현 (`backend/app/services/segmentation_service.py`)
- [ ] 세분화 데이터 저장 (JSON/CSV)
- [ ] 세분화 API 엔드포인트 구현 (`backend/app/api/segmentation.py`)
- [ ] 세분화 결과 시각화 스크립트

### 데이터베이스 설정
- [ ] PostgreSQL (Supabase) 데이터베이스 생성
- [ ] Alembic 마이그레이션 설정
- [ ] 데이터베이스 모델 정의
  - [ ] User 모델 (`backend/app/models/user.py`)
  - [ ] Project 모델 (`backend/app/models/project.py`)
  - [ ] Target 모델 (`backend/app/models/target.py`)
  - [ ] Segment 모델 (`backend/app/models/segment.py`)
- [ ] 초기 마이그레이션 생성 및 실행
- [ ] 세분화 데이터 데이터베이스 임포트

---

## 3주차: 맞춤형 콘텐츠 생성

### Gemini API 통합
- [ ] Gemini 서비스 모듈 구현 (`backend/app/services/gemini_service.py`)
- [ ] API 호출 에러 핸들링
- [ ] 응답 캐싱 (Redis)
- [ ] Rate limiting 구현

### 마케팅 전략 제안
- [ ] 전략 제안 프롬프트 엔지니어링
- [ ] 제품/타겟 정보 기반 전략 생성 로직
- [ ] 3가지 전략 생성 (감성적, 기능적, 사회적)
- [ ] 전략 API 엔드포인트 (`POST /api/generate/strategy`)
- [ ] 전략 응답 스키마 정의 (`backend/app/schemas/strategy.py`)

### 텍스트 카피 생성
- [ ] 카피 생성 프롬프트 엔지니어링
  - [ ] 프로페셔널 톤
  - [ ] 캐주얼 톤
  - [ ] 임팩트 톤
- [ ] 카피 생성 로직 구현
- [ ] 해시태그 자동 생성
- [ ] 카피 길이 제한 및 검증
- [ ] 카피 API 엔드포인트

### 나노바나나 이미지 생성
- [ ] 나노바나나 서비스 모듈 (`backend/app/services/nanobanana_service.py`)
- [ ] 카피 → 이미지 프롬프트 변환 로직
- [ ] Gemini 2.5 Flash Image API 연동
- [ ] 이미지 생성 및 저장
- [ ] 이미지 스토리지 설정 (로컬 또는 클라우드)
- [ ] 이미지 최적화 (크기, 포맷)

### 콘텐츠 생성 통합
- [ ] 전체 생성 파이프라인 구현
  - [ ] 입력 → 전략 → 카피 → 이미지 프롬프트 → 이미지
- [ ] 비동기 처리 구현
- [ ] 에러 처리 및 재시도 로직
- [ ] 진행 상황 추적
- [ ] Content 모델 및 API (`backend/app/models/content.py`)
- [ ] 생성 결과 데이터베이스 저장

### 프론트엔드 기본 UI
- [ ] API 클라이언트 설정 (`frontend/src/utils/api.js`)
- [ ] 입력 폼 컴포넌트 (`frontend/src/components/InputForm.jsx`)
- [ ] 전략 선택 컴포넌트 (`frontend/src/components/StrategySelector.jsx`)
- [ ] 결과 그리드 컴포넌트 (`frontend/src/components/ResultGrid.jsx`)
- [ ] 로딩 상태 표시
- [ ] 에러 처리 UI

---

## 4주차: 캠페인 성과 분석

### 가상 사용자 반응 데이터
- [ ] 페르소나 생성 프롬프트 작성
- [ ] Gemini API로 다양한 페르소나 생성
- [ ] 페르소나별 콘텐츠 반응 시뮬레이션
- [ ] 성과 지표 데이터 생성
  - [ ] CTR (클릭률)
  - [ ] Engagement (참여도)
  - [ ] Conversion (전환율)
  - [ ] Brand Recall (브랜드 기억도)

### 성과 분석 로직
- [ ] 성과 분석 서비스 모듈 (`backend/app/services/analysis_service.py`)
- [ ] 통계 집계 로직
- [ ] 타겟별 성과 비교
- [ ] 전략별 성과 비교
- [ ] 시계열 분석
- [ ] AI 기반 인사이트 생성

### Vector DB 통합
- [ ] Qdrant Cloud 설정
- [ ] Vector 서비스 모듈 (`backend/app/services/vector_service.py`)
- [ ] Voyage AI 임베딩 연동
- [ ] 콘텐츠 임베딩 생성 및 저장
- [ ] 유사 콘텐츠 검색 기능
- [ ] 과거 성과 데이터 참조 로직

### Streamlit 대시보드
- [ ] Streamlit 설치 및 설정
- [ ] 대시보드 레이아웃 구성
- [ ] 주요 지표 카드
- [ ] 시계열 그래프 (Plotly)
- [ ] 타겟별 비교 차트
- [ ] 전략별 비교 차트
- [ ] AI 인사이트 텍스트
- [ ] 대시보드 실행 스크립트

### 성과 예측 API
- [ ] 예측 로직 구현
- [ ] 예측 API 엔드포인트 (`POST /api/analysis/performance`)
- [ ] 대시보드 데이터 API (`GET /api/analysis/dashboard`)
- [ ] 예측 결과 스키마

---

## 5주차: 기능 통합 및 서비스화

### React 프론트엔드 본격 개발
- [ ] 라우팅 설정 (React Router)
- [ ] 전역 상태 관리 (Zustand)
  - [ ] 프로젝트 스토어
  - [ ] 콘텐츠 스토어
  - [ ] 사용자 스토어
- [ ] 메인 대시보드 페이지 (`frontend/src/pages/Dashboard.jsx`)
- [ ] 프로젝트 목록 페이지 (`frontend/src/pages/Projects.jsx`)
- [ ] 프로젝트 생성/수정 페이지 (`frontend/src/pages/ProjectForm.jsx`)
- [ ] 콘텐츠 생성 페이지 (`frontend/src/pages/Generate.jsx`)
- [ ] 히스토리 페이지 (`frontend/src/pages/History.jsx`)
- [ ] 상세 모달 컴포넌트 (`frontend/src/components/DetailModal.jsx`)

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

#### 옵션 4: 대화형 이미지 편집 (나노바나나)
- [ ] 이미지 편집 서비스 모듈
- [ ] 자연어 편집 명령 처리
- [ ] 멀티턴 대화 구현
- [ ] 편집 히스토리 관리
- [ ] 빠른 명령 버튼
- [ ] 편집 UI 컴포넌트

#### 옵션 5: 브랜드 킷
- [ ] 브랜드 정보 모델
- [ ] 브랜드 설정 UI
- [ ] 브랜드 컬러 자동 적용
- [ ] 로고 오버레이 기능
- [ ] 금지 단어 필터링
- [ ] 브랜드 톤 적용

### 클라우드 배포

#### Vercel (프론트엔드)
- [ ] Vercel 프로젝트 생성
- [ ] GitHub 저장소 연동
- [ ] 빌드 설정
- [ ] 환경 변수 설정
- [ ] 도메인 연결 (선택)
- [ ] 배포 확인

#### Railway (백엔드)
- [ ] Railway 프로젝트 생성
- [ ] Dockerfile 작성
- [ ] GitHub 저장소 연동
- [ ] 환경 변수 설정
- [ ] 데이터베이스 연결 확인
- [ ] 헬스체크 설정
- [ ] 배포 확인

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
- [ ] 사용자 인증 (JWT)

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

### 3주차 목표
- [ ] Gemini API 연동 완료
- [ ] 나노바나나 연동 완료
- [ ] 콘텐츠 생성 API 작동 확인
- [ ] 기본 UI에서 전체 플로우 테스트 성공

### 4주차 목표
- [ ] 성과 분석 시스템 작동
- [ ] Streamlit 대시보드 완성
- [ ] Vector DB 통합 완료

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
- [ ] Google AI Studio (Gemini API)
- [ ] Voyage AI
- [ ] Supabase
- [ ] Upstash Redis
- [ ] Qdrant Cloud

### 예상 비용
- Gemini API: 약 5만원
- 나노바나나: 약 2.5-5만원
- Railway: 약 1.5만원
- 총: 약 9-12만원

### 중요 링크
- Gemini API: https://ai.google.dev/gemini-api/docs
- 나노바나나: https://ai.google.dev/gemini-api/docs/image-generation
- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/
- Qdrant: https://qdrant.tech/documentation/

---

## 마일스톤

- [x] Week 1 Complete: 환경 설정 완료
- [ ] Week 2 Complete: 데이터 세분화 완료
- [ ] Week 3 Complete: 콘텐츠 생성 기능 완료
- [ ] Week 4 Complete: 성과 분석 완료
- [ ] Week 5 Complete: 서비스 통합 완료
- [ ] Week 6 Complete: 품질 개선 완료
- [ ] Week 7 Complete: 배포 및 발표 준비 완료

---

현재 진행 상황: 1주차 완료, 2주차 시작 준비
