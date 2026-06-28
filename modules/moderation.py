import logging
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserAdminInvalid, PeerIdInvalid, RightForbidden

from utils import admin_required, bot_admin_required, extract_user, parse_time

logger = logging.getLogger("WaguriBot.Moderation")

@Client.on_message(filters.command(["ban", "tban", "sban", "shadowban"]) & filters.group)
@admin_required("can_restrict_members")
@bot_admin_required("can_restrict_members")
async def ban_user(client: Client, message: Message):
    cmd = message.command[0].lower()
    user_id, reason = extract_user(message)
    
    if not user_id:
        return await message.reply_text("🌸 Please reply to a user or provide their ID to ban them.")
        
    user_mention = str(user_id)
    
    try:
        # Try to resolve user nicely
        user = await client.get_users(user_id)
        user_id = user.id
        user_mention = user.mention
        if user.id == client.me.id:
            return await message.reply_text("🌸 I can't ban myself! Baka!")
    except PeerIdInvalid:
        pass # It's probably a channel sender ID, we proceed with raw ID!
    except Exception:
        pass 
        
    try:
        member = await client.get_chat_member(message.chat.id, user_id)
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("🌸 I can't ban an administrator.")
    except Exception:
        pass # User left or is anonymous, we can still ban them
        
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
            else:
                return await message.reply_text("🌸 Invalid time! Use `1d`, `2h`, `30m`.")

    is_silent = cmd in ["sban", "shadowban"]
    
    try:
        await client.ban_chat_member(message.chat.id, user_id, until_date=ban_time)
        
        if not is_silent:
            reply_text = f"🌸 **Banned!** 🔨\n**Target:** {user_mention}{duration_text}\n**Admin:** {message.from_user.mention}"
            if reason: reply_text += f"\n**Reason:** `{reason}`"
            await message.reply_text(reply_text)
        else:
            await message.delete()
            if message.reply_to_message: await message.reply_to_message.delete()
            
    except UserAdminInvalid:
        await message.reply_text("🌸 I cannot ban an admin.")
    except RightForbidden:
        await message.reply_text("🌸 I don't have enough rights to ban this user.")
    except Exception as e:
        await message.reply_text(f"🌸 Failed to ban: `{e}`")

@Client.on_message(filters.command(["mute", "tmute", "smute"]) & filters.group)
@admin_required("can_restrict_members")
@bot_admin_required("can_restrict_members")
async def mute_user(client: Client, message: Message):
    cmd = message.command[0].lower()
    user_id, reason = extract_user(message)
    
    if not user_id:
        return await message.reply_text("🌸 Please reply to a user or provide their ID to mute them.")
        
    user_mention = str(user_id)
    try:
        user = await client.get_users(user_id)
        user_id = user.id
        user_mention = user.mention
    except Exception:
        pass
        
    try:
        member = await client.get_chat_member(message.chat.id, user_id)
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
    
    try:
        await client.restrict_chat_member(message.chat.id, user_id, permissions, until_date=mute_time)
        
        if not is_silent:
            reply_text = f"🌸 **Muted!** 🤐\n**Target:** {user_mention}{duration_text}\n**Admin:** {message.from_user.mention}"
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
    user_id, _ = extract_user(message)
    if not user_id: return await message.reply_text("🌸 Please specify a user to unmute.")
        
    try:
        chat = await client.get_chat(message.chat.id)
        await client.restrict_chat_member(message.chat.id, user_id, permissions=chat.permissions)
        await message.reply_text(f"🌸 **Unmuted!** 🗣\nTarget can speak freely again.")
    except Exception as e:
        await message.reply_text(f"🌸 Failed to unmute: `{e}`")

@Client.on_message(filters.command("unban") & filters.group)
@admin_required("can_restrict_members")
@bot_admin_required("can_restrict_members")
async def unban_user(client: Client, message: Message):
    user_id, _ = extract_user(message)
    if not user_id: return await message.reply_text("🌸 Please specify a user to unban.")
        
    try:
        await client.unban_chat_member(message.chat.id, user_id)
        await message.reply_text(f"🌸 **Unbanned!** ✨\nWelcome back to society!")
    except Exception as e:
        await message.reply_text(f"🌸 Failed to unban: `{e}`")

@Client.on_message(filters.command("kick") & filters.group)
@admin_required("can_restrict_members")
@bot_admin_required("can_restrict_members")
async def kick_user(client: Client, message: Message):
    user_id, reason = extract_user(message)
    if not user_id: return await message.reply_text("🌸 Please specify a user to kick.")
        
    try:
        try:
            member = await client.get_chat_member(message.chat.id, user_id)
            if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return await message.reply_text("🌸 Cannot kick administrators.")
        except Exception:
            pass
            
        await client.ban_chat_member(message.chat.id, user_id)
        await client.unban_chat_member(message.chat.id, user_id)
        
        text = f"🌸 **Kicked!** 🥾\n**Target:** `{user_id}`"
        if reason: text += f"\n**Reason:** `{reason}`"
        await message.reply_text(text)
    except Exception as e:
        await message.reply_text(f"🌸 Failed to kick: `{e}`")
