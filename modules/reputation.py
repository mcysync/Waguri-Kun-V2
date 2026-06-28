import logging
from pyrogram import Client, filters
from pyrogram.types import Message

from modules.database import db

logger = logging.getLogger("WaguriBot.Reputation")

async def init_rep_db():
    await db.execute("""
        CREATE TABLE IF NOT EXISTS reputation (
            chat_id INTEGER,
            user_id INTEGER,
            rep INTEGER DEFAULT 0,
            PRIMARY KEY (chat_id, user_id)
        )
    """)

import asyncio
asyncio.get_event_loop().create_task(init_rep_db())

REP_TRIGGERS = ["+", "++", "thx", "thanks", "arigato", "ty", "thank you"]

@Client.on_message(filters.regex(r"^(?i)(\+||\+\+|thx|thanks|arigato|ty|thank you)$") & filters.group & filters.reply)
async def give_reputation(client: Client, message: Message):
    sender_id = message.from_user.id
    receiver_id = message.reply_to_message.from_user.id
    chat_id = message.chat.id
    
    if sender_id == receiver_id:
        return await message.reply_text("🌸 You can't give reputation to yourself, silly!")
        
    if message.reply_to_message.from_user.is_bot:
        return await message.reply_text("🌸 Bots don't need reputation, but thank you! ❤️")
        
    await db.execute(
        "INSERT INTO reputation (chat_id, user_id, rep) VALUES (?, ?, 1) "
        "ON CONFLICT(chat_id, user_id) DO UPDATE SET rep = rep + 1",
        chat_id, receiver_id
    )
    
    record = await db.fetchone("SELECT rep FROM reputation WHERE chat_id = ? AND user_id = ?", chat_id, receiver_id)
    new_rep = record[0] if record else 1
    
    await message.reply_text(f"🌸 **Reputation Increased!** 📈\n{message.reply_to_message.from_user.mention} now has `{new_rep}` rep points.")

@Client.on_message(filters.command("rep") & filters.group)
async def check_reputation(client: Client, message: Message):
    user_id = message.reply_to_message.from_user.id if message.reply_to_message else message.from_user.id
    
    record = await db.fetchone("SELECT rep FROM reputation WHERE chat_id = ? AND user_id = ?", message.chat.id, user_id)
    rep = record[0] if record else 0
    
    user = await client.get_users(user_id)
    await message.reply_text(f"🌸 **{user.first_name}** has `{rep}` reputation points in this group.")
