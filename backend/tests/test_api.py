from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_recommend_returns_am_and_pm():
    quiz = {"skin_type": "oily", "concerns": ["acne"], "max_price": 60}
    response = client.post("/recommend", json=quiz)
    assert response.status_code == 200
    body = response.json()
    assert "am" in body and "pm" in body


def test_bad_skin_type_is_rejected():
    quiz = {"skin_type": "purple", "concerns": [], "max_price": 60}
    assert client.post("/recommend", json=quiz).status_code == 422