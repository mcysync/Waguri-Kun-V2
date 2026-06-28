import logging
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import sudo_only, extract_target
from config import Config
from modules.database import db

logger = logging.getLogger("WaguriBot.Bans")

@Client.on_message(filters.command("gban") & filters.group)
@sudo_only
async def global_ban(client: Client, message: Message):
    target_id, target_mention, reason = await extract_target(client, message)
    if not target_id: return await message.reply_text("🌸 Reply to a user or specify their ID to Global Ban them.")
    if target_id in Config.SUDO_USERS or target_id == Config.OWNER_ID:
        return await message.reply_text("🌸 I can't gban a sudo user! Baka!")
        
    reason = reason or "No reason provided."
    admin_id = message.from_user.id if message.from_user else 0
    
    await db.execute("INSERT OR REPLACE INTO gbans (user_id, reason, admin_id) VALUES (?, ?, ?)", target_id, reason, admin_id)
    
    chats = await db.fetchall("SELECT chat_id FROM chats")
    success, failed = 0, 0
    await message.reply_text(f"🌸 Initiating Global Ban on {target_mention}...\nReason: {reason}")
    
    for (chat_id,) in chats:
        try:
            await client.ban_chat_member(chat_id, target_id)
            success += 1
        except Exception:
            failed += 1
            
    await message.reply_text(f"🌸 **Global Ban Complete!** 🌍🔨\nUser: {target_mention}\nBanned in `{success}` chats (Failed: `{failed}`).")

@Client.on_message(filters.command("ungban") & filters.group)
@sudo_only
async def global_unban(client: Client, message: Message):
    target_id, target_mention, _ = await extract_target(client, message)
    if not target_id: return await message.reply_text("🌸 Reply to a user or specify their ID to un-gban them.")
        
    await db.execute("DELETE FROM gbans WHERE user_id = ?", target_id)
    chats = await db.fetchall("SELECT chat_id FROM chats")
    success, failed = 0, 0
    
    await message.reply_text(f"🌸 Reversing Global Ban on {target_mention}...")
    for (chat_id,) in chats:
        try:
            await client.unban_chat_member(chat_id, target_id)
            success += 1
        except Exception:
            failed += 1
            
    await message.reply_text(f"🌸 **Global Unban Complete!** ✨\nUser: {target_mention}\nUnbanned in `{success}` chats.")

@Client.on_message(filters.new_chat_members, group=6)
async def gban_watcher(client: Client, message: Message):
    for user in message.new_chat_members:
        is_gbanned = await db.fetchone("SELECT reason FROM gbans WHERE user_id = ?", user.id)
        if is_gbanned:
            try:
                await client.ban_chat_member(message.chat.id, user.id)
                await message.reply_text(f"🌸 **Blocked!** 🛑\n{user.mention} is globally banned.\nReason: `{is_gbanned[0]}`")
            except Exception:
                pass
