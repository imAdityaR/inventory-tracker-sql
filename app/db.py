"""
db.py
Handles the PostgreSQL connection for the Inventory Tracker app.
Reads credentials from environment variables (see .env.example).
"""

import os
import sys
import psycopg2
from psycopg2.extensions import connection as PgConnection
from dotenv import load_dotenv

load_dotenv()


def get_connection() -> PgConnection:
    """
    Creates and returns a new PostgreSQL connection using credentials
    from environment variables. Exits gracefully with a clear message
    if the connection fails (e.g. wrong password, DB not running).
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "inventory_tracker"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
        )
        return conn
    except psycopg2.OperationalError as e:
        print("\n❌ Could not connect to the database.")
        print("   Make sure PostgreSQL is running and your .env file is correct.")
        print(f"   Details: {e}")
        sys.exit(1)
