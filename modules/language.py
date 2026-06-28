import logging
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import admin_required
from modules.database import db

logger = logging.getLogger("WaguriBot.Language")

# Enterprise scale would use gettext / .po files. 
# This module implements the abstraction for database locale assignment.
SUPPORTED_LANGUAGES = {"en": "English", "es": "Español", "ja": "Japanese (日本語)"}

@Client.on_message(filters.command("setlang") & filters.group)
@admin_required("can_change_info")
async def set_language(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        langs = ", ".join(f"`{k}` ({v})" for k, v in SUPPORTED_LANGUAGES.items())
        return await message.reply_text(f"🌸 Supported languages:\n{langs}\n\nUsage: `/setlang [code]`")
        
    lang_code = args[1].lower()
    
    if lang_code not in SUPPORTED_LANGUAGES:
        return await message.reply_text("🌸 Unsupported language code.")
        
    await db.execute("INSERT OR IGNORE INTO settings (chat_id) VALUES (?)", message.chat.id)
    await db.execute("UPDATE settings SET language = ? WHERE chat_id = ?", lang_code, message.chat.id)
    
    lang_name = SUPPORTED_LANGUAGES[lang_code]
    await message.reply_text(f"🌸 Group language successfully set to **{lang_name}**!")

async def get_chat_language(chat_id: int) -> str:
    """Helper method to be imported by other modules requiring localization."""
    record = await db.fetchone("SELECT language FROM settings WHERE chat_id = ?", chat_id)
    return record[0] if record else "en"
