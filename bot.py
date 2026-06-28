import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import uvloop
from pyrogram import Client, idle
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.events import EVENT_JOB_ERROR

from config import Config

# Setup base directories
def setup_directories() -> None:
    directories = [
        "data",
        "data/backups",
        "data/cache",
        "data/logs",
        "data/media",
        "data/temp"
    ]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

setup_directories()

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"data/logs/waguri_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("WaguriBot")
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)

class WaguriBot(Client):
    """Enterprise-grade Telegram Bot initialized with Pyrogram."""
    
    def __init__(self):
        super().__init__(
            name="WaguriBot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins=dict(root="modules"),
            workdir="data/temp",
            in_memory=False
        )
        self.scheduler = AsyncIOScheduler()
        self.start_time = datetime.now()
        self.version = "1.0.0-Enterprise"
        
    async def start(self):
        """Starts the Pyrogram client, scheduler, and database connection."""
        logger.info("Initializing WaguriBot...")
        
        # Initialize Database connection (will be loaded by modules/database.py)
        # We ensure it's ready before modules do DB calls
        from modules.database import db
        await db.connect()
        await db.create_tables()
        
        # Start Scheduler
        self._setup_scheduler()
        
        # Start Pyrogram
        await super().start()
        me = await self.get_me()
        logger.info(f"WaguriBot started successfully! Logged in as {me.first_name} (@{me.username})")
        logger.info(f"Loaded plugins securely. Waguri is ready for action~ 🌸")

    async def stop(self, *args):
        """Gracefully shuts down the bot, saving state."""
        logger.info("Stopping WaguriBot gracefully...")
        
        self.scheduler.shutdown()
        
        from modules.database import db
        await db.close()
        
        await super().stop()
        logger.info("WaguriBot has safely shut down. Goodbye! 🌸")

    def _setup_scheduler(self):
        """Configures the APScheduler for background tasks."""
        def scheduler_listener(event):
            logger.error(f"Scheduler job error: {event.exception}")
            
        self.scheduler.add_listener(scheduler_listener, EVENT_JOB_ERROR)
        self.scheduler.start()

if __name__ == "__main__":
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    bot = WaguriBot()
    
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Force terminated by user.")
