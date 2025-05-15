import os
import mysql.connector

DB_HOST = os.getenv("MYSQL_HOST")
DB_NAME = os.getenv("MYSQL_DATABASE")
DB_USER = os.getenv("MYSQL_USER")
DB_PASS = os.getenv("MYSQL_PASSWORD")

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id VARCHAR(30) PRIMARY KEY,
            favorite_genre VARCHAR(50) NOT NULL
        );
    """)
    conn.commit()
    c.close()
    conn.close()

def save_user_preference(user_id, genre):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO user_preferences (user_id, favorite_genre)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE favorite_genre = VALUES(favorite_genre);
    """, (user_id, genre))
    conn.commit()
    c.close()
    conn.close()

def get_user_preference(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT favorite_genre FROM user_preferences WHERE user_id = %s", (user_id,))
    row = c.fetchone()
    c.close()
    conn.close()
    return row[0] if row else None
