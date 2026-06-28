import logging
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.enums import ChatMemberStatus

from utils import admin_required, bot_admin_required, extract_target, parse_time
from modules.database import db

logger = logging.getLogger("WaguriBot.Moderation")

@Client.on_message(filters.command(["ban", "tban", "sban", "shadowban"]) & filters.group)
@admin_required("can_restrict_members")
@bot_admin_required("can_restrict_members")
async def ban_user(client: Client, message: Message):
    cmd = message.command[0].lower()
    
    target_id, target_mention, reason = await extract_target(client, message)
    if not target_id:
        return await message.reply_text("🌸 Please reply to a user or provide their ID to ban them.")
        
    if target_id == client.me.id:
        return await message.reply_text("🌸 I can't ban myself! Baka!")
        
    try:
        member = await client.get_chat_member(message.chat.id, target_id)
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("🌸 I can't ban an administrator.")
    except Exception:
        pass
        
    ban_time = None
    duration_text = ""
    
    if cmd == "tban":
        args = message.text.split()
        time_idx = 1 if message.reply_to_message else 2
        if len(args) > time_idx:
            parsed_time = parse_time(args[time_idx])
            if parsed_time:
                ban_time = datetime.now() + timedelta(seconds=parsed_time)
                duration_text = f" for {args[time_idx]}"
                reason = " ".join(args[time_idx+1:])

    is_silent = cmd in ["sban", "shadowban"]
    admin_name = message.from_user.mention if message.from_user else "Admin"
    admin_id = message.from_user.id if message.from_user else 0
    reason_text = reason or "No reason provided."
    
    try:
        # 1. Ban them via Telegram API
        await client.ban_chat_member(message.chat.id, target_id, until_date=ban_time)
        
        # 2. Store them permanently in Waguri's Database Shield
        await db.execute(
            "INSERT OR REPLACE INTO banned_users (chat_id, user_id, admin_id, reason) VALUES (?, ?, ?, ?)",
            message.chat.id, target_id, admin_id, reason_text
        )
        
        if not is_silent:
            reply_text = f"🌸 **Banned!** 🔨\n**Target:** {target_mention}{duration_text}\n**Admin:** {admin_name}"
            if reason: reply_text += f"\n**Reason:** `{reason_text}`"
            await message.reply_text(reply_text)
        else:
            await message.delete()
            if message.reply_to_message: await message.reply_to_message.delete()
    except Exception as e:
        await message.reply_text(f"🌸 Failed to ban: `{e}`")

@Client.on_message(filters.command(["mute", "tmute", "smute"]) & filters.group)
@admin_required("can_restrict_members")
@bot_admin_required("can_restrict_members")
async def mute_user(client: Client, message: Message):
    cmd = message.command[0].lower()
    
    target_id, target_mention, reason = await extract_target(client, message)
    if not target_id:
        return await message.reply_text("🌸 Please reply to a user or provide their ID to mute them.")
        
    try:
        member = await client.get_chat_member(message.chat.id, target_id)
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("🌸 I can't mute an administrator.")
    except Exception:
        pass
        
    mute_time = None
    duration_text = ""
    
    if cmd == "tmute":
        args = message.text.split()
        time_idx = 1 if message.reply_to_message else 2
        if len(args) > time_idx:
            parsed_time = parse_time(args[time_idx])
            if parsed_time:
                mute_time = datetime.now() + timedelta(seconds=parsed_time)
                duration_text = f" for {args[time_idx]}"
                reason = " ".join(args[time_idx+1:])

    is_silent = cmd == "smute"
    permissions = ChatPermissions(can_send_messages=False)
    admin_name = message.from_user.mention if message.from_user else "Admin"
    
    try:
        await client.restrict_chat_member(message.chat.id, target_id, permissions, until_date=mute_time)
        if not is_silent:
            reply_text = f"🌸 **Muted!** 🤐\n**Target:** {target_mention}{duration_text}\n**Admin:** {admin_name}"
            if reason: reply_text += f"\n**Reason:** `{reason}`"
            await message.reply_text(reply_text)
        else:
            await message.delete()
    except Exception as e:
        await message.reply_text(f"🌸 Failed to mute: `{e}`")

@Client.on_message(filters.command("unmute") & filters.group)
@admin_required("can_restrict_members")
@bot_admin_required("can_restrict_members")
async def unmute_user(client: Client, message: Message):
    target_id, target_mention, _ = await extract_target(client, message)
    if not target_id: return await message.reply_text("🌸 Please specify a user to unmute.")
        
    try:
        chat = await client.get_chat(message.chat.id)
        await client.restrict_chat_member(message.chat.id, target_id, permissions=chat.permissions)
        await message.reply_text(f"🌸 **Unmuted!** 🗣\n{target_mention} can speak freely again.")
    except Exception as e:
        await message.reply_text(f"🌸 Failed to unmute: `{e}`")

@Client.on_message(filters.command("unban") & filters.group)
@admin_required("can_restrict_members")
@bot_admin_required("can_restrict_members")
async def unban_user(client: Client, message: Message):
    target_id, target_mention, _ = await extract_target(client, message)
    if not target_id: return await message.reply_text("🌸 Please specify a user to unban.")
        
    try:
        # 1. Unban on Telegram
        await client.unban_chat_member(message.chat.id, target_id)
        
        # 2. Delete them from Waguri's Database Shield
        await db.execute("DELETE FROM banned_users WHERE chat_id = ? AND user_id = ?", message.chat.id, target_id)
        
        await message.reply_text(f"🌸 **Unbanned!** ✨\n{target_mention} has been pardoned and removed from the database.")
    except Exception as e:
        await message.reply_text(f"🌸 Failed to unban: `{e}`")

@Client.on_message(filters.command("kick") & filters.group)
@admin_required("can_restrict_members")
@bot_admin_required("can_restrict_members")
async def kick_user(client: Client, message: Message):
    target_id, target_mention, reason = await extract_target(client, message)
    if not target_id: return await message.reply_text("🌸 Please specify a user to kick.")
        
    try:
        try:
            member = await client.get_chat_member(message.chat.id, target_id)
            if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return await message.reply_text("🌸 Cannot kick administrators.")
        except Exception:
            pass
            
        await client.ban_chat_member(message.chat.id, target_id)
        await client.unban_chat_member(message.chat.id, target_id)
        
        text = f"🌸 **Kicked!** 🥾\n**Target:** {target_mention}"
        if reason: text += f"\n**Reason:** `{reason}`"
        await message.reply_text(text)
    except Exception as e:
        await message.reply_text(f"🌸 Failed to kick: `{e}`")

# 🔥 THE DOUBLE-LAYER DATABASE SHIELD ENFORCER 🔥
@Client.on_message(filters.new_chat_members, group=20)
async def enforce_banned_users(client: Client, message: Message):
    chat_id = message.chat.id
    for user in message.new_chat_members:
        # Check if the user is in our database blacklist
        record = await db.fetchone("SELECT reason FROM banned_users WHERE chat_id = ? AND user_id = ?", chat_id, user.id)
        
        if record:
            try:
                # INSTANTLY ban them again before they can even speak
                await client.ban_chat_member(chat_id, user.id)
                await message.reply_text(f"🌸 **Database Shield Triggered!** 🛡\n{user.mention} tried to sneak back in, but they are permanently stored in my ban records. Action denied.")
            except Exception:
                pass
