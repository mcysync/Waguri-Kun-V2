import logging
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.enums import ChatMemberStatus

from utils import admin_required, bot_admin_required, extract_target, parse_time

logger = logging.getLogger("WaguriBot.Moderation")

@Client.on_message(filters.command(["ban", "tban", "sban", "shadowban"]) & filters.group)
@admin_required("can_restrict_members")
@bot_admin_required("can_restrict_members")
async def ban_user(client: Client, message: Message):
    cmd = message.command[0].lower()
    target_id, target_mention, reason = await extract_target(client, message)
    
    if not target_id: return await message.reply_text("🌸 I cannot find this user! Reply to them or provide a valid ID.")
    if target_id == client.me.id: return await message.reply_text("🌸 I can't ban myself! Baka!")
        
    try:
        member = await client.get_chat_member(message.chat.id, target_id)
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]: return await message.reply_text("🌸 I can't punish an administrator.")
    except Exception: pass
        
    ban_time = None
    if cmd == "tban":
        args = message.text.split()
        time_idx = 1 if message.reply_to_message else 2
        if len(args) > time_idx:
            parsed = parse_time(args[time_idx])
            if parsed:
                ban_time = datetime.now() + timedelta(seconds=parsed)
                reason = " ".join(args[time_idx+1:])

    admin_name = message.from_user.mention if message.from_user else "Admin"
    
    try:
        await client.ban_chat_member(chat_id=message.chat.id, user_id=target_id, until_date=ban_time)
        if cmd not in ["sban", "shadowban"]:
            reply_text = f"🌸 **Banned!** 🔨\n**Target:** {target_mention}\n**Admin:** {admin_name}"
            if reason: reply_text += f"\n**Reason:** `{reason}`"
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
    
    if not target_id: return await message.reply_text("🌸 I cannot find this user! Reply to them or provide a valid ID.")
        
    try:
        member = await client.get_chat_member(message.chat.id, target_id)
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]: return await message.reply_text("🌸 I can't punish an administrator.")
    except Exception: pass
        
    mute_time = None
    if cmd == "tmute":
        args = message.text.split()
        time_idx = 1 if message.reply_to_message else 2
        if len(args) > time_idx:
            parsed = parse_time(args[time_idx])
            if parsed:
                mute_time = datetime.now() + timedelta(seconds=parsed)
                reason = " ".join(args[time_idx+1:])

    permissions = ChatPermissions(can_send_messages=False, can_send_media_messages=False, can_send_other_messages=False)
    admin_name = message.from_user.mention if message.from_user else "Admin"
    
    try:
        await client.restrict_chat_member(chat_id=message.chat.id, user_id=target_id, permissions=permissions, until_date=mute_time)
        if cmd != "smute":
            reply_text = f"🌸 **Muted!** 🤐\n**Target:** {target_mention}\n**Admin:** {admin_name}"
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
    if not target_id: return await message.reply_text("🌸 Please specify a user.")
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
    if not target_id: return await message.reply_text("🌸 Please specify a user.")
    try:
        await client.unban_chat_member(message.chat.id, target_id)
        await message.reply_text(f"🌸 **Unbanned!** ✨\n{target_mention} has been unbanned.")
    except Exception as e:
        await message.reply_text(f"🌸 Failed to unban: `{e}`")

@Client.on_message(filters.command("kick") & filters.group)
@admin_required("can_restrict_members")
@bot_admin_required("can_restrict_members")
async def kick_user(client: Client, message: Message):
    target_id, target_mention, reason = await extract_target(client, message)
    if not target_id: return await message.reply_text("🌸 Please specify a user.")
    try:
        try:
            member = await client.get_chat_member(message.chat.id, target_id)
            if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]: return await message.reply_text("🌸 Cannot kick administrators.")
        except Exception: pass
            
        await client.ban_chat_member(message.chat.id, target_id)
        await client.unban_chat_member(message.chat.id, target_id)
        text = f"🌸 **Kicked!** 🥾\n**Target:** {target_mention}"
        if reason: text += f"\n**Reason:** `{reason}`"
        await message.reply_text(text)
    except Exception as e:
        await message.reply_text(f"🌸 Failed to kick: `{e}`")
