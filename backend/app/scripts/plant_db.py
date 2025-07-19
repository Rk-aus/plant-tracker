"""
Utility: simple read / maintenance actions on the `plants` table.
Run with, e.g.:
    python backend/scripts/plant_db.py --env test --action list
    python backend/scripts/plant_db.py --env test --action truncate
"""

import os
import sys
import argparse
from pathlib import Path
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv


def load_env(env_name: str) -> None:
    """Load the correct .env file for the given environment."""
    root = Path(__file__).resolve().parents[2]  
    env_file = root / (f".env.{env_name}" if env_name != "production" else ".env")

    if not env_file.exists():
        sys.exit(f"❌  {env_file} not found")

    load_dotenv(dotenv_path=env_file, override=True)
    print(f"📦 Loaded {env_file.relative_to(root)}")


def get_connection():
    """Create a psycopg2 connection from environment variables."""
    try:
        return psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )
    except Exception as exc:
        sys.exit(f"❌  DB connection failed: {exc}")


def list_rows(cur):
    cur.execute("SELECT * FROM plants ORDER BY plant_id;")
    rows = cur.fetchall()
    print(f"📄 {len(rows)} row(s):")
    for r in rows:
        print(r)


def truncate_table(cur):
    cur.execute(
        sql.SQL("TRUNCATE TABLE {} RESTART IDENTITY CASCADE;").format(
            sql.Identifier("plants")
        )
    )
    print("🗑️  Table truncated (rows cleared, id sequence reset).")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--env",
        default=os.getenv("ENV", "development"),
        help="Which environment to load (.env.<env>). "
        "E.g. 'test', 'development', 'production'",
    )
    parser.add_argument(
        "--action",
        choices=["list", "truncate"],
        default="list",
        help="What to do: list rows or truncate the table.",
    )
    args = parser.parse_args()

    load_env(args.env)

    print(f"🧪 ENV = {os.getenv('ENV')}")
    print(f"🌱 DB_NAME = {os.getenv('DB_NAME')}")

    conn = get_connection()
    conn.autocommit = True
    cur = conn.cursor()

    try:
        if args.action == "list":
            list_rows(cur)
        else:
            truncate_table(cur)
    finally:
        cur.close()
        conn.close()
        print("✅ Done.")


if __name__ == "__main__":
    main()
