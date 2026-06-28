import logging
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import sudo_only, extract_user
from config import Config
from modules.database import db

logger = logging.getLogger("WaguriBot.Bans")

async def init_gban_db():
    await db.execute("""
        CREATE TABLE IF NOT EXISTS gbans (
            user_id INTEGER PRIMARY KEY,
            reason TEXT,
            admin_id INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

import asyncio
asyncio.get_event_loop().create_task(init_gban_db())

@Client.on_message(filters.command("gban") & filters.group)
@sudo_only
async def global_ban(client: Client, message: Message):
    user_id, reason = extract_user(message)
    if not user_id:
        return await message.reply_text("🌸 Reply to a user or specify their ID to Global Ban them.")
        
    if user_id in Config.SUDO_USERS:
        return await message.reply_text("🌸 I can't gban a sudo user! Baka!")
        
    reason = reason or "No reason provided."
    
    # Add to DB
    await db.execute(
        "INSERT OR REPLACE INTO gbans (user_id, reason, admin_id) VALUES (?, ?, ?)",
        user_id, reason, message.from_user.id
    )
    
    # Broadcast ban to all chats where bot is admin
    chats = await db.fetchall("SELECT chat_id FROM chats")
    success, failed = 0, 0
    
    await message.reply_text(f"🌸 Initiating Global Ban on `{user_id}`...\nReason: {reason}")
    
    for (chat_id,) in chats:
        try:
            await client.ban_chat_member(chat_id, user_id)
            success += 1
        except Exception:
            failed += 1
            
    await message.reply_text(f"🌸 **Global Ban Complete!** 🌍🔨\nUser: `{user_id}`\nBanned in `{success}` chats (Failed: `{failed}`).")

@Client.on_message(filters.command("ungban") & filters.group)
@sudo_only
async def global_unban(client: Client, message: Message):
    user_id, _ = extract_user(message)
    if not user_id:
        return await message.reply_text("🌸 Reply to a user or specify their ID to un-gban them.")
        
    await db.execute("DELETE FROM gbans WHERE user_id = ?", user_id)
    
    chats = await db.fetchall("SELECT chat_id FROM chats")
    success, failed = 0, 0
    
    await message.reply_text(f"🌸 Reversing Global Ban on `{user_id}`...")
    
    for (chat_id,) in chats:
        try:
            await client.unban_chat_member(chat_id, user_id)
            success += 1
        except Exception:
            failed += 1
            
    await message.reply_text(f"🌸 **Global Unban Complete!** ✨\nUser: `{user_id}`\nUnbanned in `{success}` chats.")

@Client.on_message(filters.new_chat_members, group=6)
async def gban_watcher(client: Client, message: Message):
    for user in message.new_chat_members:
        is_gbanned = await db.fetchone("SELECT reason FROM gbans WHERE user_id = ?", user.id)
        if is_gbanned:
            try:
                await client.ban_chat_member(message.chat.id, user.id)
                await message.reply_text(f"🌸 **Blocked!** 🛑\n{user.mention} is globally banned.\nReason: `{is_gbanned[0]}`")
            except Exception as e:
                logger.error(f"GBan enforce error: {e}")
