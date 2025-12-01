"""Algorytm rekomendacji gier na podstawie podobieństwa TF-IDF."""
from difflib import get_close_matches
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def sort_scores(scores_list, key_func, top_n=30):
    """
    Sortuje listę krotek (index, similarity_score) na podstawie podanej funkcji klucza.

    Parameters:
        scores_list (list): Lista krotek (index, similarity_score).
        key_func (callable): Funkcja zwracająca klucz sortowania.
        top_n (int): Liczba wyników do zwrócenia.

    Returns:
        list: Posortowana lista z pominięciem pierwszego elementu (bazowego).
    """
    sorted_list = sorted(scores_list, key=key_func, reverse=True)
    # Pominięcie pierwszego elementu (bazowego)
    return sorted_list[1: top_n + 1]


def load_games(path='dataset/games.csv'):
    """
    Wczytuje dane o grach, przetwarza tekst i oblicza macierz podobieństwa TF-IDF.

    Parameters:
        path (str): Ścieżka do pliku CSV z danymi o grach.

    Returns:
        tuple: (DataFrame z danymi o grach, macierz podobieństwa TF-IDF)
    """
    # Wczytanie danych z pliku CSV
    # Uzupełnienie brakujących wartości pustymi ciągami
    games = pd.read_csv(path).fillna('')
    # Usunięcie zbędnych spacji z nazw kolumn
    games.columns = games.columns.str.strip()
    games.reset_index(drop=True, inplace=True)

    # Połączenie wybranych kolumn w jeden ciąg tekstowy dla każdej gry
    features = ['title', 'genres', 'description', 'franchise', 'developer']
    games['combined'] = games[features].agg(' '.join, axis=1)

    # Obliczenie macierzy podobieństwa TF-IDF
    tfidf = TfidfVectorizer(max_features=5000, stop_words='english')
    similarity = cosine_similarity(tfidf.fit_transform(games['combined']))

    return games, similarity


def recommend_game(games, similarity, game_name, top_n=30):
    """
    Rekomenduje gry podobne do podanej na podstawie podobieństwa kosinusowego.

    Parameters:
        games (DataFrame): Dane o grach.
        similarity (ndarray): Macierz podobieństwa TF-IDF.
        game_name (str): Nazwa gry, dla której mają zostać wygenerowane rekomendacje.
        top_n (int): Liczba rekomendacji do zwrócenia.

    Returns:
        tuple: (znaleziony_tytuł, lista_rekomendacji)
    """
    game_name = game_name.strip()  # Usunięcie zbędnych spacji z nazwy gry
    if not game_name:
        return None, []  # Jeśli nazwa gry jest pusta, zwróć brak wyników

    # Wyszukiwanie gry w danych na podstawie tytułu
    titles = games['title'].astype(str)
    mask = titles.str.contains(game_name, case=False, regex=False)

    if mask.any():
        idx = mask.idxmax()  # Znalezienie indeksu pierwszego dopasowania
    else:
        # Próba znalezienia podobnych tytułów za pomocą `get_close_matches`
        matches = get_close_matches(
            game_name.lower(),
            titles.str.lower(),
            n=1,
            cutoff=0.7
        )
        if not matches:
            return None, []  # Jeśli brak dopasowań, zwróć brak wyników
        idx = titles.str.lower().tolist().index(matches[0])

    # Obliczenie podobieństwa dla znalezionego tytułu
    scores = list(enumerate(similarity[idx]))

    # Posortowanie wyników na podstawie podobieństwa
    best_scores = sort_scores(
        scores,
        key_func=lambda pair: pair[1],
        top_n=top_n
    )

    # Pobranie tytułów gier na podstawie posortowanych wyników
    results = [games.loc[game_idx, 'title'] for game_idx, _ in best_scores]

    return titles[idx], results
