import logging
from pyrogram import Client

logger = logging.getLogger("WaguriBot.API")

# Cross-Platform Check: Try to import FastAPI, but fail silently on Termux
try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    import uvicorn
    HAS_API = True
except ImportError:
    HAS_API = False

# We store the bot client here safely without circular imports
bot_instance = None

def set_bot_instance(client: Client):
    global bot_instance
    bot_instance = client

if HAS_API:
    app = FastAPI(title="WaguriBot API", version="1.0-Lite")

    class BroadcastRequest(BaseModel):
        token: str
        chat_id: int
        message: str

    @app.get("/")
    async def root():
        return {"status": "WaguriBot API is online 🌸"}

    logger.info("Web API module loaded successfully (Server available).")
else:
    logger.info("Web API module loaded in Lite Mode (Web Server disabled for Termux).")

# NOTE: We removed the auto-start background task that was causing the import errors.
# The Telegram bot will now boot up instantly without getting stuck in a loop!
