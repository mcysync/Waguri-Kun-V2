import logging
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import admin_required, bot_admin_required, extract_user
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
    user_id, reason = extract_user(message)
    
    if not user_id:
        return await message.reply_text("🌸 Please reply to a user to warn them.")
        
    try:
        user = await client.get_users(user_id)
        member = await client.get_chat_member(message.chat.id, user.id)
        
        if member.status in ["administrator", "creator"]:
            return await message.reply_text("🌸 Admins are immune to my warnings, silly!")
            
        reason_text = reason or "No reason provided."
        
        # Save warning to DB
        await db.execute(
            "INSERT INTO warns (chat_id, user_id, admin_id, reason) VALUES (?, ?, ?, ?)",
            message.chat.id, user.id, message.from_user.id, reason_text
        )
        
        warn_count = await get_warns(message.chat.id, user.id)
        max_warns = Config.MAX_WARNS
        
        if cmd == "swarn":
            await message.delete()
            
        if warn_count >= max_warns:
            # Action to take (default: ban)
            await client.ban_chat_member(message.chat.id, user.id)
            await db.execute("DELETE FROM warns WHERE chat_id = ? AND user_id = ?", message.chat.id, user.id)
            if cmd != "swarn":
                await message.reply_text(f"🌸 **Max Warns Reached!** 🔨\n**User:** {user.mention}\nHas been banned after receiving {max_warns}/{max_warns} warnings.")
        else:
            if cmd != "swarn":
                await message.reply_text(f"🌸 **Warning!** ⚠️\n**User:** {user.mention}\n**Warns:** `{warn_count}/{max_warns}`\n**Reason:** `{reason_text}`")
                
    except Exception as e:
        logger.error(f"Warn error: {e}")
        await message.reply_text("🌸 An error occurred while applying the warning.")

@Client.on_message(filters.command("warnings") & filters.group)
async def check_warnings(client: Client, message: Message):
    user_id, _ = extract_user(message)
    target = user_id if user_id else message.from_user.id
    
    try:
        user = await client.get_users(target)
        warns = await db.fetchall(
            "SELECT reason, timestamp FROM warns WHERE chat_id = ? AND user_id = ? ORDER BY timestamp DESC",
            message.chat.id, user.id
        )
        
        if not warns:
            return await message.reply_text(f"🌸 **{user.first_name}** is a good bean! No warnings here. ✨")
            
        text = f"🌸 **Warnings for {user.mention}** ({len(warns)}/{Config.MAX_WARNS}):\n\n"
        for idx, (reason, ts) in enumerate(warns, 1):
            text += f"**{idx}.** `{reason}`\n"
            
        await message.reply_text(text)
    except Exception as e:
        logger.error(f"Check warns error: {e}")
        await message.reply_text("🌸 Failed to retrieve warnings.")

@Client.on_message(filters.command(["clearwarns", "rmwarns"]) & filters.group)
@admin_required("can_restrict_members")
async def clear_warnings(client: Client, message: Message):
    user_id, _ = extract_user(message)
    if not user_id:
        return await message.reply_text("🌸 Please reply to a user to clear their warnings.")
        
    try:
        user = await client.get_users(user_id)
        await db.execute("DELETE FROM warns WHERE chat_id = ? AND user_id = ?", message.chat.id, user.id)
        await message.reply_text(f"🌸 Poof! 🪄 All warnings for **{user.mention}** have been cleared.")
    except Exception as e:
        await message.reply_text("🌸 Failed to clear warnings.")
