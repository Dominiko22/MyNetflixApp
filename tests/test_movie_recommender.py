"""
Test jednostkowy (PyTest) weryfikujący stabilność silnika rekomendacji filmów.
Obejmuje test ładowania Datasetu CSV, obliczanie struktury TF-IDF oraz sprawdza
zachowanie funkcji przy podawaniu pustych lub zmyślonych nazw.
"""
from app.ml.core_logic.movies.movie_recommender import load_movies, recommend_movie

def test_load_movies():
    """Sprawdza wczytywanie danych o filamch i macierzy podobieństwa."""
    movies, similarity = load_movies(path='dataset/movies.csv')
    assert len(movies) > 0
    assert similarity.shape[0] == similarity.shape[1]
    assert similarity.shape[0] == len(movies)

def test_recommend_movie_for_known_title():
    """Sprawdza rekomendacje dla istniejącego filmu."""
    movies, similarity = load_movies(path='dataset/movies.csv')
    base, recs = recommend_movie(movies, similarity, 'Matrix')
    assert isinstance(base, str)
    assert isinstance(recs, list)
    assert len(recs) > 0

def test_recommend_movie_unknown_title():
    """Sprawdza zachowanie dla nieistniejącego tytułu filmu."""
    movies, similarity = load_movies(path='dataset/movies.csv')
    base, recs = recommend_movie(movies, similarity, 'asdasdasdasd123123')
    assert base is None
    assert not recs

def test_recommend_movie_empty_title():
    """Sprawdza zachowanie dla pustego tytułu filmu."""
    movies, similarity = load_movies(path='dataset/movies.csv')
    base, recs = recommend_movie(movies, similarity, '   ')
    assert base is None
    assert not recs
