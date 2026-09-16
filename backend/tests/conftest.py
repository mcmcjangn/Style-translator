"""테스트 공용 fixture.

실제 Gemini API는 호출하지 않습니다. FakeGeminiClient를 DI로 주입합니다.
"""

import pytest
from fastapi.testclient import TestClient

from api.routes import get_translate_service
from main import app
from services.translate import TranslateService

DEFAULT_REPLY = "번역된 결과입니다."


def error_message(response) -> str:
    """에러 응답에서 사람이 읽을 메시지를 꺼냅니다.

    현재 백엔드는 FastAPI 기본 형식 {"detail": "..."}을 사용합니다.
    공통 예외처리 리팩토링(1.5단계)으로 형식이 바뀌면 이 함수만 수정하면
    전체 테스트가 따라옵니다. 테스트 본문에서 response.json()["detail"]을
    직접 읽지 마세요.
    """
    body = response.json()
    return body["detail"]


class FakeGeminiClient:
    """GeminiClient 대역. 호출 인자를 기록해 프롬프트 조립을 검증할 수 있습니다."""

    def __init__(self, *, configured: bool = True, reply: str = DEFAULT_REPLY):
        self._configured = configured
        self.reply = reply
        self.calls: list[dict] = []

    @property
    def is_configured(self) -> bool:
        return self._configured

    def generate(self, contents: str, system_instruction: str) -> str:
        self.calls.append({"contents": contents, "system_instruction": system_instruction})
        return self.reply


@pytest.fixture
def fake_client():
    return FakeGeminiClient()


@pytest.fixture
def client(fake_client):
    """FakeGeminiClient가 주입된 TestClient."""
    app.dependency_overrides[get_translate_service] = lambda: TranslateService(fake_client)
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def make_client():
    """원하는 상태의 가짜 클라이언트로 TestClient를 만드는 팩토리.

    사용: test_client, fake = make_client(configured=False)
    """

    def _make(**kwargs):
        fake = FakeGeminiClient(**kwargs)
        app.dependency_overrides[get_translate_service] = lambda: TranslateService(fake)
        return TestClient(app), fake

    yield _make
    app.dependency_overrides.clear()
