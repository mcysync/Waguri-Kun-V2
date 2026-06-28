import logging
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import sudo_only
from modules.database import db

logger = logging.getLogger("WaguriBot.Premium")

@Client.on_message(filters.command("addpremium") & filters.private)
@sudo_only
async def grant_premium(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.reply_text("🌸 Master, provide a User ID to grant Premium status.")
        
    try:
        user_id = int(args[1])
        await db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", user_id)
        await db.execute("UPDATE users SET is_premium = 1 WHERE user_id = ?", user_id)
        
        await message.reply_text(f"🌸 User `{user_id}` has been granted Waguri Premium! 🌟")
    except ValueError:
        await message.reply_text("🌸 Invalid User ID.")

@Client.on_message(filters.command("rmpremium") & filters.private)
@sudo_only
async def revoke_premium(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.reply_text("🌸 Master, provide a User ID to revoke Premium status.")
        
    try:
        user_id = int(args[1])
        await db.execute("UPDATE users SET is_premium = 0 WHERE user_id = ?", user_id)
        await message.reply_text(f"🌸 User `{user_id}` has lost Waguri Premium. 🥀")
    except ValueError:
        await message.reply_text("🌸 Invalid User ID.")

@Client.on_message(filters.command("mypremium"))
async def check_premium(client: Client, message: Message):
    user_id = message.from_user.id
    
    record = await db.fetchone("SELECT is_premium FROM users WHERE user_id = ?", user_id)
    
    if record and record[0]:
        await message.reply_text("🌸 You are a **Waguri Premium** member! 🌟\nEnjoy increased economy limits and AI access.")
    else:
        await message.reply_text("🌸 You are currently on the Standard tier. Support the project to unlock Premium! ✨")
