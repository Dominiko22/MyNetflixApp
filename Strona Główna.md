# Media Recommendation Engine: Architecture & Design

**Autor:** Dominik Osiński
**Wersja:** 1.0.0 (Produkcyjna)
**Stack Techniczny:** Python | Flask | Scikit-learn | SQLAlchemy | Google OAuth 2.0

## 🗺️ Mapa Dokumentacji (Nawigacja)

Aby dowiedzieć się więcej o technicznych aspektach projektu, przejdź do odpowiednich sekcji:

- [[Specyfikacja Algorytmu Rekomendacji]] – Szczegółowy opis TF-IDF i Cosine Similarity.
    
- [[Model Danych i Baza SQL]] – Struktura tabel użytkowników i ulubionych.
    
- [[Integracje API i Proces ETL]] – Jak pobieramy dane z TMDB i IGDB.
    
- [[Instrukcja Uruchomienia]] – Konfiguracja środowiska i zmiennych `.env`.
- [[Autentykacja i Zarządzanie Użytkownikiem]] – Szczegóły implementacji Google OAuth 2.0, zabezpieczenia sesji i modelu User.
- [[Architektura Systemowa]] - Wysokopoziomowy schemat powiązań między modułami oraz opis przepływu danych (Data Flow).
## 1. Wprowadzenie i Cel Projektu

System jest stworzony jako inteligentny asystent do wybierania filmów i gier. Wykorzystuje techniki **Przetwarzania Języka Naturalnego (NLP)** żeby analizować opisy fabuły i na tej podstawie dobierać podobne tytuły.

> [!ABSTRACT] Problem do rozwiązania 
> W dzisiejszych czasach dostępnych jest tyle filmów i gier, że łatwo się pogubić i nie wiedzieć, co wybrać („paraliż decyzyjny”). Zwykłe wyszukiwarki oparte na tagach często zawodzą, bo nie oddają klimatu produkcji. Nasz system pomaga to obejść, łącząc tytuły na podstawie ich fabuły, a nie tylko słów-kluczy.


## 2. Architektura Systemu (High-Level)
Aplikacja opiera się na trzech filarach, które gwarantują jej stabilność i szybkość:
### 🎯 Celność (Precision)

W sercu systemu jest **TF-IDF**, który analizuje opisy filmów i gier i zamienia je na „profile” wektorowe. Dzięki temu algorytm wyłapuje ważne motywy, np. „dystopia” czy „relacje rodzinne”, a jednocześnie ignoruje zbędny szum w opisach.
### 🛡️ Bezpieczeństwo (Security)

Logowanie odbywa się przez **Google OAuth 2.0**, więc użytkownicy mogą bezpiecznie zarządzać swoimi ulubionymi tytułami bez zakładania nowego konta. System nie przechowuje haseł ani innych wrażliwych danych.
### ⚡ Skalowalność i Wydajność (Performance)

System działa na hybrydowym modelu danych:

- **Dane statyczne (CSV):** Baza ponad 5000 tytułów ładowana jest do pamięci przy starcie serwera, więc wyniki są dostępne niemal od razu.
    
- **Dane dynamiczne (API):** Plakaty i szczegóły są pobierane w czasie rzeczywistym z TMDB (filmy) i IGDB (gry), co odciąża serwer i przyspiesza działanie systemu.

## 3. Kluczowe Funkcjonalności

- **Hybrydowy Silnik:** Rekomendacje dla dwóch różnych mediów (filmy i gry) w jednej aplikacji.
    
- **Fuzzy Search:** Odporność na literówki w nazwach tytułów dzięki algorytmom dopasowania rozmytego.
    
- **Personalizacja:** Możliwość budowania własnej bazy ulubionych tytułów powiązanej z profilem Google.

