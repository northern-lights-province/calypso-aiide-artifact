import os

DB_URI = os.getenv("DB_URI", f"sqlite+aiosqlite:///data/calypso.db")
TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
