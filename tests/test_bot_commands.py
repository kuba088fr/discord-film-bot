import pytest
import requests
from types import SimpleNamespace

from discord.ext import commands
from src.bot import bot, get_connection, _load_genres, BASE_URL, API_KEY


class DummyCtx:
    def __init__(self):
        # musimy instancjonować author jako obiekt z id i display_name
        self.author = type("A", (), {"id": 123, "display_name": "Tester"})()
        self.sent = None

    async def send(self, msg):
        self.sent = msg


@pytest.fixture(autouse=True)
def mock_db(monkeypatch):
    """Podmienia get_connection na dummy, żeby testować removefavorite."""

    class DummyCursor:
        queries = []

        def execute(self, q, args):
            DummyCursor.queries.append((q, args))

        def close(self):
            pass

    class DummyConn:
        def cursor(self):
            return DummyCursor()

        def commit(self):
            pass

        def close(self):
            pass

    monkeypatch.setattr("src.bot.get_connection", lambda: DummyConn())
    return DummyCursor


@pytest.mark.asyncio
async def test_hello():
    ctx = DummyCtx()
    await bot.get_command("hello").callback(bot, ctx)
    assert "Cześć Tester" in ctx.sent


@pytest.mark.asyncio
async def test_removefavorite(mock_db):
    ctx = DummyCtx()
    await bot.get_command("removefavorite").callback(bot, ctx)
    # sprawdzamy, że wykonano DELETE
    q, args = mock_db.queries[0]
    assert "DELETE FROM user_preferences" in q
    # i że bot wysłał właściwy komunikat
    assert "🗑️ Usunąłem Twój ulubiony gatunek" in ctx.sent


@pytest.mark.asyncio
async def test_listgenres(monkeypatch):
    # mockujemy listę gatunków
    monkeypatch.setattr("src.bot._load_genres", lambda: {"a": 1, "b": 2, "c": 3})
    ctx = DummyCtx()
    await bot.get_command("listgenres").callback(bot, ctx)
    assert "a, b, c" in ctx.sent


@pytest.mark.asyncio
async def test_search(monkeypatch):
    # fałszywa odpowiedź TMDB
    sample = {"results": [{"title": "TestMovie", "release_date": "2021-05-10"}]}
    monkeypatch.setattr(
        requests, "get", lambda url, params: SimpleNamespace(json=lambda: sample)
    )
    ctx = DummyCtx()
    # invoke callback with the named parameter 'query'
    await bot.get_command("search").callback(bot, ctx, query="foo")
    assert "TestMovie (2021)" in ctx.sent
