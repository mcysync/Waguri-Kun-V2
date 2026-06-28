import logging
import random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions, CallbackQuery

from utils import admin_required, bot_admin_required
from modules.database import db

logger = logging.getLogger("WaguriBot.Captcha")

async def init_captcha_db():
    await db.execute("""
        CREATE TABLE IF NOT EXISTS captcha_settings (
            chat_id INTEGER PRIMARY KEY,
            is_enabled BOOLEAN DEFAULT 0,
            mode TEXT DEFAULT 'button'
        )
    """)

import asyncio
asyncio.get_event_loop().create_task(init_captcha_db())

# Pending verifications: {(chat_id, user_id): correct_answer}
pending_verifications = {}

@Client.on_message(filters.command("captcha") & filters.group)
@admin_required("can_restrict_members")
async def toggle_captcha(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.reply_text("🌸 Usage: `/captcha on` or `/captcha off`")
        
    state = args[1].lower() == "on"
    
    await db.execute(
        "INSERT OR REPLACE INTO captcha_settings (chat_id, is_enabled) VALUES (?, ?)",
        message.chat.id, state
    )
    
    status = "activated ✅" if state else "deactivated ❌"
    await message.reply_text(f"🌸 Welcome Captcha has been {status} for this group!")

@Client.on_message(filters.new_chat_members, group=5)
async def captcha_new_member(client: Client, message: Message):
    chat_id = message.chat.id
    
    settings = await db.fetchone("SELECT is_enabled, mode FROM captcha_settings WHERE chat_id = ?", chat_id)
    if not settings or not settings[0]:
        return
        
    mode = settings[1]
    
    for user in message.new_chat_members:
        if user.is_bot or user.id == client.me.id:
            continue
            
        try:
            # Mute the user pending verification
            await client.restrict_chat_member(
                chat_id,
                user.id,
                ChatPermissions(can_send_messages=False)
            )
            
            # Simple button captcha
            if mode == "button":
                correct_id = f"captcayes_{user.id}"
                wrong_id = f"captchano_{user.id}"
                
                buttons = [
                    InlineKeyboardButton("🌸 I am Human", callback_data=correct_id),
                    InlineKeyboardButton("🤖 I am Bot", callback_data=wrong_id)
                ]
                random.shuffle(buttons)
                
                markup = InlineKeyboardMarkup([buttons])
                
                msg = await message.reply_text(
                    f"🌸 Hello {user.mention}! Welcome to the group.\n\nPlease verify that you are human to speak.",
                    reply_markup=markup
                )
                
                pending_verifications[(chat_id, user.id)] = {"msg_id": msg.id}
                
        except Exception as e:
            logger.error(f"Captcha mute error: {e}")

@Client.on_callback_query(filters.regex(r"^captca(yes|no)_(\d+)$"))
async def captcha_callback(client: Client, callback_query: CallbackQuery):
    match = callback_query.matches[0]
    action = match.group(1)
    target_id = int(match.group(2))
    
    if callback_query.from_user.id != target_id:
        return await callback_query.answer("🌸 This is not your captcha!", show_alert=True)
        
    chat_id = callback_query.message.chat.id
    
    if action == "yes":
        try:
            chat = await client.get_chat(chat_id)
            await client.restrict_chat_member(
                chat_id,
                target_id,
                chat.permissions
            )
            await callback_query.answer("🌸 Verified! You can now chat.", show_alert=True)
            await callback_query.message.delete()
            if (chat_id, target_id) in pending_verifications:
                del pending_verifications[(chat_id, target_id)]
        except Exception as e:
            await callback_query.answer("Failed to unmute. Contact admin.", show_alert=True)
    else:
        try:
            await client.ban_chat_member(chat_id, target_id)
            await callback_query.message.edit_text("🌸 Verification failed. User banned.")
        except Exception:
            await callback_query.answer("Error executing action.", show_alert=True)
