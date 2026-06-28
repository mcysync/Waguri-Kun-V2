import logging
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import admin_required, extract_user
from modules.database import db

logger = logging.getLogger("WaguriBot.Verification")

async def init_verify_db():
    await db.execute("""
        CREATE TABLE IF NOT EXISTS verified_users (
            user_id INTEGER PRIMARY KEY,
            admin_id INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

import asyncio
asyncio.get_event_loop().create_task(init_verify_db())

@Client.on_message(filters.command("verify") & filters.group)
@admin_required("can_restrict_members")
async def verify_user(client: Client, message: Message):
    user_id, _ = extract_user(message)
    if not user_id:
        return await message.reply_text("🌸 Reply to a user to give them a Verification Badge.")
        
    try:
        user = await client.get_users(user_id)
        
        await db.execute(
            "INSERT OR REPLACE INTO verified_users (user_id, admin_id) VALUES (?, ?)",
            user.id, message.from_user.id
        )
        
        await message.reply_text(f"🌸 **Officially Verified!** ✅\n{user.mention} has been granted a verification badge by {message.from_user.mention}.")
    except Exception as e:
        logger.error(f"Verify error: {e}")
        await message.reply_text("🌸 Failed to verify the user.")

@Client.on_message(filters.command("unverify") & filters.group)
@admin_required("can_restrict_members")
async def unverify_user(client: Client, message: Message):
    user_id, _ = extract_user(message)
    if not user_id:
        return await message.reply_text("🌸 Reply to a user to strip their Verification Badge.")
        
    await db.execute("DELETE FROM verified_users WHERE user_id = ?", user_id)
    await message.reply_text(f"🌸 **Verification Revoked!** ❌\nBadge removed successfully.")

@Client.on_message(filters.command("isverified") & filters.group)
async def check_verified(client: Client, message: Message):
    user_id, _ = extract_user(message)
    target = user_id if user_id else message.from_user.id
    
    record = await db.fetchone("SELECT timestamp FROM verified_users WHERE user_id = ?", target)
    
    try:
        user = await client.get_users(target)
        if record:
            await message.reply_text(f"🌸 {user.mention} is **Verified**! ✅\nSince: `{record[0]}`")
        else:
            await message.reply_text(f"🌸 {user.mention} is **NOT** Verified. ❌")
    except Exception:
        await message.reply_text("🌸 Could not fetch user data.")
