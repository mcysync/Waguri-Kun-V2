import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from utils import admin_required
from modules.database import db

logger = logging.getLogger("WaguriBot.Settings")

async def get_settings_keyboard(chat_id: int):
    # Fetch all toggles
    set_record = await db.fetchone("SELECT antispam_enabled, welcomes_enabled FROM settings WHERE chat_id = ?", chat_id)
    as_enabled = set_record[0] if set_record else 1
    wl_enabled = set_record[1] if set_record else 1
    
    raid_record = await db.fetchone("SELECT is_active FROM raid_settings WHERE chat_id = ?", chat_id)
    raid_enabled = raid_record[0] if raid_record else 0
    
    sec_record = await db.fetchone("SELECT file_scan, scam_detect FROM security_settings WHERE chat_id = ?", chat_id)
    fs_enabled = sec_record[0] if sec_record else 1
    sd_enabled = sec_record[1] if sec_record else 1
    
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"Anti-Spam: {'✅' if as_enabled else '❌'}", callback_data="set_antispam"),
            InlineKeyboardButton(f"Welcomes: {'✅' if wl_enabled else '❌'}", callback_data="set_welcomes")
        ],
        [
            InlineKeyboardButton(f"Raid Mode: {'🚨' if raid_enabled else '❌'}", callback_data="set_raid"),
            InlineKeyboardButton(f"File Scan: {'✅' if fs_enabled else '❌'}", callback_data="set_filescan")
        ],
        [
            InlineKeyboardButton(f"Scam Detect: {'✅' if sd_enabled else '❌'}", callback_data="set_scamdetect"),
            InlineKeyboardButton("❌ Close", callback_data="set_close")
        ]
    ])

@Client.on_message(filters.command("settings") & filters.group)
@admin_required("can_change_info")
async def show_settings(client: Client, message: Message):
    await db.execute("INSERT OR IGNORE INTO chats (chat_id, title) VALUES (?, ?)", message.chat.id, message.chat.title)
    
    keyboard = await get_settings_keyboard(message.chat.id)
    await message.reply_text(
        "🌸 **Waguri Group Control Panel** 🌸\n\n"
        "Tap the buttons below to toggle various protection and utility features for this group.",
        reply_markup=keyboard
    )

@Client.on_callback_query(filters.regex(r"^set_"))
async def settings_callback(client: Client, callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    
    # Admin check
    try:
        member = await client.get_chat_member(chat_id, user_id)
        if member.status not in ["administrator", "creator"]:
            return await callback_query.answer("🌸 Only admins can change these settings!", show_alert=True)
    except Exception:
        return await callback_query.answer("Failed to verify admin status.", show_alert=True)
        
    action = callback_query.data
    
    if action == "set_close":
        await callback_query.message.delete()
        return
        
    if action == "set_antispam":
        await db.execute("UPDATE settings SET antispam_enabled = NOT antispam_enabled WHERE chat_id = ?", chat_id)
    elif action == "set_welcomes":
        await db.execute("UPDATE settings SET welcomes_enabled = NOT welcomes_enabled WHERE chat_id = ?", chat_id)
    elif action == "set_raid":
        await db.execute("INSERT OR IGNORE INTO raid_settings (chat_id) VALUES (?)", chat_id)
        await db.execute("UPDATE raid_settings SET is_active = NOT is_active WHERE chat_id = ?", chat_id)
    elif action == "set_filescan":
        await db.execute("INSERT OR IGNORE INTO security_settings (chat_id) VALUES (?)", chat_id)
        await db.execute("UPDATE security_settings SET file_scan = NOT file_scan WHERE chat_id = ?", chat_id)
    elif action == "set_scamdetect":
        await db.execute("INSERT OR IGNORE INTO security_settings (chat_id) VALUES (?)", chat_id)
        await db.execute("UPDATE security_settings SET scam_detect = NOT scam_detect WHERE chat_id = ?", chat_id)

    # Refresh keyboard
    keyboard = await get_settings_keyboard(chat_id)
    await callback_query.message.edit_reply_markup(reply_markup=keyboard)
    await callback_query.answer("Setting updated!")
