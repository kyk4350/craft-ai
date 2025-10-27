# API 키 및 클라우드 서비스 가입 가이드

## 필수 서비스 (지금 가입)

### 1. Gemini API (Google AI Studio)
✅ **이미 완료**

---

### 2. Stability AI (이미지 생성)

**용도**: 개발 중 저렴한 이미지 생성 ($0.004/장)

**가입 링크**: https://platform.stability.ai/

**가입 절차**:
1. https://platform.stability.ai/ 접속
2. "Sign Up" 클릭
3. Google 계정으로 가입 (또는 이메일)
4. Dashboard 접속
5. "API Keys" 메뉴로 이동
6. "Create API Key" 클릭
7. 키 이름 입력 (예: "ContentCraft Development")
8. API 키 복사 → .env 파일에 저장

**요금제**:
- 최초 가입 시 무료 크레딧 제공 (보통 $10)
- 이후 사용량만큼 과금
- SDXL: $0.004/이미지

**API 키 위치**:
```bash
# backend/.env
STABILITY_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
```

---

### 3. Supabase (PostgreSQL 데이터베이스)

**용도**: 사용자, 프로젝트, 콘텐츠 데이터 저장

**가입 링크**: https://supabase.com/

**가입 절차**:
1. https://supabase.com/ 접속
2. "Start your project" 클릭
3. GitHub 계정으로 로그인 (권장)
4. "New Project" 클릭
5. 프로젝트 설정:
   - Name: `contentcraft-ai`
   - Database Password: 강력한 비밀번호 생성 (저장 필수!)
   - Region: `Northeast Asia (Seoul)` 선택
   - Pricing Plan: `Free` (무료)
6. "Create new project" 클릭 (2-3분 소요)
7. 프로젝트 생성 완료 후 Settings → Database 이동
8. Connection String 복사:
   - URI 형식 선택
   - Password를 본인이 설정한 것으로 변경

**무료 플랜 제한**:
- 500 MB 데이터베이스
- 1 GB 파일 스토리지
- 50 MB 파일 업로드 제한
- 50,000 월간 활성 사용자

**DATABASE_URL 형식**:
```bash
# backend/.env
DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres
```

---

### 4. Upstash (Redis)

**용도**: API 응답 캐싱, 성능 최적화

**가입 링크**: https://upstash.com/

**가입 절차**:
1. https://upstash.com/ 접속
2. "Get Started" 클릭
3. GitHub 또는 Google 계정으로 로그인
4. Console 접속
5. "Create Database" 클릭
6. 데이터베이스 설정:
   - Name: `contentcraft-cache`
   - Type: `Regional`
   - Region: `ap-northeast-1 (Tokyo)` (가장 가까운 지역)
   - Eviction: `allkeys-lru` (메모리 가득 차면 오래된 키 삭제)
7. "Create" 클릭
8. Database Details에서 "REST API" 탭 선택
9. `UPSTASH_REDIS_REST_URL` 복사

**무료 플랜 제한**:
- 10,000 commands/day
- 256 MB 메모리
- 개발 환경에 충분함

**REDIS_URL 형식**:
```bash
# backend/.env
REDIS_URL=https://xxxxx.upstash.io
# 또는
REDIS_URL=rediss://default:[password]@xxxxx.upstash.io:6379
```

---

### 5. Qdrant Cloud (Vector Database)

**용도**: 콘텐츠 임베딩 저장, 유사도 검색

**가입 링크**: https://cloud.qdrant.io/

**가입 절차**:
1. https://cloud.qdrant.io/ 접속
2. "Sign Up" 클릭
3. Google 또는 GitHub 계정으로 로그인
4. "Create Cluster" 클릭
5. 클러스터 설정:
   - Cluster Name: `contentcraft-vectors`
   - Cloud Provider: `AWS`
   - Region: `ap-northeast-1 (Tokyo)`
   - Configuration: `Free` (1 GB)
6. "Create" 클릭 (5분 정도 소요)
7. 클러스터 생성 완료 후 "API Keys" 탭으로 이동
8. "Create API Key" 클릭
9. API Key와 Cluster URL 복사

**무료 플랜 제한**:
- 1 GB 스토리지
- 1 million vectors
- 개발 및 소규모 프로젝트에 충분

