"""POST /translate — 레이트 리미트 (429)."""

import core.rate_limit as rate_limit_module
from conftest import error_code
from core.rate_limit import RateLimiter, rate_limiter


def payload(**overrides) -> dict:
    body = {"text": "이거 언제까지 가능해?", "target_lang": "한국어", "style": "general"}
    body.update(overrides)
    return body


def test_translate_allows_requests_up_to_the_limit(client):
    for _ in range(rate_limiter.limit):
        assert client.post("/translate", json=payload()).status_code == 200


def test_translate_returns_429_once_limit_exceeded(client):
    for _ in range(rate_limiter.limit):
        client.post("/translate", json=payload())

    res = client.post("/translate", json=payload())

    assert res.status_code == 429
    assert error_code(res) == "RATE_LIMIT_EXCEEDED"


def test_health_and_styles_are_not_rate_limited(client):
    for _ in range(rate_limiter.limit + 5):
        assert client.get("/health").status_code == 200
        assert client.get("/styles").status_code == 200


def test_rate_limiter_evicts_expired_entries_to_bound_memory(monkeypatch):
    """윈도가 지난 키를 청소하지 않으면 한 번이라도 요청한 모든 IP가 프로세스 수명 내내
    쌓여 메모리가 무한정 늘어남 — 스윕이 실제로 옛 항목을 지우는지 직접 검증."""
    now = [0.0]
    monkeypatch.setattr(rate_limit_module.time, "monotonic", lambda: now[0])

    limiter = RateLimiter(limit=100, window_seconds=10)
    for i in range(50):
        limiter.check(f"ip-{i}")
    assert len(limiter._hits) == 50

    now[0] = 25.0  # window(10s) + 스윕 주기(10s)를 넘겨 이동
    limiter.check("ip-new")

    assert len(limiter._hits) == 1
