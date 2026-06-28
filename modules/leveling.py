import logging
import math
from pyrogram import Client, filters
from pyrogram.types import Message

from config import Config
from modules.database import db

logger = logging.getLogger("WaguriBot.Leveling")

async def init_leveling_db():
    await db.execute("""
        CREATE TABLE IF NOT EXISTS xp_system (
            chat_id INTEGER,
            user_id INTEGER,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            PRIMARY KEY (chat_id, user_id)
        )
    """)

import asyncio
asyncio.get_event_loop().create_task(init_leveling_db())

def get_required_xp(level: int) -> int:
    return math.floor(100 * (level ** 1.5))

@Client.on_message(filters.group & ~filters.bot & ~filters.command(["rank", "level"]), group=12)
async def xp_watcher(client: Client, message: Message):
    if not message.from_user:
        return
        
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    xp_gain = 5  # Give 5 XP per message
    
    record = await db.fetchone("SELECT xp, level FROM xp_system WHERE chat_id = ? AND user_id = ?", chat_id, user_id)
    
    if not record:
        await db.execute("INSERT INTO xp_system (chat_id, user_id, xp, level) VALUES (?, ?, ?, 1)", chat_id, user_id, xp_gain)
        return
        
    current_xp, current_level = record
    new_xp = current_xp + xp_gain
    req_xp = get_required_xp(current_level)
    
    if new_xp >= req_xp:
        new_level = current_level + 1
        await db.execute("UPDATE xp_system SET xp = ?, level = ? WHERE chat_id = ? AND user_id = ?", new_xp, new_level, chat_id, user_id)
        await message.reply_text(f"🌸 ✨ **Level Up!** ✨\nCongratulations {message.from_user.mention}, you reached **Level {new_level}**!")
    else:
        await db.execute("UPDATE xp_system SET xp = ? WHERE chat_id = ? AND user_id = ?", new_xp, chat_id, user_id)

@Client.on_message(filters.command(["rank", "level"]) & filters.group)
async def check_rank(client: Client, message: Message):
    user_id = message.from_user.id
    
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        
    record = await db.fetchone("SELECT xp, level FROM xp_system WHERE chat_id = ? AND user_id = ?", message.chat.id, user_id)
    
    if not record:
        return await message.reply_text("🌸 This user hasn't earned any XP yet.")
        
    xp, level = record
    req_xp = get_required_xp(level)
    
    user = await client.get_users(user_id)
    
    text = f"🌸 **Rank Info for {user.first_name}**\n\n"
    text += f"🌟 **Level:** `{level}`\n"
    text += f"✨ **XP:** `{xp} / {req_xp}`"
    
    await message.reply_text(text)
