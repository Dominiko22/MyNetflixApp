"""
Skrypt narzędziowy (Generator).
Podobnie jak odpowiednik dla gier, służy do masowego pobierania informacji o filmach z TheMovieDatabase (TMDB).
Dane lądują w CSV i zasilają macierze TF-IDF podczas incjalizacji aplikacji.
"""

import os
from pathlib import Path
import csv
import requests
from dotenv import load_dotenv

# --- KONFIGURACJA ŚRODOWISKA ---

# Skrypt szuka pliku .env w katalogu nadrzędnym, aby pobrać klucz API TMDB
BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"

print("TMDB_API_KEY:", bool(TMDB_API_KEY))


def fetch_movies_page(endpoint: str, page: int = 1, language: str = "pl-PL"):
    """
    Pobiera pojedyńczą stronę wyników (zazwyczaj 20 filmów) z TMDB

    Argumenty:
        endpoint (str): Punkt końcowy API (np. '/movie/top_rated' lub '/movie/popualar')
        page (int): Numer strony do pobrania
        language(str): Język opisów (domyślnie polski)
    """
    url = f"{TMDB_BASE_URL}{endpoint}"
    params = {
        "api_key": TMDB_API_KEY,
        "language": language,
        "page": page,
    }
    resp = requests.get(url, params=params, timeout=5)
    resp.raise_for_status()
    return resp.json()


def dump_movies_to_csv(
    csv_path: str,
    total: int = 1000,
    per_page: int = 20,
    endpoint: str = "/movie/top_rated",
):
    """
    Głowna funkcja eksportująca: pobiera filmy strona po stronie i zapisuje je do pliuku CSV,

    Format wyjściowy:
    title, genres, overview, release_date, rating, vote_count

    Logika:
    1. Iteruje po stronach (page), dopóki nie zbierze wymaganej liczby 'total' filmów.
    2. Odfiltrowuje filmy z niską liczbą głosów (vote_count < 50), aby zachować jakość bazy.
    3. Czyśći opisy (overview) z enterów, by nie psuć formatu CSV.
    """
    fieldnames = ["title", "genres", "overview",
                  "release_date", "rating", "vote_count"]

    rows = []
    page = 1
    while len(rows) < total:
        print(f"Pobieram filmy: strona {page}")
        data = fetch_movies_page(endpoint=endpoint, page=page)
        results = data.get("results", [])
        if not results:
            break

        for m in results:
            title = m.get("title") or m.get("name")
            if not title:
                continue

            genre_ids = m.get("genre_ids") or []
            overview = m.get("overview") or ""
            release_date = m.get("release_date") or ""
            rating = m.get("vote_average") or ""   # poprawka: vote_average
            vote_count = m.get("vote_count") or 0

            # filtr na mało znane filmy, np. min. 50 głosów
            if vote_count < 50:
                continue

            rows.append(
                {
                    "title": title,
                    "genres": ",".join(str(g) for g in genre_ids),
                    "overview": overview.replace("\n", " ").strip(),
                    "release_date": release_date,
                    "rating": rating,
                    "vote_count": vote_count,
                }
            )
            if len(rows) >= total:
                break

        page += 1
        if page > data.get("total_pages", 1):
            break

    rows = rows[:total]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Zapisano {len(rows)} filmów do {csv_path}")


if __name__ == "__main__":
    """
    Uruchomienie skryptu: pobiera 5000 najlepiej ocenianych filmów.
    """
    dump_movies_to_csv("movies.csv", total=5000, per_page=20,
                       endpoint="/movie/top_rated")
