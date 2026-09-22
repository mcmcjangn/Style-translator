# CLAUDE.md

## Project Overview

**말투 번역기 (Style Translator)** — 입력 텍스트를 지정한 말투(일반체/격식체/SNS체)로 번역하는 서비스.
Google Gemini API 사용. FastAPI 백엔드 + React/Vite 프론트엔드.

## Repo Layout

```
backend/    FastAPI 앱 — 상세는 backend/CLAUDE.md
frontend/   React/Vite 앱 — 상세는 frontend/CLAUDE.md
.github/workflows/ci-backend.yml    PR 자동 테스트 (backend-test) — `backend/**` 변경 시만 실행
.github/workflows/ci-frontend.yml   PR 자동 테스트 (frontend-test) — `frontend/**` 변경 시만 실행
```

**작업 범위에 맞는 하위 CLAUDE.md만 읽으세요.** 백엔드만 만질 때 프론트엔드 문서는 불필요합니다.

## Branch Convention

- `main` — 배포 기준
- `develop` — 통합 브랜치. 기능 작업은 `develop`에서 분기해 `develop`으로 PR
- CI는 `main` / `develop`으로 들어오는 PR에서 실행됨

## Cross-cutting Notes

- 모든 응답은 공통 envelope으로 감싸짐.
  성공 `{"success": true, "data": ...}` / 실패 `{"success": false, "error": {"code", "message"}}`.
  **양쪽이 이 형식에 묶여 있음** — 백엔드는 `core/envelope.py` + `core/error_handlers.py`,
  프론트엔드는 `src/api/client.js`의 `unwrap()`. 형식을 바꾸면 백엔드/프론트엔드/테스트를 함께 수정해야 함.
  다만 각 레이어에서 껍데기를 벗기는 지점이 한 곳씩으로 모여 있어 수정 범위는 좁음
  (백엔드 테스트는 `tests/conftest.py`의 헬퍼).
- `backend/.env`의 `GEMINI_API_KEY`는 커밋 금지 (`.gitignore`에 등록됨).
- `node_modules/`는 위치 무관하게 무시됨. `npm install`은 반드시 `frontend/`에서 실행.
