import logging
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import admin_required
from modules.database import db

logger = logging.getLogger("WaguriBot.Welcomes")

async def init_welcome_db():
    await db.execute("""
        CREATE TABLE IF NOT EXISTS welcome_settings (
            chat_id INTEGER PRIMARY KEY,
            message TEXT DEFAULT '🌸 Welcome {mention} to {chat}!',
            is_enabled BOOLEAN DEFAULT 1
        )
    """)

import asyncio
asyncio.get_event_loop().create_task(init_welcome_db())

@Client.on_message(filters.command("setwelcome") & filters.group)
@admin_required("can_change_info")
async def set_welcome(client: Client, message: Message):
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply_text(
            "🌸 Usage: `/setwelcome [text]`\n"
            "Format tags:\n"
            "`{first}` - User's first name\n"
            "`{last}` - User's last name\n"
            "`{fullname}` - User's full name\n"
            "`{username}` - User's username\n"
            "`{mention}` - User's mention\n"
            "`{id}` - User's ID\n"
            "`{chat}` - Chat's name"
        )
        
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else message.reply_to_message.text.markdown
    
    await db.execute(
        "INSERT OR REPLACE INTO welcome_settings (chat_id, message, is_enabled) VALUES (?, ?, 1)",
        message.chat.id, text
    )
    
    await message.reply_text("🌸 Custom welcome message has been set successfully!")

@Client.on_message(filters.command("welcome") & filters.group)
@admin_required("can_change_info")
async def toggle_welcome(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.reply_text("🌸 Usage: `/welcome on` or `/welcome off`")
        
    state = args[1].lower() == "on"
    
    await db.execute(
        "INSERT OR REPLACE INTO welcome_settings (chat_id, is_enabled) VALUES (?, ?)",
        message.chat.id, state
    )
    
    status = "enabled ✅" if state else "disabled ❌"
    await message.reply_text(f"🌸 Welcome messages are now {status}.")

@Client.on_message(filters.new_chat_members, group=7)
async def welcome_watcher(client: Client, message: Message):
    chat_id = message.chat.id
    
    settings = await db.fetchone("SELECT message, is_enabled FROM welcome_settings WHERE chat_id = ?", chat_id)
    if not settings or not settings[1]:
        return
        
    welcome_msg = settings[0]
    chat_name = message.chat.title
    
    for user in message.new_chat_members:
        # Don't welcome ourselves, pyrogram already fires a welcome on join
        if user.id == client.me.id:
            await message.reply_text("🌸 Hello! Thank you for adding me to your group. Make me an admin to unleash my full potential! ✨")
            continue
            
        formatted_msg = welcome_msg.format(
            first=user.first_name or "",
            last=user.last_name or "",
            fullname=f"{user.first_name or ''} {user.last_name or ''}".strip(),
            username=f"@{user.username}" if user.username else "",
            mention=user.mention,
            id=user.id,
            chat=chat_name
        )
        
        await message.reply_text(formatted_msg, disable_web_page_preview=True)
