import aiosqlite
import logging
from typing import Optional, List, Tuple, Any
import asyncio
from pathlib import Path

from config import Config

logger = logging.getLogger("WaguriBot.Database")

class Database:
    """Enterprise Asynchronous Database Wrapper for SQLite."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._conn: Optional[aiosqlite.Connection] = None
        self._lock = asyncio.Lock()

    async def connect(self):
        """Initializes connection to the SQLite database."""
        if not self._conn:
            self._conn = await aiosqlite.connect(self.db_path)
            # Enable Foreign Keys and WAL mode for high concurrency
            await self._conn.execute("PRAGMA foreign_keys = ON;")
            await self._conn.execute("PRAGMA journal_mode = WAL;")
            await self._conn.execute("PRAGMA synchronous = NORMAL;")
            logger.info(f"Connected to SQLite database at {self.db_path}")

    async def close(self):
        """Closes the database connection safely."""
        if self._conn:
            await self._conn.close()
            self._conn = None
            logger.info("Database connection closed.")

    async def execute(self, query: str, *args) -> aiosqlite.Cursor:
        """Executes a query and commits changes."""
        async with self._lock:
            if not self._conn:
                await self.connect()
            cursor = await self._conn.execute(query, args)
            await self._conn.commit()
            return cursor

    async def executemany(self, query: str, args: List[Tuple[Any, ...]]):
        """Executes multiple queries and commits changes."""
        async with self._lock:
            if not self._conn:
                await self.connect()
            await self._conn.executemany(query, args)
            await self._conn.commit()

    async def fetchone(self, query: str, *args) -> Optional[Tuple]:
        """Fetches a single row."""
        async with self._lock:
            if not self._conn:
                await self.connect()
            cursor = await self._conn.execute(query, args)
            return await cursor.fetchone()

    async def fetchall(self, query: str, *args) -> List[Tuple]:
        """Fetches all matching rows."""
        async with self._lock:
            if not self._conn:
                await self.connect()
            cursor = await self._conn.execute(query, args)
            return await cursor.fetchall()

    async def create_tables(self):
        """Creates the necessary schemas if they don't exist."""
        schemas = [
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                is_premium BOOLEAN DEFAULT 0,
                joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS chats (
                chat_id INTEGER PRIMARY KEY,
                title TEXT,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS warns (
                warn_id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                user_id INTEGER,
                admin_id INTEGER,
                reason TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(chat_id) REFERENCES chats(chat_id),
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS settings (
                chat_id INTEGER PRIMARY KEY,
                language TEXT DEFAULT 'en',
                antispam_enabled BOOLEAN DEFAULT 1,
                welcomes_enabled BOOLEAN DEFAULT 1,
                FOREIGN KEY(chat_id) REFERENCES chats(chat_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS notes (
                chat_id INTEGER,
                name TEXT,
                content TEXT,
                file_id TEXT,
                type TEXT,
                PRIMARY KEY (chat_id, name),
                FOREIGN KEY(chat_id) REFERENCES chats(chat_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS economy (
                user_id INTEGER PRIMARY KEY,
                wallet INTEGER DEFAULT 0,
                bank INTEGER DEFAULT 0,
                last_daily TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            );
            """
        ]
        
        for schema in schemas:
            await self.execute(schema)
            
        logger.info("Database schemas verified successfully.")

# Singleton pattern for the database
db = Database(Config.DATABASE_PATH)
