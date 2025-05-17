# 🎬 Discord Film Bot

**Discord Film Bot** to lekki i elastyczny bot na Discorda napisany w Pythonie, który pozwala użytkownikom:
- zapisać swój ulubiony gatunek filmowy,
- otrzymać losową rekomendację filmu z serwisu TheMovieDB (TMDB),
- przechowywać preferencje w bazie MySQL.

---

## 📂 Struktura projektu

bot-discord-filmowy/
├── .env # Twoje lokalne zmienne środowiskowe (gitignore)
├── .gitignore # Pliki/foldery ignorowane przez Git
├── docker-compose.yml # Definicja usług: MySQL + bot
├── Dockerfile # Budowanie obrazu dockera dla bota
├── requirements.txt # Zależności Pythona
├── README.md # Ta dokumentacja
├── src/ # Kod źródłowy
│ ├── bot.py # Definicja komend i eventów bota
│ ├── db.py # Obsługa MySQL (init, save, get)
│ └── movie_api.py # Komunikacja z TMDB, pobieranie rekomendacji
└── tests/ # Testy jednostkowe
├── test_db.py
├── test_movie_api.py
└── test_bot_commands.py

## ⚙️ Instalacja i uruchomienie lokalne

1. **Sklonuj repozytorium** i przejdź do katalogu:
   ```bash
   git clone https://github.com/TwojUser/discord-film-bot.git
   cd discord-film-bot
Utwórz plik .env (dodaj go do .gitignore) z następującą zawartością:

DISCORD_TOKEN=TwójDiscordTokenZDeveloperPortal
TMDB_API_KEY=TwójTMDBv3APIKey
MYSQL_HOST=mysql
MYSQL_DATABASE=botdb
MYSQL_USER=botuser
MYSQL_PASSWORD=botpassword
Zbuduj i uruchom wszystkie usługi w Dockerze:


docker-compose up -d --build
Sprawdź logi bota:


docker-compose logs -f bot
Po chwili powinieneś zobaczyć:


Przetestuj komendy na Discordzie:

/hello
/setfavorite <gatunek>
/listgenres
/search <fraza>
/recommend
/removefavorite
/help


✅ Testy
Projekt zawiera testy jednostkowe i integracyjne:

test_db.py – sprawdza moduł bazy danych z mockiem MySQL
test_movie_api.py – weryfikuje pobieranie i cache’owanie gatunków oraz selekcję filmu
test_bot_commands.py – testuje logikę komend bota z użyciem fixture i mocków

Uruchom wszystkie testy i linter:
pip install -r requirements.txt pytest pytest-asyncio black
pytest --maxfail=1 --disable-warnings -q
black --check .

🔄 CI/CD (GitHub Actions)
W katalogu .github/workflows/ci-cd.yml przygotowany jest pipeline:
test
checkout kodu
instalacja zależności
black --check
pytest
build (jeśli testy przeszły)
docker build
logowanie do GHCR
docker push
deploy (na VM przez SSH)
docker-compose pull && docker-compose up -d
Workflow uruchamiany przy pushu do main lub ręcznie (workflow_dispatch) z opcjami:
build_image: true|false
operation: install|uninstall|reinstall

Sekrety w ustawieniach repozytorium (Settings → Secrets and variables):
DISCORD_TOKEN
TMDB_API_KEY
MYSQL_HOST, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD
CR_PAT (Personal Access Token do GHCR, jeśli używasz PAT zamiast GITHUB_TOKEN)
AZURE_VM_IP, SSH_PRIVATE_KEY, SSH_KNOWN_HOSTS (do deploya przez SSH)


📄 Plik .gitignore
.gitignore to lista wzorców plików i folderów, których Git nie będzie śledzić. Dzięki temu w repozytorium nie znajdą się:

pliki tymczasowe Pythona (__pycache__/, *.pyc, *.pyo)

lokalne sekretne pliki (.env)

dane Dockera i logi (mysql-data/, *.log)

ustawienia edytora (.vscode/, .idea/)

artefakty CI/CD

Przykładowa zawartość .gitignore:

# Python
__pycache__/
*.py[cod]
*.env

# Docker
mysql-data/
*.log

# IDE
.vscode/
.idea/

# GitHub Actions
.github/actions-artifacts/

📜 Komendy bota
Komenda	Opis
/hello	Testowa – czy bot online
/setfavorite <gatunek>	Ustawia lub aktualizuje ulubiony gatunek
/removefavorite	Usuwa ulubiony gatunek z bazy
/listgenres	Wyświetla listę wszystkich dostępnych gatunków
/search <fraza>	Wyszukuje filmy po tytule (top 5 wyników)
/recommend	Losowa rekomendacja na podstawie zapisanych preferencji
/help	Pokazuje tę listę komend i krótki opis

🔒 Bezpieczeństwo
Sekrety trzymamy w .env lokalnie i w GitHub Secrets – nigdy nie commitujemy tokenów do repozytorium.

Używamy PAT z zakresem write:packages do publikowania obrazów, albo nadajemy packages: write dla GITHUB_TOKEN.

Przy deployu SSH w SSH_KNOWN_HOSTS przechowujemy odcisk serwera, by zapobiec atakom typu MITM.
