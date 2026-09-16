# CLAUDE.md

## Project Overview

**말투 번역기 (Style Translator)** — 입력 텍스트를 지정한 말투(일반체/격식체/SNS체)로 번역하는 서비스.
Google Gemini API 사용. FastAPI 백엔드 + React/Vite 프론트엔드.

## Repo Layout

```
backend/    FastAPI 앱 — 상세는 backend/CLAUDE.md
frontend/   React/Vite 앱 — 상세는 frontend/CLAUDE.md
.github/workflows/ci.yml   PR 자동 테스트 (backend-test / frontend-test)
```

**작업 범위에 맞는 하위 CLAUDE.md만 읽으세요.** 백엔드만 만질 때 프론트엔드 문서는 불필요합니다.

## Branch Convention

- `main` — 배포 기준
- `develop` — 통합 브랜치. 기능 작업은 `develop`에서 분기해 `develop`으로 PR
- CI는 `main` / `develop`으로 들어오는 PR에서 실행됨

## Cross-cutting Notes

- 에러 응답은 현재 FastAPI 기본 형식 `{"detail": "..."}`.
  프론트엔드 `src/api/client.js`가 `data.detail`을 읽으므로 **양쪽이 이 형식에 묶여 있음**.
  공통 예외처리 리팩토링 시 백엔드/프론트엔드/테스트를 함께 수정해야 함.
- `backend/.env`의 `GEMINI_API_KEY`는 커밋 금지 (`.gitignore`에 등록됨).
- `node_modules/`는 위치 무관하게 무시됨. `npm install`은 반드시 `frontend/`에서 실행.
