"""
Test jednostkowy dla głównych routerów API opartych na instancji Flask.
Sprawdza łączność HTTP, dostępność stron po stronie klienta oraz generowanie błędów
(np. błąd 400 przy wywołaniu endpointu API bez parametrów).
"""
from run import app


def test_home_page():
    """Sprawdza, czy strona główna działa (HTTP 200)."""
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200


def test_recommend_movie_missing_title():
    """Sprawdza błąd 400, gdy brak parametru 'title' dla filmu."""
    client = app.test_client()
    response = client.get("/recommend_movie")
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
