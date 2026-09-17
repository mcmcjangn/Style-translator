"""GET /styles — 프론트엔드 드롭다운용 {key: label} 맵."""

from conftest import success_data
from styles import STYLES


def test_styles_returns_all_defined_styles(client):
    res = client.get("/styles")

    assert res.status_code == 200
    assert set(success_data(res)) == set(STYLES)


def test_styles_maps_key_to_label(client):
    data = success_data(client.get("/styles"))

    for key, definition in STYLES.items():
        assert data[key] == definition["label"]


def test_styles_values_are_all_strings(client):
    """label이 dict째로 새어나가지 않는지 (내부 정의 노출 방지)."""
    data = success_data(client.get("/styles"))

    assert all(isinstance(value, str) for value in data.values())
