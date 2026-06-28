import logging
import re
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import admin_required
from modules.database import db

logger = logging.getLogger("WaguriBot.Blacklist")

async def init_blacklist_db():
    await db.execute("""
        CREATE TABLE IF NOT EXISTS blacklist_words (
            chat_id INTEGER,
            word TEXT,
            PRIMARY KEY (chat_id, word)
        )
    """)

import asyncio
asyncio.get_event_loop().create_task(init_blacklist_db())

@Client.on_message(filters.command("blacklist") & filters.group)
@admin_required("can_restrict_members")
async def add_blacklist(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.reply_text("🌸 Usage: `/blacklist [word]`")
        
    word = args[1].lower()
    
    await db.execute(
        "INSERT OR REPLACE INTO blacklist_words (chat_id, word) VALUES (?, ?)",
        message.chat.id, word
    )
    
    await message.reply_text(f"🌸 Word `{word}` added to the blacklist! Messages containing it will be deleted.")

@Client.on_message(filters.command("unblacklist") & filters.group)
@admin_required("can_restrict_members")
async def rm_blacklist(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.reply_text("🌸 Usage: `/unblacklist [word]`")
        
    word = args[1].lower()
    
    await db.execute("DELETE FROM blacklist_words WHERE chat_id = ? AND word = ?", message.chat.id, word)
    await message.reply_text(f"🌸 Word `{word}` removed from the blacklist.")

@Client.on_message(filters.command("blacklisted") & filters.group)
async def list_blacklist(client: Client, message: Message):
    records = await db.fetchall("SELECT word FROM blacklist_words WHERE chat_id = ?", message.chat.id)
    if not records:
        return await message.reply_text("🌸 No words are blacklisted in this chat.")
        
    text = "🌸 **Blacklisted Words:**\n\n"
    for (w,) in records:
        text += f"• `{w}`\n"
        
    await message.reply_text(text)

@Client.on_message(filters.text & filters.group & ~filters.bot, group=11)
async def blacklist_watcher(client: Client, message: Message):
    if not message.text:
        return
        
    chat_id = message.chat.id
    records = await db.fetchall("SELECT word FROM blacklist_words WHERE chat_id = ?", chat_id)
    if not records:
        return
        
    # Check for admins to bypass
    if message.from_user:
        try:
            member = await client.get_chat_member(chat_id, message.from_user.id)
            if member.status in ["administrator", "creator"]:
                return
        except Exception:
            pass
            
    text = message.text.lower()
    for (word,) in records:
        # Regex to match exact word boundary
        if re.search(r'\b' + re.escape(word) + r'\b', text):
            try:
                await message.delete()
                break
            except Exception as e:
                logger.error(f"Blacklist delete error: {e}")
