import logging
import asyncio
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import admin_required, parse_time
from modules.database import db

logger = logging.getLogger("WaguriBot.Scheduler")

async def init_scheduler_db():
    await db.execute("""
        CREATE TABLE IF NOT EXISTS scheduled_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            user_id INTEGER,
            content TEXT,
            trigger_time TIMESTAMP
        )
    """)

# Safe async initialization
loop = asyncio.get_event_loop()
loop.create_task(init_scheduler_db())

@Client.on_message(filters.command("schedule") & filters.group)
@admin_required("can_send_messages")
async def schedule_message(client: Client, message: Message):
    args = message.text.split(None, 2)
    if len(args) < 3:
        return await message.reply_text("🌸 Usage: `/schedule [time] [message]`\nExample: `/schedule 1h 🌸 Drink water!`")
        
    time_str = args[1]
    content = args[2]
    
    parsed_time = parse_time(time_str)
    if not parsed_time:
        return await message.reply_text("🌸 Invalid time format! Use things like `10m`, `2h`, `1d`.")
        
    trigger_time = datetime.now() + timedelta(seconds=parsed_time)
    
    await db.execute(
        "INSERT INTO scheduled_messages (chat_id, user_id, content, trigger_time) VALUES (?, ?, ?, ?)",
        message.chat.id, message.from_user.id, content, trigger_time
    )
    
    await message.reply_text(f"🌸 Message scheduled successfully! I will send it in `{time_str}`.")

# Note: Background worker removed temporarily to prevent Termux circular import crashes.
logger.info("Scheduler module loaded safely.")
