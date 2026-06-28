import logging
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import admin_required, extract_user
from modules.database import db

logger = logging.getLogger("WaguriBot.Whitelist")

async def init_whitelist_db():
    await db.execute("""
        CREATE TABLE IF NOT EXISTS whitelist_users (
            chat_id INTEGER,
            user_id INTEGER,
            PRIMARY KEY (chat_id, user_id)
        )
    """)

import asyncio
asyncio.get_event_loop().create_task(init_whitelist_db())

@Client.on_message(filters.command("whitelist") & filters.group)
@admin_required("can_restrict_members")
async def add_whitelist(client: Client, message: Message):
    user_id, _ = extract_user(message)
    if not user_id:
        return await message.reply_text("🌸 Reply to a user to add them to the Anti-Spam/AutoMod whitelist.")
        
    await db.execute(
        "INSERT OR REPLACE INTO whitelist_users (chat_id, user_id) VALUES (?, ?)",
        message.chat.id, user_id
    )
    
    await message.reply_text(f"🌸 User `{user_id}` is now whitelisted! They bypass bot restrictions.")

@Client.on_message(filters.command("unwhitelist") & filters.group)
@admin_required("can_restrict_members")
async def rm_whitelist(client: Client, message: Message):
    user_id, _ = extract_user(message)
    if not user_id:
        return await message.reply_text("🌸 Reply to a user to remove them from the whitelist.")
        
    await db.execute("DELETE FROM whitelist_users WHERE chat_id = ? AND user_id = ?", message.chat.id, user_id)
    await message.reply_text(f"🌸 User `{user_id}` removed from the whitelist.")
    
# Whitelist validation utility
async def is_whitelisted(chat_id: int, user_id: int) -> bool:
    record = await db.fetchone("SELECT 1 FROM whitelist_users WHERE chat_id = ? AND user_id = ?", chat_id, user_id)
    return bool(record)