**Qdrant 설정**:
```bash
# backend/.env
QDRANT_URL=https://xxxxx.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=xxxxx-xxxx-xxxx-xxxx-xxxxx
```

---

### 6. Voyage AI (임베딩 API) - 선택사항

**용도**: 텍스트를 벡터로 변환 (Vector DB용)

**가입 링크**: https://www.voyageai.com/

**가입 절차**:
1. https://www.voyageai.com/ 접속
2. "Get API Key" 클릭
3. Google 계정으로 로그인
4. Dashboard → "API Keys" 이동
5. "Create New Key" 클릭
6. API 키 복사

**무료 플랜**:
- 월 100만 토큰 무료
- 이후 $0.06 / 1M tokens

**대안**:
- OpenAI Embeddings (유료)
- Sentence Transformers (무료, 로컬)

```bash
# backend/.env
VOYAGE_AI_API_KEY=pa-xxxxxxxxxxxxxxxxxxxxx
```

---

## 전체 .env 파일 예시

```bash
# backend/.env

# ===== API Keys =====

# Gemini API (텍스트 생성)
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Stability AI (이미지 생성 - 개발 중)
STABILITY_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Voyage AI (임베딩 - 선택사항)
VOYAGE_AI_API_KEY=pa-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# ===== AI 모델 설정 =====

# IMAGE_PROVIDER: mock (개발 초기), stability (개발 중), nanobanana (최종)
IMAGE_PROVIDER=mock

# GEMINI_MODEL: gemini-1.5-flash (기본), gemini-1.5-pro (고품질)
GEMINI_MODEL=gemini-1.5-flash

# ===== 데이터베이스 =====

# Supabase PostgreSQL
DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres

# Upstash Redis
REDIS_URL=rediss://default:[password]@xxxxx.upstash.io:6379

# Qdrant Vector DB
QDRANT_URL=https://xxxxx.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=xxxxx-xxxx-xxxx-xxxx-xxxxx

# ===== Application =====

ENVIRONMENT=development
DEBUG=True
```

---

## 가입 우선순위

### 지금 바로 가입 (필수)
1. ✅ Gemini API - 이미 완료
2. 🔴 Stability AI - 이미지 생성용 (Week 4부터 사용)
3. 🔴 Supabase - 데이터베이스 (Week 2부터 사용)

### 이번 주 내 가입 (권장)
4. 🟡 Upstash Redis - 캐싱용 (Week 3부터 사용)
5. 🟡 Qdrant Cloud - Vector DB (Week 4부터 사용)

### 나중에 필요하면 가입
6. ⚪ Voyage AI - 임베딩용 (대안 있음)

---

## 체크리스트

### 가입 완료 체크
- [ ] Gemini API ✅ (이미 완료)
- [ ] Stability AI
- [ ] Supabase (PostgreSQL)
- [ ] Upstash (Redis)
- [ ] Qdrant Cloud (Vector DB)
- [ ] Voyage AI (선택)

### API 키 저장 체크
- [ ] backend/.env 파일에 모든 키 입력
- [ ] DATABASE_URL 비밀번호 정확히 입력
- [ ] .env 파일이 .gitignore에 있는지 확인 ✅

### 연결 테스트 체크
- [ ] Gemini API 테스트
- [ ] Stability AI 테스트
- [ ] Supabase 연결 테스트
- [ ] Redis 연결 테스트
- [ ] Qdrant 연결 테스트

---

## 예상 비용 (월간)

```
Gemini API (무료 tier): $0
Stability AI: ~$2 (개발 중 500장)
Supabase (Free): $0
Upstash (Free): $0
Qdrant (Free): $0
Voyage AI (Free): $0

총 예상 비용: ~$2/월 (개발 기간)
최종 배포 시: ~$10-15/월
```

---

## 문제 해결

### Supabase 연결 오류
- 비밀번호에 특수문자가 있으면 URL 인코딩 필요
- Connection pooler 사용 (6543 포트)

### Upstash Redis 연결 오류
- `rediss://` (SSL) 사용 확인
- REST API URL도 사용 가능

### Qdrant 연결 오류
- 클러스터가 완전히 시작될 때까지 5-10분 대기
- API Key와 URL 정확히 확인

---

마지막 업데이트: 2025-10-27
