"""
Główny silnik Machine Learning aplikacji (ML Engine).
Plik ten spina odseparowane usługi dla filmów i gier zlokalizowane w `core_logic`.
Działa jako jednolity punkt dostępu, do którego odwołują się routingi w celu wczytania macierzy
podobieństwa i uruchomienia procesów silnika rekomendacji modeli ML.
"""

import os
import numpy as np
from functools import lru_cache
from app.ml.core_logic.movies.tmdb_client import fetch_movie_details
from app.ml.core_logic.games.igdb_client import fetch_game_details
from app.ml.core_logic.movies.movie_recommender import load_movies
from app.ml.core_logic.games.game_recommender import load_games

# --- WCZYTANIE MODELI I DANYCH ---

# Filmy: TF-IDF
movies, movie_sim, movie_vectorizer = load_movies()

# Gry: SBERT
games, game_sim, game_model = load_games()

# --- MECHANIZM CACHE DLA SBERT ---
EMBEDDINGS_CACHE = os.path.join(os.path.dirname(__file__), '../../data/game_embeddings_cache.npy')

if os.path.exists(EMBEDDINGS_CACHE):
    print("--- Wczytywanie gotowych wektorów gier z pliku (szybki start)... ---")
    GAME_EMBEDDINGS = np.load(EMBEDDINGS_CACHE)
else:
    print("--- Pierwsze uruchomienie: Twój laptop generuje wektory. Poczekaj... ---")
    GAME_EMBEDDINGS = game_model.encode(
        games['combined'].tolist(), show_progress_bar=True)
    np.save(EMBEDDINGS_CACHE, GAME_EMBEDDINGS)
    print("--- Gotowe! Dane zapisane. ---")


# ---------- MAPY GATUNKÓW ----------

MOVIE_GENRES = {
    "Action": 28,
    "Comedy": 35,
    "Horror": 27,
    "Drama": 18,
    "Animation": 16,
}

GAME_GENRES = {
    "Action": 4,
    "RPG": 12,
    "Sports": 14,
}

PLATFORM_MAP = {
    6: "PC (Windows)",
    48: "PlayStation 4",
    49: "Xbox One",
    130: "Nintendo Switch",
    167: "PlayStation 5",
    169: "Xbox Series X|S",
    3: "Linux",
    14: "Mac",
    34: "Android",
    39: "iOS",
    509: "Nintendo Switch 2",
    508: "macOS",
}

# ---------- POMOCNICZE FUNKCJE CACHE ----------

@lru_cache(maxsize=1000)
def fetch_movie_details_cached(title):
    return fetch_movie_details(title)

@lru_cache(maxsize=1000)
def fetch_game_details_cached(title):
    return fetch_game_details(title)
