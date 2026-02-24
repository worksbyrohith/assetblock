"""
process.py — Initializes the AssetBlock PostgreSQL database.
Run this ONCE before starting the app: python src/process.py
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
from pathlib import Path
import os

_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)

USER = os.getenv("POSTGRE_USER", "postgres")
PASSWORD = os.getenv("POSTGRE_PASSWORD", "")
HOST = os.getenv("POSTGRE_HOST", "localhost")
PORT = os.getenv("POSTGRE_PORT", "5432")
DB = os.getenv("POSTGRE_DB", "assetblock")


def create_database():
    """Create the assetblock database if it doesn't exist."""
    conn = psycopg2.connect(
        user=USER, password=PASSWORD, host=HOST, port=PORT, database="postgres"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB}'")
    exists = cur.fetchone()
    if not exists:
        cur.execute(f"CREATE DATABASE {DB}")
        print(f"✅ Database '{DB}' created.")
    else:
        print(f"ℹ️  Database '{DB}' already exists.")
    cur.close()
    conn.close()


def create_tables():
    """Create all required tables."""
    conn = psycopg2.connect(
        user=USER, password=PASSWORD, host=HOST, port=PORT, database=DB
    )
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          SERIAL PRIMARY KEY,
            uid         VARCHAR(128) UNIQUE NOT NULL,
            email       VARCHAR(255) UNIQUE NOT NULL,
            username    VARCHAR(100),
            role        VARCHAR(20) DEFAULT 'client',
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id          SERIAL PRIMARY KEY,
            asset_name  VARCHAR(255) NOT NULL,
            hash        VARCHAR(64) UNIQUE NOT NULL,
            file_type   VARCHAR(50),
            file_size   BIGINT DEFAULT 0,
            description TEXT DEFAULT '',
            status      VARCHAR(20) DEFAULT 'Active',
            owner_uid   VARCHAR(128) REFERENCES users(uid) ON DELETE SET NULL,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS transfer_history (
            id              SERIAL PRIMARY KEY,
            asset_id        INTEGER REFERENCES assets(id) ON DELETE CASCADE,
            from_uid        VARCHAR(128),
            to_uid          VARCHAR(128),
            from_email      VARCHAR(255),
            to_email        VARCHAR(255),
            transferred_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            note            TEXT DEFAULT ''
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS activity_log (
            id          SERIAL PRIMARY KEY,
            uid         VARCHAR(128),
            email       VARCHAR(255),
            action      VARCHAR(100),
            details     TEXT DEFAULT '',
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ All tables created successfully.")


if __name__ == "__main__":
    print("🔧 Initializing AssetBlock database...")
    create_database()
    create_tables()
    print("\n🚀 Database ready! You can now start the application.")
    print("   Run: uvicorn api:app --reload  (from inside /src)")
