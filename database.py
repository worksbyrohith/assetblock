"""
database.py — PostgreSQL connection helper for AssetBlock.
Supports both DATABASE_URL (Supabase/Render) and individual env vars.
"""

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from pathlib import Path
import os

# Resolve .env from project root (one level above src/)
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)


def get_connection():
    # Prefer DATABASE_URL if provided (Supabase, Render, etc.)
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return psycopg2.connect(database_url, sslmode="require")

    # Fallback to individual env vars (local dev)
    return psycopg2.connect(
        user=os.getenv("POSTGRE_USER", "postgres"),
        password=os.getenv("POSTGRE_PASSWORD", ""),
        host=os.getenv("POSTGRE_HOST", "localhost"),
        port=os.getenv("POSTGRE_PORT", "5432"),
        database=os.getenv("POSTGRE_DB", "assetblock"),
    )


def execute_query(query: str, params=None, fetch=False):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute(query, params)
        if fetch:
            result = cur.fetchall()
            return [dict(row) for row in result]
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


def execute_one(query: str, params=None):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute(query, params)
        result = cur.fetchone()
        conn.commit()
        return dict(result) if result else None
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()
