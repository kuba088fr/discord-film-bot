# 🎬 Discord Film Bot

**Discord Film Bot** to lekki i elastyczny bot na Discorda napisany w Pythonie, który pozwala użytkownikom:
- zapisać swój ulubiony gatunek filmowy,
- otrzymać losową rekomendację filmu z serwisu TheMovieDB (TMDB),
- przechowywać preferencje w bazie MySQL.

---

## 📂 Struktura projektu

bot-discord-filmowy/
├── .env
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── README.md
├── src/
│   ├── bot.py
│   ├── db.py
│   └── movie_api.py
└── tests/
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
/recommend


✅ Testy
Projekt zawiera co najmniej trzy testy jednostkowe (w tym jeden z mockiem). Aby je uruchomić, wykonaj:
pytest --maxfail=1 --disable-warnings -q
black --check .
pytest – uruchamia testy w folderze tests/.

black --check – weryfikuje zgodność z formatowaniem kodu.

🔄 CI/CD (GitHub Actions)
W katalogu .github/workflows/ci-cd.yml znajduje się gotowy pipeline:

Testy (pytest + black)

Build (Docker build i opcjonalny push do rejestru)

Deploy (SSH + Docker Compose lub inny sposób)

Pipeline jest wyzwalany przy pushu do gałęzi main lub manualnie przez workflow_dispatch z opcjami:

build_image: true|false

operation: install|uninstall|reinstall

Sekrety (DISCORD_TOKEN, TMDB_API_KEY) przechowujemy w ustawieniach repozytorium.

📄 Plik .gitignore
.gitignore to lista wzorców plików i folderów, których Git nie będzie śledzić. Dzięki temu w repozytorium nie znajdą się:

pliki tymczasowe Pythona (__pycache__/, *.pyc, *.pyo)

lokalne sekretne pliki (.env)

dane Dockera i logi (mysql-data/, *.log)

ustawienia edytora (.vscode/, .idea/)

artefakty CI/CD

Przykładowa zawartość .gitignore:

gitignore
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

# GitHub Actions artifacts
.github/actions-artifacts/
