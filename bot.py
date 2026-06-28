import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from pyrogram import Client

from config import Config

def setup_directories():
    for d in ["data", "data/backups", "data/cache", "data/logs", "data/temp"]:
        Path(d).mkdir(parents=True, exist_ok=True)

setup_directories()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("WaguriBot")
logging.getLogger("pyrogram").setLevel(logging.WARNING)

class WaguriBot(Client):
    def __init__(self):
        super().__init__(
            name="WaguriBot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins=dict(root="modules"),
            # 🔥 CRITICAL TERMUX FIX: Bypasses Android SQLite locks
            in_memory=True 
        )

    async def start(self):
        logger.info("Initializing WaguriBot in Mobile RAM Mode...")
        from modules.database import db
        await db.connect()
        await db.create_tables()
        logger.info("Database loaded!")

        await super().start()
        me = await self.get_me()
        logger.info(f"WaguriBot started successfully! Logged in as {me.first_name} (@{me.username}) 🌸")

    async def stop(self, *args):
        logger.info("Stopping gracefully...")
        from modules.database import db
        await db.close()
        await super().stop()

if __name__ == "__main__":
    bot = WaguriBot()
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Terminated by user.")
