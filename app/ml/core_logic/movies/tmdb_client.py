"""
Moduł klienta API TheMovieDatabase (TMDB).
Odpowiada za pobieranie obrazów (plakaty, tła) i detali filmu w czasie rzeczywistym
w odpowiedzi na zapytania z frontendu, cachując jednocześnie wyniki w pamięci modułu.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w342"

_movie_cache: dict[str, dict] = {}


def fetch_movie_details(title: str) -> dict | None:
    """Zwraca dane filmu z TMDB (pierwszy wynik) lub None."""
    if not TMDB_API_KEY:
        print("Brak klucza API TMDB.")
        return None

    # cache w pamięci
    if title in _movie_cache:
        return _movie_cache[title]

    params = {
        "api_key": TMDB_API_KEY,
        "query": title,
        "include_adult": "false",
        "language": "pl-PL",
    }

    try:
        response = requests.get(TMDB_SEARCH_URL, params=params, timeout=2)
        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])
        if not results:
            return None

        movie = results[0]
        poster_path = movie.get("poster_path")
        backdrop_path = movie.get("backdrop_path")
        
        if poster_path:
            movie["Poster"] = TMDB_IMAGE_BASE + poster_path
        else:
            movie["Poster"] = None
            
        if backdrop_path:
            movie["Backdrop"] = "https://image.tmdb.org/t/p/w1280" + backdrop_path
        else:
            movie["Backdrop"] = None

        _movie_cache[title] = movie
        return movie
    except requests.RequestException as e:
        print(f"Błąd podczas pobierania danych z TMDB: {e}")
        return None
