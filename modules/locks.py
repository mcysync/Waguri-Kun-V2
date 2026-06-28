import logging
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions

from utils import admin_required, bot_admin_required
from modules.database import db

logger = logging.getLogger("WaguriBot.Locks")

LOCK_TYPES = {
    "text": "can_send_messages",
    "media": "can_send_media_messages",
    "stickers": "can_send_other_messages",
    "gifs": "can_send_other_messages",
    "polls": "can_send_other_messages",
    "links": "can_add_web_page_previews",
    "all": "all"
}

@Client.on_message(filters.command("lock") & filters.group)
@admin_required("can_restrict_members")
@bot_admin_required("can_restrict_members")
async def lock_chat_item(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.reply_text(f"🌸 What should I lock? Available: `{', '.join(LOCK_TYPES.keys())}`")
        
    lock_target = args[1].lower()
    if lock_target not in LOCK_TYPES:
        return await message.reply_text(f"🌸 Invalid lock type. Available: `{', '.join(LOCK_TYPES.keys())}`")
        
    chat = await client.get_chat(message.chat.id)
    current_perms = chat.permissions
    
    if lock_target == "all":
        new_perms = ChatPermissions(can_send_messages=False)
    else:
        kwargs = {
            "can_send_messages": current_perms.can_send_messages,
            "can_send_media_messages": current_perms.can_send_media_messages,
            "can_send_other_messages": current_perms.can_send_other_messages,
            "can_add_web_page_previews": current_perms.can_add_web_page_previews,
            "can_invite_users": current_perms.can_invite_users,
            "can_pin_messages": current_perms.can_pin_messages,
            "can_change_info": current_perms.can_change_info
        }
        kwargs[LOCK_TYPES[lock_target]] = False
        new_perms = ChatPermissions(**kwargs)
        
    try:
        await client.set_chat_permissions(message.chat.id, new_perms)
        await message.reply_text(f"🌸 Locked `{lock_target}` for this chat! 🔒")
    except Exception as e:
        logger.error(f"Lock error: {e}")
        await message.reply_text("🌸 I failed to lock the chat. Check my permissions.")

@Client.on_message(filters.command("unlock") & filters.group)
@admin_required("can_restrict_members")
@bot_admin_required("can_restrict_members")
async def unlock_chat_item(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.reply_text(f"🌸 What should I unlock? Available: `{', '.join(LOCK_TYPES.keys())}`")
        
    unlock_target = args[1].lower()
    if unlock_target not in LOCK_TYPES:
        return await message.reply_text(f"🌸 Invalid unlock type.")
        
    chat = await client.get_chat(message.chat.id)
    current_perms = chat.permissions
    
    if unlock_target == "all":
        new_perms = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
    else:
        kwargs = {
            "can_send_messages": current_perms.can_send_messages,
            "can_send_media_messages": current_perms.can_send_media_messages,
            "can_send_other_messages": current_perms.can_send_other_messages,
            "can_add_web_page_previews": current_perms.can_add_web_page_previews,
            "can_invite_users": current_perms.can_invite_users,
            "can_pin_messages": current_perms.can_pin_messages,
            "can_change_info": current_perms.can_change_info
        }
        kwargs[LOCK_TYPES[unlock_target]] = True
        new_perms = ChatPermissions(**kwargs)
        
    try:
        await client.set_chat_permissions(message.chat.id, new_perms)
        await message.reply_text(f"🌸 Unlocked `{unlock_target}` for this chat! 🔓")
    except Exception as e:
        await message.reply_text("🌸 I failed to unlock. Check my permissions.")

@Client.on_message(filters.command("locks") & filters.group)
async def check_locks(client: Client, message: Message):
    chat = await client.get_chat(message.chat.id)
    perms = chat.permissions
    
    text = "🌸 **Current Chat Permissions:**\n\n"
    text += f"• **Messages:** {'✅' if perms.can_send_messages else '❌'}\n"
    text += f"• **Media:** {'✅' if perms.can_send_media_messages else '❌'}\n"
    text += f"• **Stickers/GIFs:** {'✅' if perms.can_send_other_messages else '❌'}\n"
    text += f"• **Web Previews:** {'✅' if perms.can_add_web_page_previews else '❌'}\n"
    text += f"• **Invites:** {'✅' if perms.can_invite_users else '❌'}\n"
    text += f"• **Pin Messages:** {'✅' if perms.can_pin_messages else '❌'}\n"
    text += f"• **Change Info:** {'✅' if perms.can_change_info else '❌'}\n"
    
    await message.reply_text(text)
