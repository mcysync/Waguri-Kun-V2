import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from utils import admin_required
from modules.database import db

logger = logging.getLogger("WaguriBot.Reports")

async def init_reports_db():
    await db.execute("""
        CREATE TABLE IF NOT EXISTS report_settings (
            chat_id INTEGER PRIMARY KEY,
            is_enabled BOOLEAN DEFAULT 1
        )
    """)

import asyncio
asyncio.get_event_loop().create_task(init_reports_db())

@Client.on_message(filters.command("reports") & filters.group)
@admin_required("can_change_info")
async def toggle_reports(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.reply_text("🌸 Usage: `/reports on` or `/reports off`")
        
    state = args[1].lower() == "on"
    
    await db.execute(
        "INSERT OR REPLACE INTO report_settings (chat_id, is_enabled) VALUES (?, ?)",
        message.chat.id, state
    )
    
    await message.reply_text(f"🌸 The report (@admin) system is now {'enabled ✅' if state else 'disabled ❌'}.")

@Client.on_message(filters.regex(r"(?i)^@admin(s)?") | filters.command(["report"]))
async def report_message(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("🌸 Reply to a message to report it to the admins.")
        
    chat_id = message.chat.id
    
    settings = await db.fetchone("SELECT is_enabled FROM report_settings WHERE chat_id = ?", chat_id)
    if settings and not settings[0]:
        return # Reports disabled in this chat
        
    admins = []
    async for admin in client.get_chat_members(chat_id, filter=filters.ChatMembersFilter.ADMINISTRATORS):
        if not admin.user.is_bot:
            admins.append(admin.user.mention)
            
    if not admins:
        return await message.reply_text("🌸 There are no human admins to notify here!")
        
    report_text = f"🌸 **Report!** 🚨\n**User:** {message.from_user.mention}\n**Reason:** Needs attention!\n"
    
    # Mention all admins invisibly
    mention_string = "[\u2063](tg://user?id=1)"
    for admin_mention in admins:
        mention_string += admin_mention + " "
        
    await message.reply_to_message.reply_text(
        report_text + mention_string,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("View Message", url=message.reply_to_message.link)]
        ])
    )
    
    await message.reply_text("🌸 I've notified the admins!")
