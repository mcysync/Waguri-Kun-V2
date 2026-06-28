import logging
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import admin_required
from modules.database import db

logger = logging.getLogger("WaguriBot.Goodbye")

async def init_goodbye_db():
    await db.execute("""
        CREATE TABLE IF NOT EXISTS goodbye_settings (
            chat_id INTEGER PRIMARY KEY,
            message TEXT DEFAULT '🌸 Goodbye {first}, we will miss you!',
            is_enabled BOOLEAN DEFAULT 0
        )
    """)

import asyncio
asyncio.get_event_loop().create_task(init_goodbye_db())

@Client.on_message(filters.command("setgoodbye") & filters.group)
@admin_required("can_change_info")
async def set_goodbye(client: Client, message: Message):
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply_text("🌸 Usage: `/setgoodbye [text]`\nSee `/setwelcome` for format tags.")
        
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else message.reply_to_message.text.markdown
    
    await db.execute(
        "INSERT OR REPLACE INTO goodbye_settings (chat_id, message, is_enabled) VALUES (?, ?, 1)",
        message.chat.id, text
    )
    
    await message.reply_text("🌸 Custom goodbye message has been set successfully!")

@Client.on_message(filters.command("goodbye") & filters.group)
@admin_required("can_change_info")
async def toggle_goodbye(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.reply_text("🌸 Usage: `/goodbye on` or `/goodbye off`")
        
    state = args[1].lower() == "on"
    
    await db.execute(
        "INSERT OR REPLACE INTO goodbye_settings (chat_id, is_enabled) VALUES (?, ?)",
        message.chat.id, state
    )
    
    status = "enabled ✅" if state else "disabled ❌"
    await message.reply_text(f"🌸 Goodbye messages are now {status}.")

@Client.on_message(filters.left_chat_member, group=8)
async def goodbye_watcher(client: Client, message: Message):
    chat_id = message.chat.id
    user = message.left_chat_member
    
    if user.id == client.me.id:
        return
        
    settings = await db.fetchone("SELECT message, is_enabled FROM goodbye_settings WHERE chat_id = ?", chat_id)
    if not settings or not settings[1]:
        return
        
    goodbye_msg = settings[0]
    chat_name = message.chat.title
    
    formatted_msg = goodbye_msg.format(
        first=user.first_name or "",
        last=user.last_name or "",
        fullname=f"{user.first_name or ''} {user.last_name or ''}".strip(),
        username=f"@{user.username}" if user.username else "",
        mention=user.mention,
        id=user.id,
        chat=chat_name
    )
    
    await message.reply_text(formatted_msg, disable_web_page_preview=True)
