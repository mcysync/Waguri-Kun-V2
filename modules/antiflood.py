import logging
import time
from collections import defaultdict
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions

from utils import admin_required, bot_admin_required
from modules.database import db

logger = logging.getLogger("WaguriBot.AntiFlood")

# In-memory store for flood tracking
# {chat_id: {user_id: {"count": int, "last_msg": str, "timestamp": float}}}
flood_cache = defaultdict(lambda: defaultdict(lambda: {"count": 0, "last_msg": "", "timestamp": 0.0}))

async def init_flood_db():
    await db.execute("""
        CREATE TABLE IF NOT EXISTS flood_settings (
            chat_id INTEGER PRIMARY KEY,
            limit_count INTEGER DEFAULT 0,
            action TEXT DEFAULT 'mute'
        )
    """)

import asyncio
asyncio.get_event_loop().create_task(init_flood_db())

@Client.on_message(filters.command("setflood") & filters.group)
@admin_required("can_restrict_members")
async def set_flood(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.reply_text("🌸 Usage: `/setflood [number]` (0 to disable)")
        
    try:
        limit = int(args[1])
        if limit < 0:
            raise ValueError
    except ValueError:
        return await message.reply_text("🌸 Please provide a valid positive number.")
        
    await db.execute(
        "INSERT OR REPLACE INTO flood_settings (chat_id, limit_count, action) VALUES (?, ?, COALESCE((SELECT action FROM flood_settings WHERE chat_id = ?), 'mute'))",
        message.chat.id, limit, message.chat.id
    )
    
    if limit == 0:
        await message.reply_text("🌸 Anti-Flood has been disabled for this group.")
    else:
        await message.reply_text(f"🌸 Anti-Flood set! I'll take action if someone sends more than `{limit}` consecutive messages.")

@Client.on_message(filters.command("floodmode") & filters.group)
@admin_required("can_restrict_members")
async def set_flood_mode(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.reply_text("🌸 Usage: `/floodmode [kick/ban/mute]`")
        
    mode = args[1].lower()
    if mode not in ["kick", "ban", "mute"]:
        return await message.reply_text("🌸 Invalid mode! Please choose `kick`, `ban`, or `mute`.")
        
    await db.execute(
        "INSERT OR REPLACE INTO flood_settings (chat_id, limit_count, action) VALUES (?, COALESCE((SELECT limit_count FROM flood_settings WHERE chat_id = ?), 0), ?)",
        message.chat.id, message.chat.id, mode
    )
    
    await message.reply_text(f"🌸 Anti-Flood action set to: **{mode.upper()}**")

@Client.on_message(filters.group & ~filters.bot & ~filters.me, group=3)
async def flood_watcher(client: Client, message: Message):
    if not message.from_user:
        return
        
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    settings = await db.fetchone("SELECT limit_count, action FROM flood_settings WHERE chat_id = ?", chat_id)
    if not settings or settings[0] == 0:
        return
        
    limit_count, action = settings
    
    now = time.time()
    user_cache = flood_cache[chat_id][user_id]
    
    # Reset count if last message was more than 10 seconds ago
    if now - user_cache["timestamp"] > 10.0:
        user_cache["count"] = 1
    else:
        user_cache["count"] += 1
        
    user_cache["timestamp"] = now
    
    if user_cache["count"] > limit_count:
        # Reset to prevent multiple triggers
        user_cache["count"] = 0
        
        # Check admin status
        try:
            member = await client.get_chat_member(chat_id, user_id)
            if member.status in ["administrator", "creator"]:
                return
        except Exception:
            pass
            
        try:
            if action == "ban":
                await client.ban_chat_member(chat_id, user_id)
                await message.reply_text(f"🌸 **Anti-Flood Triggered!**\n{message.from_user.mention} was banned for flooding.")
            elif action == "kick":
                await client.ban_chat_member(chat_id, user_id)
                await client.unban_chat_member(chat_id, user_id)
                await message.reply_text(f"🌸 **Anti-Flood Triggered!**\n{message.from_user.mention} was kicked for flooding.")
            else: # mute
                await client.restrict_chat_member(chat_id, user_id, ChatPermissions(can_send_messages=False))
                await message.reply_text(f"🌸 **Anti-Flood Triggered!**\n{message.from_user.mention} was muted for flooding.")
        except Exception as e:
            logger.error(f"AntiFlood action error: {e}")
