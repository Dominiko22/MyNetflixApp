"""Klient TMDB do pobierania szczegółów filmu po tytule."""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w342"


def fetch_movie_details(title: str) -> dict | None:
    """Zwraca dane filmu z TMDB (pierwszy wynik) lub None."""
    if not TMDB_API_KEY:
        return None

    params = {
        "api_key": TMDB_API_KEY,
        "query": title,
    }

    try:
        response = requests.get(TMDB_SEARCH_URL, params=params, timeout=5)
        data = response.json()

        results = data.get("results", [])
        if not results:
            return None

        movie = results[0]
        poster_path = movie.get("poster_path")
        if poster_path:
            movie["Poster"] = TMDB_IMAGE_BASE + poster_path

        return movie
    except requests.RequestException as e:
        print(f"Błąd podczas pobierania danych z TMDB: {e}")
        return None
