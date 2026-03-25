## 1. Źródła Danych (Data Sources)

System korzysta z dwóch popularnych źródeł w branży rozrywkowej:

- **TMDB API (The Movie Database):** Metadane o filmach, opisy fabuły, oceny i plakaty.
    
- **IGDB API (Twitch/Internet Game Database):** Informacje o grach, w tym streszczenia i okładki.

## 2. Architektura Procesu ETL

Przygotowanie danych odbywa się w trzech krokach, żeby wszystko było spójne i gotowe do rekomendacji.
### 🟢 E - Extract (Pobieranie)

Skrypty `generate_movies.py` oraz `generate_games.py` odpytują API o najpopularniejsze tytuły, np. filmy z oceną > 7 i dużą liczbą głosów.

### 🟡 T - Transform (Przetwarzanie)

Surowe dane w JSON są przekształcane tak, żeby silnik ML mógł je wykorzystać:

- **Czyszczenie:** Usuwamy rekordy bez opisu fabuły.
    
- **Normalizacja:** Łączenie gatunków w jeden ciąg znaków (string).
    
- **Konkatenacja:** Tworzenie kolumny `combined`, która łączy gatunki i opis fabuły – łatwiej potem liczyć wektory TF-IDF.
    

### 🔵 L - Load (Ładowanie)

Gotowe ramki danych (DataFrames) zapisujemy do plików CSV, które służą jako lokalna baza dla aplikacji Flask.


## 3. Implementacja Techniczna (Python)

### Przykładowe pobieranie danych z TMDB:

```Python
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

def fetch_popular_movies(pages=5):
    all_movies = []
    for page in range(1, pages + 1):
        url = f"https://api.themoviedb.org/3/movie/top_rated?api_key={API_KEY}&page={page}"
        response = requests.get(url).json()
        all_movies.extend(response['results'])
    return all_movies
```

Przetwarzanie danych w Pandas:

```Python
import pandas as pd

def clean_data(raw_list):
    df = pd.DataFrame(raw_list)
    # Wybór tylko potrzebnych kolumn
    df = df[['id', 'title', 'genre_ids', 'overview', 'vote_count']]
    # Usuwanie braków
    df.dropna(subset=['overview'], inplace=True)
    return df
```

## 4. Bezpieczeństwo i Konfiguracja

Wszystkie klucze API są przechowywane w pliku środowiskowym `.env`. **Nigdy nie są one przesyłane do repozytorium GitHub.**

> [!WARNING] Plik .env 
> Upewnij się, że plik `.gitignore` zawiera linię `.env`. Wyciek klucza API może prowadzić do zablokowania dostępu do usług TMDB/IGDB.

> [!INFO] Dynamiczne pobieranie okładek 
> System nie przechowuje grafik lokalnie. Pobiera jedynie ścieżki (path) do plików, a finalne obrazy są renderowane przez front-end bezpośrednio z serwerów CDN dostawców API: `https://image.tmdb.org/t/p/w500/{poster_path}`