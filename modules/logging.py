import logging
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import admin_required
from modules.database import db

logger = logging.getLogger("WaguriBot.Logging")

async def init_logging_db():
    await db.execute("""
        CREATE TABLE IF NOT EXISTS log_channels (
            chat_id INTEGER PRIMARY KEY,
            log_channel_id INTEGER
        )
    """)

import asyncio
asyncio.get_event_loop().create_task(init_logging_db())

@Client.on_message(filters.command("setlog") & filters.group)
@admin_required("can_change_info")
async def set_log_channel(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.reply_text("🌸 Usage: `/setlog [channel_id]`\nMake sure I am an admin in that channel!")
        
    try:
        log_channel_id = int(args[1])
        # Verify bot can post
        msg = await client.send_message(log_channel_id, "🌸 Connection established! Logging enabled for the group.")
        
        await db.execute(
            "INSERT OR REPLACE INTO log_channels (chat_id, log_channel_id) VALUES (?, ?)",
            message.chat.id, log_channel_id
        )
        
        await message.reply_text(f"🌸 Logging channel set to `{log_channel_id}` successfully!")
    except Exception as e:
        logger.error(f"Setlog error: {e}")
        await message.reply_text("🌸 Failed to connect to the channel. Are you sure the ID is correct and I am an admin there?")

@Client.on_message(filters.command("unsetlog") & filters.group)
@admin_required("can_change_info")
async def unset_log_channel(client: Client, message: Message):
    await db.execute("DELETE FROM log_channels WHERE chat_id = ?", message.chat.id)
    await message.reply_text("🌸 Logging disabled. Events will no longer be forwarded.")

async def log_event(client: Client, chat_id: int, text: str):
    """Utility function to send logs to the configured channel."""
    record = await db.fetchone("SELECT log_channel_id FROM log_channels WHERE chat_id = ?", chat_id)
    if record:
        try:
            await client.send_message(record[0], f"**Log Event** | `{chat_id}`\n\n{text}")
        except Exception as e:
            logger.error(f"Failed to write to log channel for {chat_id}: {e}")
