"""
Moduł klienta API do komunikacji z bazą IGDB (Internet Game Database).
Służy do pozyskiwania szczegółowych danych o pojedynczych grach "w locie" (np. okładki, artworki)
wymaganych przez moduł Views do wyświetlenia karty produktu.
"""

import os
from pathlib import Path

import requests
from dotenv import load_dotenv

# --- KONFIGURACJA ŚRODOWISKA --- 
# Skrypt wczytuje poświadczenia IGDB z pluku .env
BASE_DIR = Path(__file__).resolve().parents[3]
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)

IGDB_CLIENT_ID = os.getenv("IGDB_CLIENT_ID")
IGDB_ACCESS_TOKEN = os.getenv("IGDB_ACCESS_TOKEN")

IGDB_GAMES_URL = "https://api.igdb.com/v4/games"
IGDB_IMAGE_BASE = "https://images.igdb.com/igdb/image/upload/"

_game_cache: dict[str, dict] = {}

HEADERS = {
    "Client-ID": IGDB_CLIENT_ID,
    "Authorization": f"Bearer {IGDB_ACCESS_TOKEN}",
    "Content-Type": "application/json",
}


def fetch_game_details(title: str) -> dict | None:
    """
    Wyszukuje grę w API IGDB po tytule i zwraca jej szczegóły wraz z linkiem do okładki.

    Proces:
    1. Sprawdza czy wynik jest już w lokalnym cache (_game_cache)/
    2. Wysyła zapytanie tpuy 'search', ograniczając wynik do 1 najlepiej dopasowanej gry.
    3. Pobiera 'image_id' okładki i zamienia je na pełny adres URL (rozmiar t_cover_big).

    Zwraca:
        dict: Słownik z danymi gry (name, summary, storyline, Poster) lub None w przypadku błędu.
    """
    if not IGDB_CLIENT_ID or not IGDB_ACCESS_TOKEN:
        print("Brak danych do IGDB API (games).")
        return None

    # Sprawdzenie pamięci podręcznej
    if title in _game_cache:
        return _game_cache[title]

    # Budowanie kwerendy: szukamy nazwy, opisów oraz ID okładki, artworków i screenshotów dla podanego tytułu
    query = f'fields name, summary, storyline, cover.image_id, artworks.image_id, screenshots.image_id; search "{title}"; limit 1;'

    try:
        resp = requests.post(
            IGDB_GAMES_URL, headers=HEADERS, data=query, timeout=2)
        resp.raise_for_status()
        games = resp.json()
        if not games:
            print("Nie znaleziono gry o podanym tytule.")
            return None

        game = games[0]

        cover = game.get("cover") or {}
        image_id = cover.get("image_id")

        if image_id:
            game["Poster"] = f"{IGDB_IMAGE_BASE}t_cover_big/{image_id}.jpg"
        else:
            game["Poster"] = None
            
        artworks = game.get("artworks", [])
        screenshots = game.get("screenshots", [])
        
        backdrop_id = None
        if artworks and isinstance(artworks, list) and len(artworks) > 0:
            backdrop_id = artworks[0].get("image_id")
        elif screenshots and isinstance(screenshots, list) and len(screenshots) > 0:
            backdrop_id = screenshots[0].get("image_id")
            
        if backdrop_id:
            game["Backdrop"] = f"{IGDB_IMAGE_BASE}t_1080p/{backdrop_id}.jpg"
        else:
            game["Backdrop"] = None

        _game_cache[title] = game
        return game
    except requests.RequestException as e:
        print(f"IGDB game error: {e}")
        return None


if __name__ == "__main__":
    """
    Szybki test modułu: sprawdza, czy API poprawnie zwraca dane dla popularnego tytułu.
    """
    test_game = "Fortnite Battle Royale"
    result = fetch_game_details(test_game)
    if result:
        print(f"Znaleziono: {result['name']}")
        print(f"Link do plakatu: {result['Poster']}")
