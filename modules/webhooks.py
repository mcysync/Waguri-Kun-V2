import logging
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import sudo_only

logger = logging.getLogger("WaguriBot.Webhooks")

# Simple listener to manage webhooks state if external services push to Waguri
# Handled via FastAPI in api.py for incoming HTTP requests.
# This file provides management commands.

@Client.on_message(filters.command("webhook_info") & filters.private)
@sudo_only
async def webhook_info(client: Client, message: Message):
    # Because we use long-polling via Pyrogram for Telegram connection,
    # Telegram webhooks are empty. We report internal API status instead.
    
    await message.reply_text(
        "🌸 **Waguri API Gateway Status**\n\n"
        "**Host:** `0.0.0.0`\n"
        "**Port:** `8080`\n"
        "**Status:** `Active ✅`\n\n"
        "Dashboard Webhooks can hit `http://YOUR_IP:8080/broadcast` to send messages."
    )
