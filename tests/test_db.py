import pytest
from unittest.mock import patch, MagicMock

# Importuj funkcje, które chcesz testować z src.db
from src.db import init_db, save_user_preference, get_user_preference

@pytest.fixture
def mock_db_environment(monkeypatch):
    monkeypatch.setenv("MYSQL_HOST", "mock_host")
    monkeypatch.setenv("MYSQL_DATABASE", "mock_db")
    monkeypatch.setenv("MYSQL_USER", "mock_user")
    monkeypatch.setenv("MYSQL_PASSWORD", "mock_pass")

@pytest.fixture
def mock_mysql_connector(monkeypatch, mock_db_environment):
    mock_cursor_instance = MagicMock()
    mock_connection_instance = MagicMock()
    mock_connection_instance.cursor.return_value = mock_cursor_instance
    
    # Mockujemy `mysql.connector.connect` wewnątrz modułu `src.db`,
    # ponieważ to tam jest ono wywoływane przez funkcje takie jak `get_connection()`.
    mock_connect_function = MagicMock(return_value=mock_connection_instance)
    monkeypatch.setattr('src.db.mysql.connector.connect', mock_connect_function) # Poprawna ścieżka
    
    return {
        "connect_func": mock_connect_function,
        "connection_inst": mock_connection_instance,
        "cursor_inst": mock_cursor_instance
    }

def test_init_db_creates_table_and_commits(mock_mysql_connector):
    init_db()
    
    mock_mysql_connector["connect_func"].assert_called_once()
    mock_mysql_connector["connection_inst"].cursor.assert_called_once()
    
    executed_sql = mock_mysql_connector["cursor_inst"].execute.call_args[0][0]
    assert "CREATE TABLE IF NOT EXISTS user_preferences" in executed_sql
    assert "user_id VARCHAR(30) PRIMARY KEY" in executed_sql
    
    mock_mysql_connector["connection_inst"].commit.assert_called_once()
    mock_mysql_connector["cursor_inst"].close.assert_called_once()
    mock_mysql_connector["connection_inst"].close.assert_called_once()

def test_save_user_preference_executes_correct_sql_and_commits(mock_mysql_connector):
    test_user_id = "test_user_save"
    test_genre = "science-fiction"
    
    save_user_preference(test_user_id, test_genre)
    
    mock_mysql_connector["cursor_inst"].execute.assert_called_once()
    executed_sql = mock_mysql_connector["cursor_inst"].execute.call_args[0][0]
    executed_params = mock_mysql_connector["cursor_inst"].execute.call_args[0][1]
    
    assert "INSERT INTO user_preferences (user_id, favorite_genre)" in executed_sql
    assert "ON DUPLICATE KEY UPDATE favorite_genre = VALUES(favorite_genre)" in executed_sql
    assert executed_params == (test_user_id, test_genre)
    mock_mysql_connector["connection_inst"].commit.assert_called_once()

def test_get_user_preference_fetches_and_returns_genre_when_found(mock_mysql_connector):
    test_user_id = "test_user_get_found"
    expected_genre = "thriller"
    mock_mysql_connector["cursor_inst"].fetchone.return_value = (expected_genre,) 
    
    actual_genre = get_user_preference(test_user_id)
    
    mock_mysql_connector["cursor_inst"].execute.assert_called_once_with(
        "SELECT favorite_genre FROM user_preferences WHERE user_id = %s", (test_user_id,)
    )
    assert actual_genre == expected_genre

def test_get_user_preference_returns_none_when_not_found(mock_mysql_connector):
    test_user_id = "test_user_get_not_found"
    mock_mysql_connector["cursor_inst"].fetchone.return_value = None
    
    actual_genre = get_user_preference(test_user_id)
    
    mock_mysql_connector["cursor_inst"].execute.assert_called_once_with(
        "SELECT favorite_genre FROM user_preferences WHERE user_id = %s", (test_user_id,)
    )
    assert actual_genre is None