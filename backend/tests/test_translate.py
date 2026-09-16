"""POST /translate — 정상 케이스 + 에러 케이스.

에러 메시지 단정은 conftest.error_message()를 거칩니다.
응답 형식이 바뀌면 그 헬퍼만 고치면 됩니다.
"""

import pytest
from google.genai import errors as genai_errors

from conftest import DEFAULT_REPLY, error_message
from styles import STYLES


def payload(**overrides) -> dict:
    body = {"text": "이거 언제까지 가능해?", "target_lang": "한국어", "style": "general"}
    body.update(overrides)
    return body


# ---------- 정상 케이스 ----------


def test_translate_returns_translated_text(client):
    res = client.post("/translate", json=payload())

    assert res.status_code == 200
    assert res.json() == {"translated": DEFAULT_REPLY, "style": "general"}


@pytest.mark.parametrize("style", sorted(STYLES))
def test_translate_accepts_every_defined_style(client, style):
    """STYLES에 스타일을 추가해도 엔드포인트가 받아주는지 자동으로 검증."""
    res = client.post("/translate", json=payload(style=style))

    assert res.status_code == 200
    assert res.json()["style"] == style


def test_translate_strips_whitespace_from_model_output(make_client):
    test_client, _ = make_client(reply="  앞뒤 공백 있는 응답  \n")

    assert test_client.post("/translate", json=payload()).json()["translated"] == "앞뒤 공백 있는 응답"


def test_translate_passes_text_and_style_prompt_to_client(client, fake_client):
    """프롬프트 조립 검증 — 원문, 대상 언어, 스타일 설명, few-shot 예시가 들어가야 함."""
    client.post("/translate", json=payload(text="안녕", target_lang="영어", style="sns"))

    assert len(fake_client.calls) == 1
    call = fake_client.calls[0]
    assert call["contents"] == "안녕"
    prompt = call["system_instruction"]
    assert "영어" in prompt
    assert STYLES["sns"]["description"] in prompt
    assert STYLES["sns"]["examples"][0]["source"] in prompt


# ---------- 에러 케이스 ----------


def test_translate_rejects_unknown_style(client):
    res = client.post("/translate", json=payload(style="존재하지_않는_스타일"))

    assert res.status_code == 400
    assert "존재하지_않는_스타일" in error_message(res)


def test_translate_rejects_empty_text(client):
    res = client.post("/translate", json=payload(text=""))

    assert res.status_code == 400
    assert "비어" in error_message(res)


def test_translate_rejects_whitespace_only_text(client):
    res = client.post("/translate", json=payload(text="   \n\t  "))

    assert res.status_code == 400


def test_translate_does_not_call_client_on_validation_error(client, fake_client):
    """검증 실패 시 Gemini 호출이 일어나지 않아야 함 (불필요한 과금 방지)."""
    client.post("/translate", json=payload(style="없는스타일"))
    client.post("/translate", json=payload(text=""))

    assert fake_client.calls == []


def test_translate_fails_when_api_key_missing(make_client):
    test_client, _ = make_client(configured=False)

    res = test_client.post("/translate", json=payload())

    assert res.status_code == 500
    assert "GEMINI_API_KEY" in error_message(res)


def test_translate_returns_502_when_gemini_fails(make_client):
    """Gemini 장애는 서버 오류(500)가 아니라 업스트림 오류(502)로 나가야 함."""
    test_client, fake = make_client()

    def boom(contents, system_instruction):
        raise genai_errors.APIError(503, {"error": {"message": "service unavailable"}})

    fake.generate = boom

    res = test_client.post("/translate", json=payload())

    assert res.status_code == 502
    assert "번역 엔진" in error_message(res)


# ---------- 스키마 검증 (FastAPI/Pydantic 기본 422) ----------


@pytest.mark.parametrize("missing", ["text", "target_lang", "style"])
def test_translate_requires_all_fields(client, missing):
    body = payload()
    del body[missing]

    assert client.post("/translate", json=body).status_code == 422


def test_translate_rejects_wrong_type(client):
    assert client.post("/translate", json=payload(text=123)).status_code == 422
