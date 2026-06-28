import logging
import asyncio
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import parse_time
from modules.database import db

logger = logging.getLogger("WaguriBot.Reminders")

async def init_reminders_db():
    await db.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            user_id INTEGER,
            content TEXT,
            trigger_time TIMESTAMP
        )
    """)

# Safe async initialization
loop = asyncio.get_event_loop()
loop.create_task(init_reminders_db())

@Client.on_message(filters.command(["remind", "remindme"]))
async def set_reminder(client: Client, message: Message):
    args = message.text.split(None, 2)
    if len(args) < 3:
        return await message.reply_text("🌸 Usage: `/remindme [time] [task]`\nExample: `/remindme 30m Check the oven`")
        
    time_str = args[1]
    content = args[2]
    
    parsed_time = parse_time(time_str)
    if not parsed_time:
        return await message.reply_text("🌸 I couldn't understand that time format. Try `15m`, `1h`, `2d`, etc.")
        
    trigger_time = datetime.now() + timedelta(seconds=parsed_time)
    
    await db.execute(
        "INSERT INTO reminders (chat_id, user_id, content, trigger_time) VALUES (?, ?, ?, ?)",
        message.chat.id, message.from_user.id, content, trigger_time
    )
    
    await message.reply_text(f"🌸 Got it! I will remind you to `{content}` in `{time_str}`.")

@Client.on_message(filters.command("reminders"))
async def list_reminders(client: Client, message: Message):
    records = await db.fetchall("SELECT id, content, trigger_time FROM reminders WHERE user_id = ?", message.from_user.id)
    
    if not records:
        return await message.reply_text("🌸 You don't have any active reminders.")
        
    text = "🌸 **Your Active Reminders:**\n\n"
    for r_id, content, trigger_time in records:
        text += f"• `{content}` (ID: {r_id})\n  ⏳ Due: `{trigger_time}`\n"
        
    await message.reply_text(text)

# Note: Background worker removed temporarily to prevent Termux circular import crashes.
logger.info("Reminders module loaded safely.")
