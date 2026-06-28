import logging
import re
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import admin_required
from modules.database import db
from modules.logging import log_event

logger = logging.getLogger("WaguriBot.Security")

DANGEROUS_EXTENSIONS = [".exe", ".bat", ".vbs", ".scr", ".cmd", ".js", ".msi", ".jar", ".wsf", ".sh"]

async def init_security_db():
    await db.execute("""
        CREATE TABLE IF NOT EXISTS security_settings (
            chat_id INTEGER PRIMARY KEY,
            file_scan BOOLEAN DEFAULT 1,
            scam_detect BOOLEAN DEFAULT 1
        )
    """)

import asyncio
asyncio.get_event_loop().create_task(init_security_db())

@Client.on_message(filters.command("security") & filters.group)
@admin_required("can_change_info")
async def security_settings(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        record = await db.fetchone("SELECT file_scan, scam_detect FROM security_settings WHERE chat_id = ?", message.chat.id)
        fs, sd = record if record else (1, 1)
        
        text = "🌸 **Security Shields:**\n\n"
        text += f"📁 File Scanner: {'✅' if fs else '❌'}\n"
        text += f"🎣 Scam Detector: {'✅' if sd else '❌'}\n\n"
        text += "Use `/security file [on/off]` or `/security scam [on/off]` to toggle."
        return await message.reply_text(text)
        
    setting = args[1].lower()
    if len(args) < 3 or args[2].lower() not in ["on", "off"]:
        return await message.reply_text("🌸 Please specify `on` or `off`.")
        
    state = 1 if args[2].lower() == "on" else 0
    
    # Ensure record exists
    await db.execute("INSERT OR IGNORE INTO security_settings (chat_id) VALUES (?)", message.chat.id)
    
    if setting in ["file", "filescan"]:
        await db.execute("UPDATE security_settings SET file_scan = ? WHERE chat_id = ?", state, message.chat.id)
        await message.reply_text(f"🌸 File Scanner is now {'enabled ✅' if state else 'disabled ❌'}.")
    elif setting in ["scam", "scamdetect"]:
        await db.execute("UPDATE security_settings SET scam_detect = ? WHERE chat_id = ?", state, message.chat.id)
        await message.reply_text(f"🌸 Scam Detector is now {'enabled ✅' if state else 'disabled ❌'}.")
    else:
        await message.reply_text("🌸 Invalid setting. Use `file` or `scam`.")

@Client.on_message(filters.document & filters.group, group=14)
async def file_scanner(client: Client, message: Message):
    chat_id = message.chat.id
    
    record = await db.fetchone("SELECT file_scan FROM security_settings WHERE chat_id = ?", chat_id)
    if record and not record[0]:
        return
        
    file_name = message.document.file_name
    if not file_name:
        return
        
    ext = "." + file_name.split(".")[-1].lower() if "." in file_name else ""
    
    if ext in DANGEROUS_EXTENSIONS:
        try:
            await message.delete()
            await message.reply_text(f"🌸 **Threat Blocked!** 🛡\nDeleted a dangerous file: `{file_name}` sent by {message.from_user.mention}.")
            await log_event(client, chat_id, f"Security: Deleted dangerous file {file_name} from {message.from_user.mention}")
        except Exception as e:
            logger.error(f"File scan delete error: {e}")

@Client.on_message(filters.text & filters.group, group=15)
async def scam_detector(client: Client, message: Message):
    chat_id = message.chat.id
    
    record = await db.fetchone("SELECT scam_detect FROM security_settings WHERE chat_id = ?", chat_id)
    if record and not record[0]:
        return
        
    text = message.text.lower()
    
    # Common phishing patterns
    scam_patterns = [
        r"t\.m[e@]\/.*(nitro|premium|gift).*(free)",
        r"(free|get).*(telegram|tg).*(premium)",
        r"(http|https)://.*(steam-nitro|discord-gift|telegram-premium).*\.(com|ru|org|xyz|shop)"
    ]
    
    for pattern in scam_patterns:
        if re.search(pattern, text):
            try:
                await message.delete()
                await client.restrict_chat_member(chat_id, message.from_user.id, filters.ChatPermissions(can_send_messages=False))
                await message.reply_text(f"🌸 **Phishing Blocked!** 🎣\n{message.from_user.mention} was muted for sending a malicious scam link.")
                await log_event(client, chat_id, f"Security: Muted {message.from_user.mention} for scam link.")
                break
            except Exception as e:
                logger.error(f"Scam detect error: {e}")
