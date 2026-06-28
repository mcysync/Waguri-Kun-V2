import logging
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import admin_required, extract_target
from modules.database import db

logger = logging.getLogger("WaguriBot.Approvals")

@Client.on_message(filters.command("approve") & filters.group)
@admin_required("can_restrict_members")
async def approve_user(client: Client, message: Message):
    target_id, target_mention, _ = await extract_target(client, message)
    if not target_id: return await message.reply_text("🌸 Reply to a user to approve them.")
        
    await db.execute("INSERT OR REPLACE INTO approved_users (chat_id, user_id) VALUES (?, ?)", message.chat.id, target_id)
    await message.reply_text(f"🌸 Approved {target_mention}! They are now an officially recognized member.")

@Client.on_message(filters.command("disapprove") & filters.group)
@admin_required("can_restrict_members")
async def disapprove_user(client: Client, message: Message):
    target_id, target_mention, _ = await extract_target(client, message)
    if not target_id: return await message.reply_text("🌸 Reply to a user to disapprove them.")
        
    await db.execute("DELETE FROM approved_users WHERE chat_id = ? AND user_id = ?", message.chat.id, target_id)
    await message.reply_text(f"🌸 Disapproved {target_mention}. Recognition revoked.")
