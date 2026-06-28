import time
import logging
from datetime import datetime, timedelta

from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.errors import UserAdminInvalid, RightForbidden, RPCError

from utils import admin_required, bot_admin_required, extract_user, parse_time
from modules.database import db

logger = logging.getLogger("WaguriBot.Moderation")

@Client.on_message(filters.command(["ban", "tban", "sban", "shadowban"]) & filters.group)
@admin_required("can_restrict_members")
@bot_admin_required("can_restrict_members")
async def ban_user(client: Client, message: Message):
    cmd = message.command[0].lower()
    user_id, reason = extract_user(message)
    
    if not user_id:
        return await message.reply_text("🌸 Please reply to a user or provide their ID to ban them.")
        
    if user_id == client.me.id:
        return await message.reply_text("🌸 I can't ban myself! Baka!")
        
    try:
        user = await client.get_users(user_id)
        member = await client.get_chat_member(message.chat.id, user.id)
        
        if member.status in ["administrator", "creator"]:
            return await message.reply_text("🌸 I can't take action against an administrator.")
            
        ban_time = None
        duration_text = ""
        
        if cmd == "tban":
            args = message.text.split()
            if len(args) < 3 and not message.reply_to_message:
                return await message.reply_text("🌸 Usage: /tban [time] [reason] (as reply) OR /tban @user [time] [reason]")
            
            time_idx = 1 if message.reply_to_message else 2
            if len(args) > time_idx:
                parsed_time = parse_time(args[time_idx])
                if parsed_time:
                    ban_time = datetime.now() + timedelta(seconds=parsed_time)
                    duration_text = f" for {args[time_idx]}"
                    reason = " ".join(args[time_idx+1:])
                else:
                    return await message.reply_text("🌸 Invalid time format! Use something like `1d`, `2h`, `30m`.")

        is_silent = cmd in ["sban", "shadowban"]
        
        await client.ban_chat_member(message.chat.id, user.id, until_date=ban_time)
        
        if not is_silent:
            reply_text = f"🌸 **Banned!** 🔨\n**User:** {user.mention}{duration_text}\n**Admin:** {message.from_user.mention}"
            if reason:
                reply_text += f"\n**Reason:** `{reason}`"
            await message.reply_text(reply_text)
        else:
            await message.delete()
            if message.reply_to_message:
                await message.reply_to_message.delete()
            
    except RightForbidden:
        await message.reply_text("🌸 I don't have enough privileges to ban this user.")
    except Exception as e:
        logger.error(f"Ban error: {e}")
        await message.reply_text("🌸 Failed to execute ban.")

@Client.on_message(filters.command("unban") & filters.group)
@admin_required("can_restrict_members")
@bot_admin_required("can_restrict_members")
async def unban_user(client: Client, message: Message):
    user_id, reason = extract_user(message)
    if not user_id:
        return await message.reply_text("🌸 Please specify a user to unban.")
        
    try:
        user = await client.get_users(user_id)
        await client.unban_chat_member(message.chat.id, user.id)
        await message.reply_text(f"🌸 **Unbanned!** ✨\n**User:** {user.mention}\nWelcome back to society!")
    except Exception as e:
        await message.reply_text(f"🌸 Failed to unban: {e}")

@Client.on_message(filters.command(["mute", "tmute", "smute"]) & filters.group)
@admin_required("can_restrict_members")
@bot_admin_required("can_restrict_members")
async def mute_user(client: Client, message: Message):
    cmd = message.command[0].lower()
    user_id, reason = extract_user(message)
    
    if not user_id:
        return await message.reply_text("🌸 Please reply to a user or provide their ID to mute them.")
        
    try:
        user = await client.get_users(user_id)
        member = await client.get_chat_member(message.chat.id, user.id)
        
        if member.status in ["administrator", "creator"]:
            return await message.reply_text("🌸 I can't mute an administrator.")
            
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

        permissions = ChatPermissions(can_send_messages=False)
        is_silent = cmd == "smute"
        
        await client.restrict_chat_member(message.chat.id, user.id, permissions, until_date=mute_time)
        
        if not is_silent:
            reply_text = f"🌸 **Muted!** 🤐\n**User:** {user.mention}{duration_text}\n**Admin:** {message.from_user.mention}"
            if reason:
                reply_text += f"\n**Reason:** `{reason}`"
            await message.reply_text(reply_text)
        else:
            await message.delete()
            
    except Exception as e:
        logger.error(f"Mute error: {e}")
        await message.reply_text("🌸 Failed to mute the user.")

@Client.on_message(filters.command("unmute") & filters.group)
@admin_required("can_restrict_members")
@bot_admin_required("can_restrict_members")
async def unmute_user(client: Client, message: Message):
    user_id, _ = extract_user(message)
    if not user_id:
        return await message.reply_text("🌸 Please specify a user to unmute.")
        
    try:
        user = await client.get_users(user_id)
        # Restore normal permissions based on group defaults, but un-restricting generally works
        chat = await client.get_chat(message.chat.id)
        await client.restrict_chat_member(
            message.chat.id, 
            user.id, 
            permissions=chat.permissions
        )
        await message.reply_text(f"🌸 **Unmuted!** 🗣\n**User:** {user.mention} can speak freely again.")
    except Exception as e:
        await message.reply_text(f"🌸 Failed to unmute: {e}")

@Client.on_message(filters.command("kick") & filters.group)
@admin_required("can_restrict_members")
@bot_admin_required("can_restrict_members")
async def kick_user(client: Client, message: Message):
    user_id, reason = extract_user(message)
    if not user_id:
        return await message.reply_text("🌸 Please specify a user to kick.")
        
    try:
        user = await client.get_users(user_id)
        member = await client.get_chat_member(message.chat.id, user.id)
        if member.status in ["administrator", "creator"]:
            return await message.reply_text("🌸 Cannot kick administrators.")
            
        # Ban and immediately unban to act as a kick
        await client.ban_chat_member(message.chat.id, user.id)
        await client.unban_chat_member(message.chat.id, user.id)
        
        text = f"🌸 **Kicked!** 🥾\n**User:** {user.mention}"
        if reason:
            text += f"\n**Reason:** `{reason}`"
        await message.reply_text(text)
    except Exception as e:
        await message.reply_text("🌸 Failed to kick user.")
