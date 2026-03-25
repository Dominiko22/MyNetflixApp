## 1. Architektura Przechowywania Danych

Żeby system działał szybko i sprawnie, korzystamy z dwóch typów magazynów danych:

- **SQLite:** Przechowuje profile użytkowników i informacje o tym, które tytuły mają w ulubionych.
    
- **CSV:** Zawiera wszystkie dane potrzebne do silnika rekomendacji, czyli opisy i gatunki filmów i gier. Dzięki temu Pandas może szybko robić obliczenia na wektorach.


## 2. Schemat Bazy Danych (Entity Relationship Diagram)

Baza danych działa na zasadzie **jeden-do-wielu (1:N)**. To znaczy, że jeden użytkownik może mieć wiele ulubionych filmów i gier przypisanych do swojego konta

```sql
erDiagram
    USER ||--o{ FAVORITE : "posiada"
    USER {
        int id PK
        string email UK
    }
    FAVORITE {
        int id PK
        int user_id FK
        string title
        string category "movie / game"
    }
```

## 3. Implementacja ORM (SQLAlchemy)

Do komunikacji z bazą danych wykorzystano **SQLAlchemy**. Dzięki temu nie trzeba pisać surowych zapytań SQL – można po prostu operować na obiektach Pythona, co jest wygodniejsze i czytelniejsze.

> [!INFO] Model Użytkownika
Jako unikalny identyfikator użytkownika system wykorzystuje `email`, który pobierany jest automatycznie z konta Google po zalogowaniu przez OAuth 2.0.

```Python
# Model danych w main.py
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # Relacja pozwalająca na wywołanie user.favorites
    favorites = db.relationship('Favorite', backref='owner', lazy=True)

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False) # 'movie' lub 'game'
```

## 4. Zarządzanie Danymi Statycznymi (CSV)

Dane potrzebne do działania silnika rekomendacji są wczytywane przy starcie aplikacji do obiektów `DataFrame` (Pandas). Dzięki temu system może szybko przetwarzać opisy i gatunki filmów i gier.

### 4.1. Struktura zbioru danych (Dataset Schema) 
Dane o filmach są przechowywane w pliku `movies.csv`. Poniżej pokazano przykładową strukturę i wyjaśnienie najważniejszych kolumn.

> [!EXAMPLE] Fragment pliku movies.csv
> | ID | Tytuł | Gatunki | Opis (Overview) | Głosy |
> | :--- | :--- | :--- | :--- | :--- |
> | 27205 | **Inception** | Action, Sci-Fi | A thief who steals corporate secrets through use of dream-sharing technology... | 34000 |
> | 157336 | **Interstellar** | Adventure, Drama | The adventures of a group of explorers who make use of a newly discovered wormhole... | 32000 |


> [!TIP] Spójność Danych
> Kolumna `title` w bazie SQL służy do łączenia danych z plikami CSV przy wyświetlaniu profilu użytkownika. Dzięki temu nie trzeba powielać opisów i okładek w bazie, co znacznie zmniejsza jej rozmiar.
## 5. Przykładowe Zapytania (Logic Flow)

### Pobieranie ulubionych filmów użytkownika:

```Python
# Pobranie obiektu użytkownika z bazy
current_user = User.query.filter_by(email=session_email).first()

# Wyciągnięcie tylko filmów z listy ulubionych
user_fav_movies = [fav for fav in current_user.favorites if fav.category == 'movie']
```

