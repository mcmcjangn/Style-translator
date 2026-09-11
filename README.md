# 말투 번역기 (Style Translator)

같은 문장도 상황에 따라 격식체, 일반체, 캐주얼체 등 다른 말투로 표현해야 하는
번역 수요를 해결하는 AI 기반 다중 스타일 번역 서비스입니다.
FastAPI 백엔드 + React(Vite) 프론트엔드로 구성되어 있으며,
Google Gemini API를 통해 스타일별 프롬프트 기반 번역을 수행합니다.

## 기술 스택

- **백엔드**: FastAPI, Python, google-genai SDK
- **프론트엔드**: React, Vite
- **번역 엔진**: Google Gemini API (gemini-3.5-flash)

## 구조

style-translator/
├── backend/
│ ├── main.py # /translate, /styles, /health 엔드포인트
│ ├── styles.py # 스타일별 프롬프트 정의 (few-shot 예시)
│ ├── requirements.txt
│ └── .env.example
└── frontend/
├── src/App.jsx
├── src/App.css
└── package.json


## 실행 방법

### 백엔드

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # .env에 본인 GEMINI_API_KEY 입력
uvicorn main:app --reload --port 8000
```

`http://localhost:8000/docs`에서 Swagger UI로 API를 바로 테스트할 수 있습니다.

### 프론트엔드

```bash
cd frontend
npm install
npm run dev
```

`http://localhost:5173`에서 확인하세요.

## 로드맵

### ✅ 1단계 — 핵심 MVP
짧은 문장을 스타일 프롬프트로 변환해 Gemini API로 번역. 완료.

### 2단계 — 장문 처리
문서를 문단/토큰 단위로 청킹하고, 청크 단위로 순차 번역하는 기능 추가.

### 3단계 — 테스트 & QA 체계 구축
- `pytest` 기반 단위/통합 테스트 작성 (`/translate`, `/styles`, `/health` 엔드포인트)
- 정상 케이스 + 에러 케이스(잘못된 스타일, 빈 텍스트, API 키 누락 등) 함께 커버
- 테스트를 CI(GitHub Actions)에 연동해 PR마다 자동 실행
- 목표: "테스트 커버리지를 기반으로 안정성을 확보한 백엔드"를 실제 코드로 증명

### 4단계 — 대용량 트래픽 대응
- 동일 문장+스타일 조합 캐싱 (Redis) — 중복 API 호출 방지
- Rate limiting으로 과도한 요청 차단
- 비동기 처리(async I/O)로 동시 요청 처리량 개선
- 부하 테스트(Locust 또는 k6)로 처리 가능한 동시 사용자 수 측정 및 기록
- 목표: "몇 명까지 동시에 처리 가능한지"를 숫자로 말할 수 있는 백엔드

### 5단계 — 문맥 일관성 (RAG)
청크 번역 결과를 벡터 DB에 저장하고, 다음 청크 번역 시 관련 문맥을 검색해
프롬프트에 주입 — 캐릭터명/말투 일관성 유지.

### 6단계 — 배포 & 모니터링
Docker 컨테이너화 → AWS 배포 → 로그/비용 모니터링 대시보드 구성.

## 스타일 추가하기

`backend/styles.py`의 `STYLES` 딕셔너리에 항목을 추가하면 프론트엔드
드롭다운에 자동으로 반영됩니다.