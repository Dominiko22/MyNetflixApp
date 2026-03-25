"""
Skrypt narzędziowy (Generator).
Służy do masowego pobierania danych o grach z API IGDB i zapisywania ich do lokalnego pliku CSV.
Działa poza głównym rygorem aplikacji Flask - używany do cyklicznej budowy bazy uczącej modele.
"""

import os
from pathlib import Path
import csv
import requests
from dotenv import load_dotenv


# --- KONFIGRUACJA ŚRODOWISKA ---

# skrypt szuka pliuku .env dwa poziomy wyżej, aby pobrać dane logowania do API IGDB
BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)

IGDB_CLIENT_ID = os.getenv("IGDB_CLIENT_ID")
IGDB_ACCESS_TOKEN = os.getenv("IGDB_ACCESS_TOKEN")

IGDB_GAMES_URL = "https://api.igdb.com/v4/games"

print("IGDB_CLIENT_ID:", IGDB_CLIENT_ID)
print("IGDB_ACCESS_TOKEN:", bool(IGDB_ACCESS_TOKEN))

# Nagłówki wymagane przed Twitch/IGDB API do autoryzacji zapytań
HEADERS = {
    "Client-ID": IGDB_CLIENT_ID,
    "Authorization": f"Bearer {IGDB_ACCESS_TOKEN}",
    "Content-Type": "application/json",
}


def fetch_games_batch(limit: int = 500, offset: int = 0):
    """
    Pobiera pojedyńczą paczkę danych z API IGDB przy użyciu języka zapytań Apicalypse.

    Argumenty:
        limit (int): Liczba gier do pobrania w jednym zapytaniu (max 500)
        offset (int): Punkt startowy (używany do stronicowania wyników)

    Komenda (query):
        - fields: wybiera konkretne dane (id gatunków, platformy, oceny, opisy).
        - where: filtruje tylko gry, które mają więcej niż 50 ocen (odsiewa "śmieci")
        - sort: ustawia kolejność od najlepiej oceniancych.
    """
    query = (
        "fields name, genres, keywords, platforms, multiplayer_modes, "
        "first_release_date, storyline, summary, total_rating, total_rating_count;"
        " where total_rating_count > 50 & total_rating != null;"
        " sort total_rating desc;"
        f" limit {limit};"
        f" offset {offset};"
    )

    resp = requests.post(IGDB_GAMES_URL, headers=HEADERS,
                         data=query, timeout=5)
    resp.raise_for_status()
    return resp.json()


def dump_games_to_csv(csv_path: str, total: int = 1000, batch_size: int = 500):
    """
    Głowna funkcja procesora: pobiera dane w pętli i zapisuje je do pliku CSV.

    Proces:
    1. Pobiera gry w "paczkach" (batch), dopóki nie osiągnie limitu 'total'\
    2. Mapuje zagnieżdzone listy (np. gatunki [1, 4, 21] na ciągi tekstowe oddzielone przecinkami)
    3. Czyści opisy (storyline) ze znakówn nowej linii, aby nie zepsuć struktury CSV.
    4. Zapisuje gotową listę słowników do pliku za pomocą DictWriter.
    """
    fieldnames = [
        "title",
        "genre",
        "platform",
        "keyword",
        "multiplayer_mode",
        "release_date",
        "storyline",
        "total_rating",
        "total_rating_count",
    ]

    rows = []
    offset = 0

    while offset < total:
        print(f"Pobieram gry: offset={offset}")
        batch = fetch_games_batch(limit=batch_size, offset=offset)
        if not batch:
            break

        for g in batch:
            title = g.get("name")
            if not title:
                continue

            genres = g.get("genres") or []
            platforms = g.get("platforms") or []
            keywords = g.get("keywords") or []
            multiplayer = g.get("multiplayer_modes") or []
            first_release = g.get("first_release_date")
            storyline = g.get("storyline") or g.get("summary") or ""
            total_rating = g.get("total_rating") or ""
            total_rating_count = g.get("total_rating_count") or ""

            rows.append({
                "title": title,
                "genre": ",".join(str(x) for x in genres),
                "platform": ",".join(str(x) for x in platforms),
                "keyword": ",".join(str(x) for x in keywords),
                "multiplayer_mode": ",".join(str(x) for x in multiplayer),
                "release_date": first_release or "",
                "storyline": storyline.replace("\n", " ").strip(),
                "total_rating": total_rating,
                "total_rating_count": total_rating_count,
            })

        offset += batch_size
        if len(rows) >= total:
            break

    rows = rows[:total]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Zapisano {len(rows)} gier do {csv_path}")


if __name__ == "__main__":
    # Uruchomienie skryptu.
    # Domyślnie pobiera 5000 najpopularniejszych gier, co stanowi solidną bazę
    # dla silnika rekomendacji.
    dump_games_to_csv("games.csv", total=5000, batch_size=500)
