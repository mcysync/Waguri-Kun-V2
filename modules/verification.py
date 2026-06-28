import logging
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import admin_required, extract_target
from modules.database import db

logger = logging.getLogger("WaguriBot.Verification")

@Client.on_message(filters.command("verify") & filters.group)
@admin_required("can_restrict_members")
async def verify_user(client: Client, message: Message):
    target_id, target_mention, _ = await extract_target(client, message)
    if not target_id: return await message.reply_text("🌸 Reply to a user to give them a Verification Badge.")
        
    admin_id = message.from_user.id if message.from_user else 0
    try:
        await db.execute("INSERT OR REPLACE INTO verified_users (user_id, admin_id) VALUES (?, ?)", target_id, admin_id)
        admin_name = message.from_user.mention if message.from_user else "Admin"
        await message.reply_text(f"🌸 **Officially Verified!** ✅\n{target_mention} has been granted a verification badge by {admin_name}.")
    except Exception as e:
        await message.reply_text(f"🌸 Failed to verify the user: `{e}`")

@Client.on_message(filters.command("unverify") & filters.group)
@admin_required("can_restrict_members")
async def unverify_user(client: Client, message: Message):
    target_id, target_mention, _ = await extract_target(client, message)
    if not target_id: return await message.reply_text("🌸 Reply to a user to strip their Verification Badge.")
        
    await db.execute("DELETE FROM verified_users WHERE user_id = ?", target_id)
    await message.reply_text(f"🌸 **Verification Revoked!** ❌\nBadge removed from {target_mention}.")

@Client.on_message(filters.command("isverified") & filters.group)
async def check_verified(client: Client, message: Message):
    target_id, target_mention, _ = await extract_target(client, message)
    if not target_id:
        target_id = message.from_user.id if message.from_user else 0
        target_mention = message.from_user.mention if message.from_user else "You"
        
    record = await db.fetchone("SELECT timestamp FROM verified_users WHERE user_id = ?", target_id)
    
    if record:
        await message.reply_text(f"🌸 {target_mention} is **Verified**! ✅\nSince: `{record[0]}`")
    else:
        await message.reply_text(f"🌸 {target_mention} is **NOT** Verified. ❌")
