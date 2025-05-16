# tests/test_bot_commands.py
import pytest
import requests
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

# Poprawny import - importujemy TYLKO instancję bota
from src.bot import bot  # Zakładamy, że 'bot' to Twoja instancja commands.Bot


class DummyCtx:
    def __init__(self, author_id=123, author_display_name="Tester"):
        self.author = type(
            "Author", (), {"id": author_id, "display_name": author_display_name}
        )()
        self.sent_messages = []

    async def send(self, msg):
        self.sent_messages.append(msg)

    @property
    def last_sent_message(self):
        return self.sent_messages[-1] if self.sent_messages else None


@pytest.fixture
def mock_db_connection_for_bot_commands(monkeypatch):
    mock_cursor_instance = MagicMock()
    mock_connection_instance = MagicMock()
    mock_connection_instance.cursor.return_value = mock_cursor_instance
    monkeypatch.setattr(
        "src.bot.get_connection", MagicMock(return_value=mock_connection_instance)
    )
    return {"conn": mock_connection_instance, "cursor": mock_cursor_instance}


@pytest.mark.asyncio
async def test_hello():
    ctx = DummyCtx(author_display_name="Kuba")
    await bot.get_command("hello").callback(ctx)
    assert f"Hello {ctx.author.display_name}! I am ready!" in ctx.last_sent_message


@pytest.mark.asyncio
@patch("src.bot.save_user_preference")
async def test_setfavorite(mock_save_user_preference):
    ctx = DummyCtx()
    test_genre = "action"
    await bot.get_command("setfavorite").callback(ctx, genre=test_genre)
    mock_save_user_preference.assert_called_once_with(
        str(ctx.author.id), test_genre.lower()
    )
    assert (
        f"✅ Your favorite genre has been set to: **{test_genre}**"
        in ctx.last_sent_message
    )


@pytest.mark.asyncio
async def test_removefavorite(mock_db_connection_for_bot_commands):
    ctx = DummyCtx()
    await bot.get_command("removefavorite").callback(ctx)
    mock_db_connection_for_bot_commands["cursor"].execute.assert_called_once_with(
        "DELETE FROM user_preferences WHERE user_id = %s", (str(ctx.author.id),)
    )
    mock_db_connection_for_bot_commands["conn"].commit.assert_called_once()
    assert (
        "🗑️ Your favorite genre has been removed. Set a new one using `/setfavorite <genre>`."
        in ctx.last_sent_message
    )


@pytest.mark.asyncio
@patch("src.bot._load_genres")
async def test_listgenres(mock_internal_load_genres):
    ctx = DummyCtx()
    mock_internal_load_genres.return_value = {"action": 1, "comedy": 2, "drama": 3}
    await bot.get_command("listgenres").callback(ctx)
    assert "🎞️ Supported genres:" in ctx.last_sent_message
    assert "action, comedy, drama" in ctx.last_sent_message


@pytest.mark.asyncio
@patch("src.bot.get_user_preference")
@patch("src.bot.get_random_movie")
async def test_recommend_with_preference(
    mock_get_random_movie, mock_get_user_preference
):
    ctx = DummyCtx()
    user_favorite_genre = "fantasy"
    recommended_movie_details = "Fantasy Movie (2023) - An epic adventure."
    mock_get_user_preference.return_value = user_favorite_genre
    mock_get_random_movie.return_value = recommended_movie_details
    await bot.get_command("recommend").callback(ctx)
    mock_get_user_preference.assert_called_once_with(str(ctx.author.id))
    mock_get_random_movie.assert_called_once_with(user_favorite_genre)
    assert (
        f"🎬 Recommendation for **{user_favorite_genre}**: {recommended_movie_details}"
        in ctx.last_sent_message
    )


@pytest.mark.asyncio
@patch("src.bot.get_user_preference")
async def test_recommend_no_preference(mock_get_user_preference):
    ctx = DummyCtx()
    mock_get_user_preference.return_value = None
    await bot.get_command("recommend").callback(ctx)
    mock_get_user_preference.assert_called_once_with(str(ctx.author.id))
    assert (
        "⚠️ Please set a favorite genre first using `/setfavorite <genre>`."
        in ctx.last_sent_message
    )


@pytest.mark.asyncio
@patch("requests.get")
async def test_search_api_mocked(mock_requests_get):
    ctx = DummyCtx()
    query = "Inception"
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "results": [
            {"title": "Inception", "release_date": "2010-07-16"},
            {"title": "Inception: The Cobol Job", "release_date": "2010-12-07"},
        ]
    }
    mock_requests_get.return_value = mock_response
    await bot.get_command("search").callback(ctx, query=query)
    mock_requests_get.assert_called_once()
    assert "🔍 Top 5 results:" in ctx.last_sent_message
    assert "Inception (2010)" in ctx.last_sent_message
    assert "Inception: The Cobol Job (2010)" in ctx.last_sent_message
