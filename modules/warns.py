import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus

from utils import admin_required, bot_admin_required, extract_target
from config import Config
from modules.database import db

logger = logging.getLogger("WaguriBot.Warns")

async def get_warns(chat_id: int, user_id: int) -> int:
    query = "SELECT COUNT(*) FROM warns WHERE chat_id = ? AND user_id = ?"
    result = await db.fetchone(query, chat_id, user_id)
    return result[0] if result else 0

@Client.on_message(filters.command(["warn", "swarn"]) & filters.group)
@admin_required("can_restrict_members")
@bot_admin_required("can_restrict_members")
async def warn_user(client: Client, message: Message):
    cmd = message.command[0].lower()
    
    # INSTANT EXTRACTION
    target_id, target_mention, reason = await extract_target(client, message)
    if not target_id: return await message.reply_text("🌸 Please reply to a user to warn them.")
        
    try:
        member = await client.get_chat_member(message.chat.id, target_id)
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("🌸 Admins are immune to my warnings, silly!")
    except Exception: pass
            
    reason_text = reason or "No reason provided."
    admin_id = message.from_user.id if message.from_user else 0
    
    try:
        await db.execute("INSERT INTO warns (chat_id, user_id, admin_id, reason) VALUES (?, ?, ?, ?)", message.chat.id, target_id, admin_id, reason_text)
        warn_count = await get_warns(message.chat.id, target_id)
        max_warns = Config.MAX_WARNS
        
        if cmd == "swarn": await message.delete()
            
        if warn_count >= max_warns:
            await client.ban_chat_member(message.chat.id, target_id)
            await db.execute("DELETE FROM warns WHERE chat_id = ? AND user_id = ?", message.chat.id, target_id)
            if cmd != "swarn":
                await message.reply_text(f"🌸 **Max Warns Reached!** 🔨\n**Target:** {target_mention}\nHas been banned after {max_warns}/{max_warns} warnings.")
        else:
            if cmd != "swarn":
                await message.reply_text(f"🌸 **Warning!** ⚠️\n**Target:** {target_mention}\n**Warns:** `{warn_count}/{max_warns}`\n**Reason:** `{reason_text}`")
                
    except Exception as e:
        await message.reply_text(f"🌸 An error occurred applying the warning: `{e}`")

@Client.on_message(filters.command("warnings") & filters.group)
async def check_warnings(client: Client, message: Message):
    target_id, target_mention, _ = await extract_target(client, message)
    
    # If no target provided, check self
    if not target_id:
        target_id = message.from_user.id if message.from_user else 0
        target_mention = message.from_user.mention if message.from_user else "You"
        
    if target_id == 0: return
    
    try:
        warns = await db.fetchall("SELECT reason, timestamp FROM warns WHERE chat_id = ? AND user_id = ? ORDER BY timestamp DESC", message.chat.id, target_id)
        if not warns: return await message.reply_text(f"🌸 {target_mention} is a good bean! No warnings here. ✨")
            
        text = f"🌸 **Warnings for {target_mention}** ({len(warns)}/{Config.MAX_WARNS}):\n\n"
        for idx, (reason, ts) in enumerate(warns, 1): text += f"**{idx}.** `{reason}`\n"
        await message.reply_text(text)
    except Exception as e:
        await message.reply_text(f"🌸 Failed to retrieve warnings: `{e}`")

@Client.on_message(filters.command(["clearwarns", "rmwarns"]) & filters.group)
@admin_required("can_restrict_members")
async def clear_warnings(client: Client, message: Message):
    target_id, target_mention, _ = await extract_target(client, message)
    if not target_id: return await message.reply_text("🌸 Please reply to a user to clear their warnings.")
        
    try:
        await db.execute("DELETE FROM warns WHERE chat_id = ? AND user_id = ?", message.chat.id, target_id)
        await message.reply_text(f"🌸 Poof! 🪄 All warnings for {target_mention} have been cleared.")
    except Exception as e:
        await message.reply_text(f"🌸 Failed to clear warnings: `{e}`")
