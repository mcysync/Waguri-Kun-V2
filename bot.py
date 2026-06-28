import sys
import logging
from pathlib import Path
from pyrogram import Client
from config import Config

Path("data").mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", handlers=[logging.StreamHandler(sys.stdout)])
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
            in_memory=True  # 🔥 CRITICAL FIX: Restores RAM cache, prevents to_bytes crash!
        )

    async def start(self):
        from modules.database import db
        await db.connect()
        await db.create_tables()
        await super().start()
        me = await self.get_me()
        logger.info(f"WaguriBot started successfully! Logged in as {me.first_name} (@{me.username}) 🌸")

    async def stop(self, *args):
        from modules.database import db
        await db.close()
        await super().stop()

if __name__ == "__main__":
    bot = WaguriBot()
    bot.run()
