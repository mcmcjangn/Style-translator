"""GET /health — API 키 설정 여부 확인용 헬스체크."""

import api.routes as routes


def test_health_returns_ok(client):
    res = client.get("/health")

    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_health_reports_api_key_configured(client, monkeypatch):
    """/health는 DI를 거치지 않고 전역 gemini_client를 직접 읽습니다.

    따라서 dependency_overrides가 통하지 않아 monkeypatch가 필요합니다.
    (1.5단계에서 /health도 Depends를 타게 바꾸면 이 테스트를 fixture 기반으로
    단순화할 수 있습니다.)
    """
    monkeypatch.setattr(routes.gemini_client, "_client", object())

    assert client.get("/health").json()["api_key_configured"] is True


def test_health_reports_api_key_missing(client, monkeypatch):
    monkeypatch.setattr(routes.gemini_client, "_client", None)

    assert client.get("/health").json()["api_key_configured"] is False
