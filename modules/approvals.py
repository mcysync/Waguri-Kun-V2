import logging
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import admin_required, extract_user
from modules.database import db

logger = logging.getLogger("WaguriBot.Approvals")

async def init_approvals_db():
    await db.execute("""
        CREATE TABLE IF NOT EXISTS approved_users (
            chat_id INTEGER,
            user_id INTEGER,
            PRIMARY KEY (chat_id, user_id)
        )
    """)

import asyncio
asyncio.get_event_loop().create_task(init_approvals_db())

@Client.on_message(filters.command("approve") & filters.group)
@admin_required("can_restrict_members")
async def approve_user(client: Client, message: Message):
    user_id, _ = extract_user(message)
    if not user_id:
        return await message.reply_text("🌸 Reply to a user to approve them.")
        
    await db.execute(
        "INSERT OR REPLACE INTO approved_users (chat_id, user_id) VALUES (?, ?)",
        message.chat.id, user_id
    )
    
    await message.reply_text(f"🌸 Approved `{user_id}`! They are now an officially recognized member.")

@Client.on_message(filters.command("disapprove") & filters.group)
@admin_required("can_restrict_members")
async def disapprove_user(client: Client, message: Message):
    user_id, _ = extract_user(message)
    if not user_id:
        return await message.reply_text("🌸 Reply to a user to disapprove them.")
        
    await db.execute("DELETE FROM approved_users WHERE chat_id = ? AND user_id = ?", message.chat.id, user_id)
    await message.reply_text(f"🌸 Disapproved `{user_id}`. Recognition revoked.")
