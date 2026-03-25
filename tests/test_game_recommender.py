"""
Test jednostkowy (PyTest) weryfikujący stabilność silnika rekomendacji gier.
Sprawdza czy maszyna zlicza gry prawidłowo, buduje kształtną macierz SBERT,
lub jak algorytm zachowuje się przy błędnych / brakujących tytułach gier.
"""
from app.ml.core_logic.games.game_recommender import load_games, recommend_game

def test_load_games():
    """Sprawdza wczytywanie danych o grach i macierzy podobieństwa."""
    games, similarity = load_games(path='dataset/games.csv')
    assert len(games) > 0
    assert similarity.shape[0] == similarity.shape[1]
    assert similarity.shape[0] == len(games)

def test_recommend_gamme_known_title():
    """Sprawdza rekomendacje dla istniejącej gry."""
    games, similarity = load_games(path='dataset/games.csv')
    base, recs = recommend_game(games, similarity, 'Fortnite')
    assert isinstance(base, str)
    assert isinstance(recs, list)
    assert len(recs) > 0

def test_recommend_game_unknown_title():
    """Sprawdza zachowanie dla nieistniejącego tytułu gry."""
    games, similarity = load_games(path='dataset/games.csv')
    base, recs = recommend_game(games, similarity, 'asdasdasdasd123123')
    assert base is None
    assert not recs

def test_recommend_game_empty_title():
    """Sprawdza zachowanie dla pustego tytułu gry."""
    games, similarity = load_games(path='dataset/games.csv')
    base, recs = recommend_game(games, similarity, '   ')
    assert base is None
    assert not recs
