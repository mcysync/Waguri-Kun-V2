import logging
from pyrogram import Client, filters
from pyrogram.types import Message

from modules.database import db

logger = logging.getLogger("WaguriBot.Reputation")

# BULLETPROOF CUSTOM FILTER (NO REGEX CRASHES)
def check_rep_trigger(_, __, message: Message):
    if not message.text:
        return False
    triggers = ["+", "++", "thx", "thanks", "arigato", "ty", "thank you"]
    return message.text.strip().lower() in triggers

rep_filter = filters.create(check_rep_trigger)

@Client.on_message(filters.group & filters.reply & rep_filter)
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
