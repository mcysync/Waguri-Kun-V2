import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from modules.database import db

@Client.on_message(filters.regex(r"^(?i)(\+|\+\+|thx|thanks|arigato|ty|thank you)$") & filters.group & filters.reply)
async def give_reputation(client: Client, message: Message):
    sender_id = message.from_user.id
    receiver_id = message.reply_to_message.from_user.id
    chat_id = message.chat.id
    
    if sender_id == receiver_id:
        return await message.reply_text("🌸 You can't give reputation to yourself, silly!")
        
    if message.reply_to_message.from_user.is_bot:
        return await message.reply_text("🌸 Bots don't need reputation, but thank you! ❤️")
        
    await db.execute(
        "INSERT INTO reputation (chat_id, user_id, rep) VALUES (?, ?, 1) ON CONFLICT(chat_id, user_id) DO UPDATE SET rep = rep + 1",
        chat_id, receiver_id
    )
    record = await db.fetchone("SELECT rep FROM reputation WHERE chat_id = ? AND user_id = ?", chat_id, receiver_id)
    await message.reply_text(f"🌸 **Reputation Increased!** 📈\n{message.reply_to_message.from_user.mention} now has `{record[0]}` rep points.")
