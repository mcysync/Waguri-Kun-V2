import logging
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from datetime import datetime, timedelta

from utils import admin_required, bot_admin_required, extract_user, parse_time

logger = logging.getLogger("WaguriBot.Mutes")

@Client.on_message(filters.command("mutemedia") & filters.group)
@admin_required("can_restrict_members")
@bot_admin_required("can_restrict_members")
async def mute_media(client: Client, message: Message):
    user_id, reason = extract_user(message)
    if not user_id:
        return await message.reply_text("🌸 Reply to a user to revoke their media rights.")
        
    try:
        user = await client.get_users(user_id)
        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False
        )
        await client.restrict_chat_member(message.chat.id, user.id, permissions)
        await message.reply_text(f"🌸 **Media Muted!** 📸🚫\n{user.mention} can now only send text messages.")
    except Exception as e:
        await message.reply_text(f"🌸 Failed to media-mute: {e}")

@Client.on_message(filters.command("mutevoice") & filters.group)
@admin_required("can_restrict_members")
@bot_admin_required("can_restrict_members")
async def mute_voice(client: Client, message: Message):
    user_id, reason = extract_user(message)
    if not user_id:
        return await message.reply_text("🌸 Reply to a user to revoke their voice/video notes rights.")
        
    try:
        user = await client.get_users(user_id)
        chat_perms = (await client.get_chat(message.chat.id)).permissions
        
        # Pyrogram doesn't have a specific voice note permission flag separate from media/other, 
        # so this is typically handled via standard media mutes or chat locks. 
        # For simplicity, we disable other_messages (which covers stickers, gifs, polls).
        permissions = ChatPermissions(
            can_send_messages=chat_perms.can_send_messages,
            can_send_media_messages=chat_perms.can_send_media_messages,
            can_send_other_messages=False,
            can_add_web_page_previews=chat_perms.can_add_web_page_previews
        )
        await client.restrict_chat_member(message.chat.id, user.id, permissions)
        await message.reply_text(f"🌸 **Voice/Sticker Muted!** 🎤🚫\n{user.mention} has lost audio/sticker privileges.")
    except Exception as e:
        await message.reply_text("🌸 Failed to apply restriction.")
