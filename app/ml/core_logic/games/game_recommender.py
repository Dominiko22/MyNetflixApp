"""
Algorytm rekomendacji gier silnika ML bazujący na architekturze App Factory.
Wykorzystuje model uczenia maszynowego SBERT i macierz dystansu kosinusowego do 
wyszukiwania i rekomendacji podobnych tytułów gier.
"""
from difflib import get_close_matches
import pandas as pd
import pickle
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


def sort_scores(scores_list, key_func, top_n=30):
    """
    Sortuje listę krotek (index, similarity_score) na podstawie podanej funkcji klucza i wybiera najlepsze wyniki.

    Zasada działania:
    1. Sortuje wyniki od najbardziej do najmniej podobnych (similarity_score od 1.0 do 0.0)
    2. Pomija pierwszy element [0], ponieważ jest do tytuł bazowy (jest zawsze w 100% (1.0:1.0) podobna do siebie, co jest bez sensu by to wypisywać)
    
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


def load_games(path=os.path.join(os.path.dirname(__file__), '../../../dataset/games.csv'), cache_path=os.path.join(os.path.dirname(__file__), '../../../data/similarity_cache.pkl')):
    """
    Wczytuje dane o grach, przetwarza tekst i oblicza macierz podobieństwa TF-IDF.

    Kluczowe kroki:
    1. Łączenie cech (combined): Tworzymy jedne długi opis dla każdej gry,
    np. "The Witcher 3 RPG fantasy open-world"
    2. TfidfVectroizer: Zamienia tekst na liczby. Nadaje niską wagę słowom powszechnie używanym np. "game", a wysoką unikalnym np. "cyberpunk"
    3. Cosine Similarity: Oblicza kąt między profilami gier w przestrzeni matematycznej.
    im mniejszy kąt, tym bardziej podobne gry.

    Parameters:
        path (str): Ścieżka do pliku CSV z danymi o grach.

    Returns:
        tuple: (DataFrame z danymi o grach, macierz podobieństwa TF-IDF)
    """
    # Wczytanie danych z pliku CSV
    games = pd.read_csv(path).fillna('')

    # Usunięcie zbędnych spacji z nazw kolumn
    games.columns = games.columns.str.strip()
    games.reset_index(drop=True, inplace=True)

    # Upewniamy się, że nowe kolumny istnieją (gdyby kiedyś czegoś brakowało)
    for col in ["genre", "pegi", "platform", "keyword", "multiplayer_mode", "release_date"]:
        if col not in games.columns:
            games[col] = ""

    # Połączenie wybranych kolumn w jeden ciąg tekstowy dla każdej gry
    text_features = ["title", "keyword", "genre", "summary", "storyline"]
    for col in text_features:
        if col not in games.columns:
            games[col] = ""

    games[text_features] = games[text_features].fillna("").astype(str)
    games["combined"] = games[text_features].agg(" ".join, axis=1)

    # Inteligentne obliczanie podobieńśtwa
    # Sprawdzamy, czy mamy już zapisaną macierz, żeby nie liczyć jej co chwile
    if os.path.exists(cache_path):
        print("Wczytywanie podobieństwa z pliku cache...")
        with open(cache_path, 'rb') as f:
            similarity = pickle.load(f)
        model = SentenceTransformer('all-MiniLM-L6-v2')
    else:
        print("Obliczanie wektorów SBERT (to może chwilę potrwać przy pierwszym uruchomieniu)...")
        # Ładujemy lekki i szybki model językowy
        model = SentenceTransformer('all-MiniLM-L6-v2')

        # Zamiana tekstu na "odciski palców" znaczenia (embeddings)
        embeddings = model.encode(games["combined"].tolist(), show_progress_bar=True)

        # Obliczam podobieństwo cosine
        similarity = cosine_similarity(embeddings)

        # Zapisuje do pliku na przywszłość
        with open(cache_path, 'wb') as f:
            pickle.dump(similarity, f)

    return games, similarity, model


def recommend_game(games, similarity, game_name, top_n=30):
    """
    Znajduje grę w bazie (nawet z literówką) i zwraca najbardziej podobne tytuły.

    Obsługa błędów:
    1. Jeśli użytkownik wpisze "Witcher", maska str.contains znajdzie pełny tytuł 
    2. Jeśli użytkownik zrobi bład "Wittcher", get_close_matches naprawi bład i znajdzie właściwy indeks.

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
