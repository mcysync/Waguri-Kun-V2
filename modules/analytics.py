import logging
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import admin_required
from modules.database import db

logger = logging.getLogger("WaguriBot.Analytics")

async def init_analytics_db():
    await db.execute("""
        CREATE TABLE IF NOT EXISTS message_stats (
            chat_id INTEGER,
            user_id INTEGER,
            msg_count INTEGER DEFAULT 0,
            PRIMARY KEY (chat_id, user_id)
        )
    """)

import asyncio
asyncio.get_event_loop().create_task(init_analytics_db())

@Client.on_message(filters.group & ~filters.bot, group=13)
async def analytics_watcher(client: Client, message: Message):
    if not message.from_user:
        return
        
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # Save chat tracking
    await db.execute("INSERT OR IGNORE INTO chats (chat_id, title) VALUES (?, ?)", chat_id, message.chat.title)
    
    # Save message count
    await db.execute(
        "INSERT INTO message_stats (chat_id, user_id, msg_count) VALUES (?, ?, 1) "
        "ON CONFLICT(chat_id, user_id) DO UPDATE SET msg_count = msg_count + 1",
        chat_id, user_id
    )

@Client.on_message(filters.command(["top", "topusers"]) & filters.group)
async def top_users(client: Client, message: Message):
    records = await db.fetchall(
        "SELECT user_id, msg_count FROM message_stats WHERE chat_id = ? ORDER BY msg_count DESC LIMIT 10",
        message.chat.id
    )
    
    if not records:
        return await message.reply_text("🌸 It's quiet here... No data recorded yet.")
        
    text = "🌸 **Top 10 Most Active Members:**\n\n"
    
    for idx, (user_id, count) in enumerate(records, 1):
        try:
            user = await client.get_users(user_id)
            name = user.first_name
        except Exception:
            name = f"User {user_id}"
            
        text += f"**{idx}.** {name} - `{count}` messages\n"
        
    await message.reply_text(text)

@Client.on_message(filters.command("mystats") & filters.group)
async def my_stats(client: Client, message: Message):
    record = await db.fetchone(
        "SELECT msg_count FROM message_stats WHERE chat_id = ? AND user_id = ?",
        message.chat.id, message.from_user.id
    )
    
    count = record[0] if record else 0
    await message.reply_text(f"🌸 You have sent `{count}` messages in this group, {message.from_user.mention}!")
