import logging
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

import asyncio
asyncio.get_event_loop().create_task(init_scheduler_db())

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

async def scheduler_worker(client: Client):
    """Background task to process scheduled messages."""
    await client.wait_for_start()
    while not client.is_connected:
        await asyncio.sleep(1)
        
    logger.info("Scheduler background worker started.")
    while True:
        try:
            now = datetime.now()
            
            # Fetch due messages
            records = await db.fetchall("SELECT id, chat_id, content FROM scheduled_messages WHERE trigger_time <= ?", now)
            
            for record_id, chat_id, content in records:
                try:
                    await client.send_message(chat_id, f"🌸 **Scheduled Announcement:**\n\n{content}")
                    await db.execute("DELETE FROM scheduled_messages WHERE id = ?", record_id)
                except Exception as e:
                    logger.error(f"Failed to send scheduled message {record_id} to {chat_id}: {e}")
                    # Delete it anyway to prevent infinite loop
                    await db.execute("DELETE FROM scheduled_messages WHERE id = ?", record_id)
                    
        except Exception as e:
            logger.error(f"Scheduler worker error: {e}")
            
        await asyncio.sleep(30) # Check every 30 seconds

# Register the worker with the asyncio event loop once
import sys
if "run" in sys.argv or __name__ != "__main__":
    loop = asyncio.get_event_loop()
    from bot import bot # Import the global bot instance safely
    loop.create_task(scheduler_worker(bot))
