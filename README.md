# 말투 번역기 (Style Translator) — MVP

같은 문장을 격식체 / 사극체 / SNS체 / 문학체 등 원하는 스타일로 바꿔 번역해주는
FastAPI + React 웹앱입니다. 1단계 MVP: 짧은 문장을 스타일 프롬프트로 변환해
OpenAI API로 번역합니다.

## 구조

```
style-translator/
├── backend/          # FastAPI 서버
│   ├── main.py       # /translate, /styles 엔드포인트
│   ├── styles.py      # 스타일별 프롬프트 정의 (few-shot 예시)
│   ├── requirements.txt
│   └── .env.example
└── frontend/         # React (Vite) 클라이언트
    ├── src/App.jsx
    ├── src/App.css
    └── package.json
```

## 실행 방법

### 1. 백엔드

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # .env에 본인 OPENAI_API_KEY 입력
uvicorn main:app --reload --port 8000
```

`http://localhost:8000/docs` 에서 Swagger UI로 API를 바로 테스트할 수 있습니다.

### 2. 프론트엔드

```bash
cd frontend
npm install
npm run dev
```

`http://localhost:5173` 에서 확인하세요. (백엔드가 8000번 포트에서 먼저 떠 있어야 합니다.)

## 다음 단계 (로드맵)

- [x] 1단계: 핵심 MVP — 단문 스타일 번역
- [ ] 2단계: 장문 처리 — 문서를 청크 단위로 나눠 번역
- [ ] 3단계: 문맥 일관성 — 이전 청크 번역을 벡터 DB에 저장하고 검색해 프롬프트에 주입 (RAG)
- [ ] 4단계: Redis 캐싱 + 비용/요청 로그 + Docker/AWS 배포

## 스타일 추가하기

`backend/styles.py`의 `STYLES` 딕셔너리에 항목을 하나 추가하면 프론트엔드
드롭다운에 자동으로 반영됩니다. (few-shot 예시 2~3개를 함께 넣어주세요.)
