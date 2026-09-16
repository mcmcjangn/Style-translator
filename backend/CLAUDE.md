# Backend — CLAUDE.md

FastAPI 앱. 레이어 분리 구조 (router → service → client).

## Commands

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000     # Swagger: http://localhost:8000/docs
pip install -r requirements.txt
pytest                                    # 테스트 (pytest.ini: pythonpath=., testpaths=tests)
```

## Layers

| 파일 | 역할 |
|---|---|
| `main.py` | FastAPI 인스턴스, CORS 미들웨어, 라우터 등록 |
| `api/routes.py` | 엔드포인트 3개 + `get_translate_service()` DI 팩토리 |
| `services/translate.py` | `TranslateService` — 검증, 프롬프트 조립, 클라이언트 호출 |
| `clients/gemini.py` | `GeminiClient` — Gemini SDK 래퍼. 모듈 로드 시 싱글톤 `gemini_client` 생성 |
| `core/config.py` | `Settings` — 환경변수, 모델명, CORS 허용 오리진 |
| `models/schemas.py` | `TranslateRequest` / `TranslateResponse` |
| `styles.py` | `STYLES` 딕셔너리 — 스타일 단일 정의처 |

## Endpoints

- `GET /health` → `{"status": "ok", "api_key_configured": bool}`
- `GET /styles` → `{key: label}` (`STYLES`에서 생성)
- `POST /translate` — `{text, target_lang, style}` → `{translated, style}`

에러 (현재 `services/translate.py`에서 `HTTPException` 직접 raise):

| 조건 | 코드 | detail |
|---|---|---|
| API 키 미설정 | 500 | `GEMINI_API_KEY가 설정되지 않았습니다...` |
| 알 수 없는 스타일 | 400 | `알 수 없는 스타일: {style}` |
| 빈 텍스트 | 400 | `번역할 텍스트가 비어 있습니다.` |
| Gemini 호출 실패 | 502 | `번역 엔진 호출 실패: {exc}` (`api/routes.py`에서 처리) |

## Gemini 호출

`clients/gemini.py` — 모델 `gemini-3.5-flash`, temperature 0.3, max_output_tokens 1024.
`GEMINI_API_KEY`가 없으면 `_client=None`이 되고 `is_configured`가 False (import 자체는 성공하므로 CI에서 키 없이 테스트 가능).

프롬프트는 `TranslateService._build_system_prompt()`에서 `target_lang` + 스타일 `description` + few-shot `examples`를 한국어 시스템 지시문에 주입해 조립.

## Adding a Style

`styles.py`의 `STYLES`에 항목 추가만 하면 됩니다 (현재 `general` / `formal` / `sns`).
프론트엔드는 `/styles`로 자동 반영되므로 다른 수정 불필요.

```python
"your_key": {
    "label": "UI에 표시될 이름",
    "description": "시스템 프롬프트에 들어갈 스타일 설명",
    "examples": [{"source": "원문 예시", "target": "스타일 적용 예시"}],
},
```

## Testing

`tests/conftest.py`에 `FakeGeminiClient`와 `client` fixture가 있습니다.
실제 Gemini API를 호출하지 않으며, `app.dependency_overrides[get_translate_service]`로 주입합니다.

- **에러 응답 형식을 단정할 때는 `conftest.py`의 `error_message()` 헬퍼를 쓰세요.**
  공통 예외처리 리팩토링 시 그 함수 한 곳만 고치면 전체 테스트가 따라옵니다.
- `GET /health`는 DI를 거치지 않고 전역 `gemini_client`를 직접 읽습니다 (`api/routes.py`).
  따라서 `dependency_overrides`가 통하지 않고 `monkeypatch`가 필요합니다.
