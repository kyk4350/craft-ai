# ContentCraft AI

AI 기반 마케팅 콘텐츠 자동 생성 플랫폼

## 프로젝트 개요

ContentCraft AI는 Gemini API와 나노바나나(Gemini 2.5 Flash Image)를 활용하여 타겟 맞춤형 마케팅 콘텐츠(텍스트 카피 + 이미지)를 자동으로 생성하는 플랫폼입니다.

## 주요 기능

- [ ] 고객 데이터 수집 및 세분화
- [ ] AI 기반 마케팅 전략 제안
- [ ] 텍스트 카피 자동 생성 (3가지 톤)
- [ ] 이미지 자동 생성 (나노바나나)
- [ ] 성과 예측 및 분석
- [ ] 대시보드 및 히스토리 관리

## 기술 스택

### Backend
- FastAPI (Python 3.11+)
- PostgreSQL (Supabase)
- Redis (Upstash)
- Qdrant (Vector DB)
- Google Gemini API
- Voyage AI (Embeddings)

### Frontend
- React 18
- Vite
- Tailwind CSS
- Zustand (State Management)
- React Router
- Axios

## 프로젝트 구조

```
craft-ai/
├── backend/                 # FastAPI 백엔드
│   ├── app/
│   │   ├── api/            # API 라우트
│   │   ├── models/         # 데이터베이스 모델
│   │   ├── services/       # 외부 서비스 (Gemini, 나노바나나 등)
│   │   ├── schemas/        # Pydantic 스키마
│   │   ├── utils/          # 유틸리티
│   │   ├── config.py       # 설정
│   │   └── main.py         # 진입점
│   ├── tests/              # 테스트
│   └── requirements.txt    # 의존성
├── frontend/               # React 프론트엔드
│   ├── src/
│   │   ├── components/     # React 컴포넌트
│   │   ├── pages/          # 페이지
│   │   ├── stores/         # Zustand 스토어
│   │   ├── utils/          # 유틸리티
│   │   └── assets/         # 정적 파일
│   ├── public/
│   └── package.json
├── data/                   # 데이터 파일
│   ├── raw/               # 원본 데이터
│   ├── processed/         # 처리된 데이터
│   └── segments/          # 세분화 데이터
├── docs/                   # 문서
├── scripts/                # 유틸리티 스크립트
└── README.md
```

## 설치 및 실행

### 1. 저장소 클론

```bash
git clone <repository-url>
cd craft-ai
```

### 2. 백엔드 설정

```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일을 열어 API 키 등을 설정

# 서버 실행
uvicorn app.main:app --reload --port 8000
```

백엔드 API: http://localhost:8000
API 문서: http://localhost:8000/docs

### 3. 프론트엔드 설정

```bash
cd frontend

# 의존성 설치
npm install

# 환경변수 설정
cp .env.example .env

# 개발 서버 실행
npm run dev
```

프론트엔드: http://localhost:5173

## API 엔드포인트

### Health Check
- `GET /` - API 정보
- `GET /health` - 헬스 체크

### 프로젝트 (예정)
- `POST /api/projects` - 프로젝트 생성
- `GET /api/projects` - 프로젝트 목록
- `GET /api/projects/{id}` - 프로젝트 상세
- `PUT /api/projects/{id}` - 프로젝트 수정
- `DELETE /api/projects/{id}` - 프로젝트 삭제

### 생성 (예정)
- `POST /api/generate/strategy` - 마케팅 전략 제안
- `POST /api/generate/content` - 콘텐츠 생성 (카피 + 이미지)

### 분석 (예정)
- `POST /api/analysis/performance` - 성과 예측
- `GET /api/analysis/dashboard` - 대시보드 데이터

## 개발 일정 (7주)

### 1주차: 프로젝트 이해 및 기획
- [x] 프로젝트 기획서 작성
- [x] 기능 정의서 작성
- [x] 개발 환경 설정

### 2주차: 데이터 수집 및 고객 세분화 (현재)
- [ ] Kaggle 데이터셋 수집
- [ ] 공공데이터 수집
- [ ] Gemini API로 합성 데이터 생성
- [ ] 세분화 모듈 구현
- [ ] 데이터 저장 (JSON/CSV)

### 3주차: 맞춤형 콘텐츠 생성
- [ ] Gemini API 연동
- [ ] 나노바나나 API 연동
- [ ] 전략 제안 기능
- [ ] 카피 생성 기능 (3가지 톤)
- [ ] 이미지 생성 기능
- [ ] 기본 UI 구현

### 4주차: 캠페인 성과 분석
- [ ] 가상 사용자 반응 데이터 생성
- [ ] 성과 분석 로직 구현
- [ ] Streamlit 대시보드 개발
- [ ] AI 기반 성과 예측

### 5주차: 기능 통합 및 서비스화
- [ ] React 프론트엔드 본격 개발
- [ ] 백엔드 API 완성
- [ ] 전체 통합 테스트
- [ ] 데이터베이스 스키마 완성

### 6주차: 품질 개선 및 UX 강화
- [ ] 프롬프트 최적화
- [ ] UI/UX 개선
- [ ] 성능 최적화
- [ ] 다양한 옵션 추가

### 7주차: 기능 고도화 및 배포
- [ ] 부가 기능 개발 (최소 1개)
- [ ] 클라우드 배포 (Vercel + Railway)
- [ ] 최종 통합 테스트
- [ ] 문서화 및 발표 준비

## 환경 변수

### Backend (.env)
```
GEMINI_API_KEY=your_key
VOYAGE_AI_API_KEY=your_key
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
QDRANT_URL=http://...
QDRANT_API_KEY=your_key
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

## 테스트

```bash
# 백엔드 테스트
cd backend
pytest

# 프론트엔드 테스트
cd frontend
npm test
```

## 배포

### Frontend (Vercel)
```bash
cd frontend
npm run build
# Vercel CLI 또는 GitHub 연동으로 배포
```

### Backend (Railway)
```bash
cd backend
# Railway CLI 또는 GitHub 연동으로 배포
```

## 라이선스

MIT License

## 문서

자세한 내용은 다음 문서를 참고하세요:
- [프로젝트 기획서](./프로젝트_기획서_v2.md)
- [기능 정의서](./기능_정의서_v2.md)
- [개발 TODO](./TODO.md)

## 기여

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 연락처

프로젝트 관련 문의사항은 이슈를 등록해주세요.
test
