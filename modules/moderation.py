import logging
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.enums import ChatMemberStatus
from pyrogram.raw import functions, types

from utils import admin_required, bot_admin_required, extract_target, parse_time

logger = logging.getLogger("WaguriBot.Moderation")

@Client.on_message(filters.command(["ban", "tban", "sban"]) & filters.group)
@admin_required("can_restrict_members")
@bot_admin_required("can_restrict_members")
async def ban_user(client: Client, message: Message):
    cmd = message.command[0].lower()
    target_id, target_mention, reason = await extract_target(client, message)
    if not target_id: return await message.reply_text("🌸 Please reply to a user, or type their `@username` or `ID`.")
    if target_id == client.me.id: return await message.reply_text("🌸 I can't ban myself! Baka!")
        
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
    except AttributeError:
        # 🔥 THE RAW MTPROTO FALLBACK: Bypasses the NoneType to_bytes crash!
        try:
            peer = await client.resolve_peer(target_id)
            chat_peer = await client.resolve_peer(message.chat.id)
            until = int(ban_time.timestamp()) if ban_time else 0
            banned_rights = types.ChatBannedRights(until_date=until, view_messages=True, send_messages=True, send_media=True, send_stickers=True, send_gifs=True, send_games=True, send_inline=True, embed_links=True)
            await client.invoke(functions.channels.EditBanned(channel=chat_peer, participant=peer, banned_rights=banned_rights))
        except Exception as raw_e:
            return await message.reply_text(f"🌸 API Error: Telegram servers cannot find this user. Have they spoken here recently? (`{raw_e}`)")
    except Exception as e:
        return await message.reply_text(f"🌸 Failed to ban: `{e}`")

    if cmd != "sban":
        reply_text = f"🌸 **Banned!** 🔨\n**Target:** {target_mention}\n**Admin:** {admin_name}"
        if reason: reply_text += f"\n**Reason:** `{reason}`"
        await message.reply_text(reply_text)
    else:
        await message.delete()

@Client.on_message(filters.command(["mute", "tmute", "smute"]) & filters.group)
@admin_required("can_restrict_members")
@bot_admin_required("can_restrict_members")
async def mute_user(client: Client, message: Message):
    cmd = message.command[0].lower()
    target_id, target_mention, reason = await extract_target(client, message)
    if not target_id: return await message.reply_text("🌸 Please reply to a user, or type their `@username` or `ID`.")
        
    mute_time = None
    if cmd == "tmute":
        args = message.text.split()
        time_idx = 1 if message.reply_to_message else 2
        if len(args) > time_idx:
            parsed = parse_time(args[time_idx])
            if parsed:
                mute_time = datetime.now() + timedelta(seconds=parsed)
                reason = " ".join(args[time_idx+1:])

    admin_name = message.from_user.mention if message.from_user else "Admin"
    
    try:
        permissions = ChatPermissions(can_send_messages=False, can_send_media_messages=False, can_send_other_messages=False)
        await client.restrict_chat_member(chat_id=message.chat.id, user_id=target_id, permissions=permissions, until_date=mute_time)
    except AttributeError:
        # 🔥 THE RAW MTPROTO FALLBACK
        try:
            peer = await client.resolve_peer(target_id)
            chat_peer = await client.resolve_peer(message.chat.id)
            until = int(mute_time.timestamp()) if mute_time else 0
            banned_rights = types.ChatBannedRights(until_date=until, view_messages=False, send_messages=True, send_media=True, send_stickers=True, send_gifs=True, send_games=True, send_inline=True, embed_links=True)
            await client.invoke(functions.channels.EditBanned(channel=chat_peer, participant=peer, banned_rights=banned_rights))
        except Exception as raw_e:
            return await message.reply_text(f"🌸 API Error: Telegram servers cannot find this user. (`{raw_e}`)")
    except Exception as e:
        return await message.reply_text(f"🌸 Failed to mute: `{e}`")

    if cmd != "smute":
        reply_text = f"🌸 **Muted!** 🤐\n**Target:** {target_mention}\n**Admin:** {admin_name}"
        if reason: reply_text += f"\n**Reason:** `{reason}`"
        await message.reply_text(reply_text)
    else:
        await message.delete()

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
        await client.ban_chat_member(message.chat.id, target_id)
        await client.unban_chat_member(message.chat.id, target_id)
        text = f"🌸 **Kicked!** 🥾\n**Target:** {target_mention}"
        if reason: text += f"\n**Reason:** `{reason}`"
        await message.reply_text(text)
    except Exception as e:
        await message.reply_text(f"🌸 Failed to kick: `{e}`")
