import aiosqlite
import logging
import asyncio
from typing import Optional, List, Tuple

from config import Config

logger = logging.getLogger("WaguriBot.Database")

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._conn: Optional[aiosqlite.Connection] = None
        self._lock = asyncio.Lock()

    async def connect(self):
        if not self._conn:
            self._conn = await aiosqlite.connect(self.db_path)
            await self._conn.execute("PRAGMA foreign_keys = ON;")
            await self._conn.execute("PRAGMA journal_mode = WAL;")

    async def close(self):
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def execute(self, query: str, *args) -> aiosqlite.Cursor:
        async with self._lock:
            if not self._conn: await self.connect()
            cursor = await self._conn.execute(query, args)
            await self._conn.commit()
            return cursor

    async def fetchone(self, query: str, *args) -> Optional[Tuple]:
        async with self._lock:
            if not self._conn: await self.connect()
            cursor = await self._conn.execute(query, args)
            return await cursor.fetchone()

    async def fetchall(self, query: str, *args) -> List[Tuple]:
        async with self._lock:
            if not self._conn: await self.connect()
            cursor = await self._conn.execute(query, args)
            return await cursor.fetchall()

    async def create_tables(self):
        schemas = [
            "CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, is_premium BOOLEAN DEFAULT 0, joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP);",
            "CREATE TABLE IF NOT EXISTS chats (chat_id INTEGER PRIMARY KEY, title TEXT, added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP);",
            "CREATE TABLE IF NOT EXISTS warns (warn_id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, user_id INTEGER, admin_id INTEGER, reason TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);",
            "CREATE TABLE IF NOT EXISTS settings (chat_id INTEGER PRIMARY KEY, language TEXT DEFAULT 'en', antispam_enabled BOOLEAN DEFAULT 1, welcomes_enabled BOOLEAN DEFAULT 1);",
            "CREATE TABLE IF NOT EXISTS notes (chat_id INTEGER, name TEXT, content TEXT, file_id TEXT, type TEXT, PRIMARY KEY (chat_id, name));",
            "CREATE TABLE IF NOT EXISTS economy (user_id INTEGER PRIMARY KEY, wallet INTEGER DEFAULT 0, bank INTEGER DEFAULT 0, last_daily TIMESTAMP);",
            "CREATE TABLE IF NOT EXISTS flood_settings (chat_id INTEGER PRIMARY KEY, limit_count INTEGER DEFAULT 0, action TEXT DEFAULT 'mute');",
            "CREATE TABLE IF NOT EXISTS raid_settings (chat_id INTEGER PRIMARY KEY, is_active BOOLEAN DEFAULT 0, action TEXT DEFAULT 'kick', trigger_count INTEGER DEFAULT 5, time_window INTEGER DEFAULT 10);",
            "CREATE TABLE IF NOT EXISTS captcha_settings (chat_id INTEGER PRIMARY KEY, is_enabled BOOLEAN DEFAULT 0, mode TEXT DEFAULT 'button');",
            "CREATE TABLE IF NOT EXISTS gbans (user_id INTEGER PRIMARY KEY, reason TEXT, admin_id INTEGER, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);",
            "CREATE TABLE IF NOT EXISTS welcome_settings (chat_id INTEGER PRIMARY KEY, message TEXT DEFAULT '🌸 Welcome {mention} to {chat}!', is_enabled BOOLEAN DEFAULT 1);",
            "CREATE TABLE IF NOT EXISTS goodbye_settings (chat_id INTEGER PRIMARY KEY, message TEXT DEFAULT '🌸 Goodbye {first}, we will miss you!', is_enabled BOOLEAN DEFAULT 0);",
            "CREATE TABLE IF NOT EXISTS report_settings (chat_id INTEGER PRIMARY KEY, is_enabled BOOLEAN DEFAULT 1);",
            "CREATE TABLE IF NOT EXISTS log_channels (chat_id INTEGER PRIMARY KEY, log_channel_id INTEGER);",
            "CREATE TABLE IF NOT EXISTS automod_rules (chat_id INTEGER, rule_type TEXT, action TEXT DEFAULT 'delete', PRIMARY KEY (chat_id, rule_type));",
            "CREATE TABLE IF NOT EXISTS blacklist_words (chat_id INTEGER, word TEXT, PRIMARY KEY (chat_id, word));",
            "CREATE TABLE IF NOT EXISTS whitelist_users (chat_id INTEGER, user_id INTEGER, PRIMARY KEY (chat_id, user_id));",
            "CREATE TABLE IF NOT EXISTS approved_users (chat_id INTEGER, user_id INTEGER, PRIMARY KEY (chat_id, user_id));",
            "CREATE TABLE IF NOT EXISTS xp_system (chat_id INTEGER, user_id INTEGER, xp INTEGER DEFAULT 0, level INTEGER DEFAULT 1, PRIMARY KEY (chat_id, user_id));",
            "CREATE TABLE IF NOT EXISTS reputation (chat_id INTEGER, user_id INTEGER, rep INTEGER DEFAULT 0, PRIMARY KEY (chat_id, user_id));",
            "CREATE TABLE IF NOT EXISTS security_settings (chat_id INTEGER PRIMARY KEY, file_scan BOOLEAN DEFAULT 1, scam_detect BOOLEAN DEFAULT 1);",
            "CREATE TABLE IF NOT EXISTS verified_users (user_id INTEGER PRIMARY KEY, admin_id INTEGER, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);",
            "CREATE TABLE IF NOT EXISTS scheduled_messages (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, user_id INTEGER, content TEXT, trigger_time TIMESTAMP);",
            "CREATE TABLE IF NOT EXISTS reminders (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, user_id INTEGER, content TEXT, trigger_time TIMESTAMP);",
            
            # 🔥 THE NEW BAN STORAGE SHIELD 🔥
            "CREATE TABLE IF NOT EXISTS banned_users (chat_id INTEGER, user_id INTEGER, admin_id INTEGER, reason TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (chat_id, user_id));"
        ]
        for s in schemas: await self.execute(s)
        logger.info("Database schemas loaded, including Ban Shield.")

db = Database(Config.DATABASE_PATH)
