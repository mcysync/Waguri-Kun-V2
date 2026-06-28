import logging
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions

from utils import admin_required, bot_admin_required, extract_target

logger = logging.getLogger("WaguriBot.Mutes")

@Client.on_message(filters.command("mutemedia") & filters.group)
@admin_required("can_restrict_members")
@bot_admin_required("can_restrict_members")
async def mute_media(client: Client, message: Message):
    target_id, target_mention, _ = await extract_target(client, message)
    if not target_id: return await message.reply_text("🌸 Reply to a user to revoke their media rights.")
        
    try:
        permissions = ChatPermissions(can_send_messages=True, can_send_media_messages=False, can_send_other_messages=False, can_add_web_page_previews=False)
        await client.restrict_chat_member(message.chat.id, target_id, permissions)
        await message.reply_text(f"🌸 **Media Muted!** 📸🚫\n{target_mention} can now only send text messages.")
    except Exception as e:
        await message.reply_text(f"🌸 Failed to media-mute: `{e}`")

@Client.on_message(filters.command("mutevoice") & filters.group)
@admin_required("can_restrict_members")
@bot_admin_required("can_restrict_members")
async def mute_voice(client: Client, message: Message):
    target_id, target_mention, _ = await extract_target(client, message)
    if not target_id: return await message.reply_text("🌸 Reply to a user to revoke their voice/video notes rights.")
        
    try:
        chat_perms = (await client.get_chat(message.chat.id)).permissions
        permissions = ChatPermissions(can_send_messages=chat_perms.can_send_messages, can_send_media_messages=chat_perms.can_send_media_messages, can_send_other_messages=False, can_add_web_page_previews=chat_perms.can_add_web_page_previews)
        await client.restrict_chat_member(message.chat.id, target_id, permissions)
        await message.reply_text(f"🌸 **Voice/Sticker Muted!** 🎤🚫\n{target_mention} has lost audio/sticker privileges.")
    except Exception as e:
        await message.reply_text(f"🌸 Failed to apply restriction: `{e}`")
