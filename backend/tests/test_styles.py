"""GET /styles — 프론트엔드 드롭다운용 {key: label} 맵."""

from styles import STYLES


def test_styles_returns_all_defined_styles(client):
    res = client.get("/styles")

    assert res.status_code == 200
    assert set(res.json()) == set(STYLES)


def test_styles_maps_key_to_label(client):
    body = client.get("/styles").json()

    for key, definition in STYLES.items():
        assert body[key] == definition["label"]


def test_styles_values_are_all_strings(client):
    """label이 dict째로 새어나가지 않는지 (내부 정의 노출 방지)."""
    body = client.get("/styles").json()

    assert all(isinstance(value, str) for value in body.values())
