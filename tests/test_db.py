import pytest
from unittest.mock import patch, MagicMock

from src.db import init_db, save_user_preference, get_user_preference

# Jeśli get_connection jest również eksportowane i używane gdzie indziej, można by je też testować,
# ale tutaj skupiamy się na funkcjach używających get_connection.


@pytest.fixture
def mock_db_environment(monkeypatch):
    """
    Mockuje zmienne środowiskowe, jeśli są one odczytywane na poziomie modułu w src.db.
    Ważne, jeśli `DB_HOST` itp. są definiowane globalnie w `src/db.py`.
    """
    monkeypatch.setenv("MYSQL_HOST", "mock_host")
    monkeypatch.setenv("MYSQL_DATABASE", "mock_db")
    monkeypatch.setenv("MYSQL_USER", "mock_user")
    monkeypatch.setenv("MYSQL_PASSWORD", "mock_pass")


@pytest.fixture
def mock_mysql_connector(
    monkeypatch, mock_db_environment
):  # Dodajemy mock_db_environment jako zależność
    """
    Kompleksowo mockuje mysql.connector.connect oraz zwracane przez nie obiekty połączenia i kursora.
    Ta fixtura będzie używana przez wszystkie testy w tym pliku.
    """
    mock_cursor_instance = MagicMock()
    mock_connection_instance = MagicMock()
    mock_connection_instance.cursor.return_value = mock_cursor_instance

    # Mockujemy `mysql.connector.connect` wewnątrz modułu `src.db`,
    # ponieważ to tam jest ono wywoływane przez funkcje takie jak `get_connection()`.
    mock_connect_function = MagicMock(return_value=mock_connection_instance)
    monkeypatch.setattr("src.db.mysql.connector.connect", mock_connect_function)

    # Zwracamy słownik z instancjami mocków, aby móc na nich wykonywać asercje w testach
    return {
        "connect_func": mock_connect_function,
        "connection_inst": mock_connection_instance,
        "cursor_inst": mock_cursor_instance,
    }


def test_init_db_creates_table_and_commits(mock_mysql_connector):
    """
    Testuje, czy init_db:
    1. Próbuje nawiązać połączenie.
    2. Uzyskuje kursor.
    3. Wykonuje zapytanie CREATE TABLE.
    4. Commituje transakcję.
    5. Zamyka kursor i połączenie.
    """
    init_db()  # Wywołujemy testowaną funkcję

    # Asercje na mockach
    mock_mysql_connector[
        "connect_func"
    ].assert_called_once()  # Czy mysql.connector.connect zostało wywołane
    # Można dodać asercje na argumenty wywołania connect_func, jeśli get_connection przekazuje konkretne wartości
    # np. mock_mysql_connector["connect_func"].assert_called_once_with(host="mock_host", ...)

    mock_mysql_connector["connection_inst"].cursor.assert_called_once()

    # Sprawdzenie wykonanego zapytania SQL
    executed_sql = mock_mysql_connector["cursor_inst"].execute.call_args[0][0]
    assert "CREATE TABLE IF NOT EXISTS user_preferences" in executed_sql
    assert "user_id VARCHAR(30) PRIMARY KEY" in executed_sql
    assert "favorite_genre VARCHAR(50) NOT NULL" in executed_sql

    mock_mysql_connector["connection_inst"].commit.assert_called_once()
    mock_mysql_connector["cursor_inst"].close.assert_called_once()
    mock_mysql_connector["connection_inst"].close.assert_called_once()


def test_save_user_preference_executes_correct_sql_and_commits(mock_mysql_connector):
    """
    Testuje, czy save_user_preference:
    1. Wykonuje poprawne zapytanie INSERT ... ON DUPLICATE KEY UPDATE.
    2. Przekazuje poprawne parametry (user_id, genre).
    3. Commituje transakcję.
    """
    test_user_id = "test_user_save"
    test_genre = "science-fiction"

    save_user_preference(test_user_id, test_genre)

    mock_mysql_connector["cursor_inst"].execute.assert_called_once()
    # call_args to krotka (args, kwargs), [0] to args (pozycyjne)
    # args[0] to pierwszy argument pozycyjny (SQL string)
    # args[1] to drugi argument pozycyjny (krotka z parametrami)
    executed_sql = mock_mysql_connector["cursor_inst"].execute.call_args[0][0]
    executed_params = mock_mysql_connector["cursor_inst"].execute.call_args[0][1]

    assert "INSERT INTO user_preferences (user_id, favorite_genre)" in executed_sql
    assert (
        "VALUES (%s, %s)" in executed_sql
    )  # lub jakiekolwiek placeholdery używa mysql.connector
    assert (
        "ON DUPLICATE KEY UPDATE favorite_genre = VALUES(favorite_genre)"
        in executed_sql
    )
    assert executed_params == (test_user_id, test_genre)

    mock_mysql_connector["connection_inst"].commit.assert_called_once()
    mock_mysql_connector["cursor_inst"].close.assert_called_once()
    mock_mysql_connector["connection_inst"].close.assert_called_once()


def test_get_user_preference_fetches_and_returns_genre_when_found(mock_mysql_connector):
    """
    Testuje, czy get_user_preference:
    1. Wykonuje poprawne zapytanie SELECT.
    2. Przekazuje poprawny user_id.
    3. Zwraca gatunek, jeśli rekord zostanie znaleziony.
    """
    test_user_id = "test_user_get_found"
    expected_genre = "thriller"

    # Konfigurujemy mock kursora, aby fetchone() zwróciło symulowany wiersz z bazy
    mock_mysql_connector["cursor_inst"].fetchone.return_value = (expected_genre,)

    actual_genre = get_user_preference(test_user_id)

    mock_mysql_connector["cursor_inst"].execute.assert_called_once_with(
        "SELECT favorite_genre FROM user_preferences WHERE user_id = %s",
        (test_user_id,),
    )
    mock_mysql_connector["cursor_inst"].fetchone.assert_called_once()
    assert actual_genre == expected_genre

    mock_mysql_connector["cursor_inst"].close.assert_called_once()
    mock_mysql_connector["connection_inst"].close.assert_called_once()


def test_get_user_preference_returns_none_when_not_found(mock_mysql_connector):
    """
    Testuje, czy get_user_preference:
    1. Wykonuje poprawne zapytanie SELECT.
    2. Zwraca None, jeśli rekord NIE zostanie znaleziony.
    """
    test_user_id = "test_user_get_not_found"

    # Konfigurujemy mock kursora, aby fetchone() zwróciło None (brak rekordu)
    mock_mysql_connector["cursor_inst"].fetchone.return_value = None

    actual_genre = get_user_preference(test_user_id)

    mock_mysql_connector["cursor_inst"].execute.assert_called_once_with(
        "SELECT favorite_genre FROM user_preferences WHERE user_id = %s",
        (test_user_id,),
    )
    mock_mysql_connector["cursor_inst"].fetchone.assert_called_once()
    assert actual_genre is None

    mock_mysql_connector["cursor_inst"].close.assert_called_once()
    mock_mysql_connector["connection_inst"].close.assert_called_once()
