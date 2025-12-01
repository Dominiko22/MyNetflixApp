"""Algorytm rekomendacji filmów na podstawie podobieństwa TF‑IDF."""

from difflib import get_close_matches

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def sort_similar(similar_list, key_func, top_n: int = 30):
    """
    Sortuje listę krotek (index, similarity_score) na podstawie podanej funkcji klucza.

    Parameters
    ----------
    similar_list : list[tuple[int, float]]
        Lista krotek (index, similarity_score).
    key_func : callable
        Funkcja zwracająca klucz sortowania (np. lambda pair: pair[1]).
    top_n : int
        Liczba wyników do zwrócenia.

    Returns
    -------
    list[tuple[int, float]]
        Posortowana lista z pominięciem pierwszego elementu (bazowego).
    """
    sorted_list = sorted(similar_list, key=key_func, reverse=True)
    # Pomijamy pierwszy element, bo to sam film bazowy
    return sorted_list[1: top_n + 1]


def load_movies(path: str = "dataset/movies.csv"):
    """
    Wczytuje dane o filmach, buduje tekstową reprezentację i macierz podobieństwa TF‑IDF.

    Parameters
    ----------
    path : str
        Ścieżka do pliku CSV z danymi o filmach.

    Returns
    -------
    movies : pandas.DataFrame
        Dane o filmach z kolumną 'combined'.
    similarity : numpy.ndarray
        Macierz podobieństwa kosinusowego pomiędzy filmami.
    """
    movies = pd.read_csv(path)

    movies["title"] = movies["title"].fillna("")

    features = ["genres", "keywords", "tagline", "cast", "director"]
    for feature in features:
        movies[feature] = movies[feature].fillna("")

    # Połączenie wybranych kolumn w jeden ciąg tekstowy dla każdego filmu
    movies["combined"] = movies[features].agg(" ".join, axis=1)

    # TF‑IDF + podobieństwo kosinusowe
    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform(movies["combined"])
    similarity = cosine_similarity(vectors)

    return movies, similarity


def recommend_movie(
    movies: pd.DataFrame,
    similarity,
    movie_name: str,
    top_n: int = 10,
):
    """
    Rekomenduje filmy podobne do podanego na podstawie podobieństwa kosinusowego.

    Parameters
    ----------
    movies : pandas.DataFrame
        Dane o filmach (m.in. kolumna 'title').
    similarity : numpy.ndarray
        Macierz podobieństwa TF‑IDF (N x N).
    movie_name : str
        Nazwa filmu, dla którego mają zostać wygenerowane rekomendacje.
    top_n : int
        Liczba rekomendacji do zwrócenia.

    Returns
    -------
    base_title : str | None
        Tytuł filmu bazowego lub None, jeśli nie znaleziono.
    recommendations : list[str]
        Lista tytułów rekomendowanych filmów.
    """
    movie_name = movie_name.strip()
    if not movie_name:
        return None, []

    titles = movies["title"].fillna("")

    # Dopasowanie tytułu użytkownika do najbliższego istniejącego tytułu
    matches = get_close_matches(
        movie_name.lower(),
        titles.str.lower().tolist(),
        n=1,
        cutoff=0.7,
    )
    if not matches:
        return None, []

    match_lower = matches[0]
    idx = titles.str.lower().tolist().index(match_lower)
    base_title = movies.at[idx, "title"]

    # Lista (index, similarity_score) dla wszystkich filmów względem bazowego
    similar_movies = list(enumerate(similarity[idx]))

    # Bierzemy więcej kandydatów, żeby po filtrach nadal mieć top_n wyników
    best_matches = sort_similar(
        similar_movies,
        key_func=lambda pair: pair[1],
        top_n=top_n * 2,
    )

    seen_titles = set()
    results: list[str] = []

    for movie_idx, _ in best_matches:
        title = movies.at[movie_idx, "title"]

        if title == base_title:
            continue  # pomiń film bazowy

        if title in seen_titles:
            continue  # pomiń duplikaty

        seen_titles.add(title)
        results.append(title)

        if len(results) >= top_n:
            break

    return base_title, results
