import logging
import asyncio
from pyrogram import Client

from config import Config
from modules.database import db

logger = logging.getLogger("WaguriBot.API")

# Cross-Platform Check: Skip loading web server if FastAPI (Rust) isn't installed
try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    import uvicorn
    HAS_API = True
except ImportError:
    HAS_API = False

# Safe method to inject pyrogram client into FastAPI
bot_instance = None

def set_bot_instance(client: Client):
    global bot_instance
    bot_instance = client

if HAS_API:
    app = FastAPI(title="WaguriBot API", version="1.0-Enterprise")

    class BroadcastRequest(BaseModel):
        token: str
        chat_id: int
        message: str

    @app.get("/")
    async def root():
        return {"status": "WaguriBot API is online 🌸"}

    @app.get("/stats")
    async def api_stats():
        users = (await db.fetchone("SELECT COUNT(*) FROM users"))[0]
        chats = (await db.fetchone("SELECT COUNT(*) FROM chats"))[0]
        return {
            "users": users,
            "chats": chats,
            "version": "1.0.0-Enterprise"
        }

    @app.post("/broadcast")
    async def api_broadcast(req: BroadcastRequest):
        if req.token != Config.BOT_TOKEN:
            raise HTTPException(status_code=403, detail="Invalid authorization token")
            
        if not bot_instance:
            raise HTTPException(status_code=503, detail="Bot client is not initialized")
            
        try:
            await bot_instance.send_message(req.chat_id, req.message)
            return {"status": "success", "chat_id": req.chat_id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def run_api():
        """Background task to run the FastAPI server."""
        config = uvicorn.Config(app, host="0.0.0.0", port=8080, log_level="error")
        server = uvicorn.Server(config)
        logger.info("Waguri Web API starting on port 8080...")
        await server.serve()

else:
    async def run_api():
        logger.info("FastAPI not installed. Running in Mobile/Lite Mode (API Web Server Disabled).")

# Auto-start API worker if in run mode
import sys
if "run" in sys.argv or __name__ != "__main__":
    loop = asyncio.get_event_loop()
    from bot import bot
    set_bot_instance(bot)
    loop.create_task(run_api())
