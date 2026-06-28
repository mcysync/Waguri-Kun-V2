import logging
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

import asyncio
asyncio.get_event_loop().create_task(init_reminders_db())

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

async def reminder_worker(client: Client):
    """Background task to process user reminders."""
    await client.wait_for_start()
    while not client.is_connected:
        await asyncio.sleep(1)
        
    logger.info("Reminder background worker started.")
    while True:
        try:
            now = datetime.now()
            
            records = await db.fetchall("SELECT id, chat_id, user_id, content FROM reminders WHERE trigger_time <= ?", now)
            
            for r_id, chat_id, user_id, content in records:
                try:
                    user = await client.get_users(user_id)
                    await client.send_message(
                        chat_id, 
                        f"🌸 **Ding Dong!** {user.mention}\n\nYou asked me to remind you:\n`{content}`"
                    )
                    await db.execute("DELETE FROM reminders WHERE id = ?", r_id)
                except Exception as e:
                    logger.error(f"Failed to send reminder {r_id}: {e}")
                    await db.execute("DELETE FROM reminders WHERE id = ?", r_id)
                    
        except Exception as e:
            logger.error(f"Reminder worker error: {e}")
            
        await asyncio.sleep(15) # Check every 15 seconds

# Register the worker
import sys
if "run" in sys.argv or __name__ != "__main__":
    loop = asyncio.get_event_loop()
    from bot import bot
    loop.create_task(reminder_worker(bot))
