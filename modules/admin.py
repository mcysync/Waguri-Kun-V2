import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import RightForbidden

from utils import admin_required, bot_admin_required, extract_target

logger = logging.getLogger("WaguriBot.Admin")

@Client.on_message(filters.command("promote") & filters.group)
@admin_required("can_promote_members")
@bot_admin_required("can_promote_members")
async def promote_user(client: Client, message: Message):
    target_id, target_mention, title = await extract_target(client, message)
    if not target_id: return await message.reply_text("🌸 Please reply to a user or specify their ID to promote them.")
        
    try:
        bot_status = await client.get_chat_member(message.chat.id, client.me.id)
        await client.promote_chat_member(message.chat.id, target_id, privileges=bot_status.privileges)
        if title:
            await client.set_administrator_title(message.chat.id, target_id, title[:16])
        await message.reply_text(f"🌸 Yay! Successfully promoted {target_mention} to admin!\nTitle: `{title or 'Admin'}`")
    except RightForbidden:
        await message.reply_text("🌸 I don't have enough rights to promote this user.")
    except Exception as e:
        await message.reply_text(f"🌸 Failed to promote: `{e}`")

@Client.on_message(filters.command("demote") & filters.group)
@admin_required("can_promote_members")
@bot_admin_required("can_promote_members")
async def demote_user(client: Client, message: Message):
    target_id, target_mention, _ = await extract_target(client, message)
    if not target_id: return await message.reply_text("🌸 Please reply to an admin or specify their ID to demote them.")
        
    try:
        member = await client.get_chat_member(message.chat.id, target_id)
        if member.status.name == "OWNER": return await message.reply_text("🌸 I can't demote the group creator, silly!")
            
        await client.promote_chat_member(
            message.chat.id, target_id, is_anonymous=False, can_manage_chat=False, can_change_info=False,
            can_post_messages=False, can_edit_messages=False, can_delete_messages=False, can_invite_users=False,
            can_restrict_members=False, can_pin_messages=False, can_promote_members=False
        )
        await message.reply_text(f"🌸 Done! {target_mention} has been stripped of their admin privileges.")
    except RightForbidden:
        await message.reply_text("🌸 I can't demote an admin who was promoted by someone else with higher privileges.")
    except Exception as e:
        await message.reply_text(f"🌸 Failed to demote: `{e}`")

@Client.on_message(filters.command(["pin", "unpin", "unpinall"]) & filters.group)
@admin_required("can_pin_messages")
@bot_admin_required("can_pin_messages")
async def pin_handler(client: Client, message: Message):
    cmd = message.command[0].lower()
    if cmd == "pin":
        if not message.reply_to_message: return await message.reply_text("🌸 Reply to a message to pin it!")
        notify = "silent" not in message.text.lower()
        await message.reply_to_message.pin(disable_notification=not notify)
        await message.reply_text("🌸 Pinned the message successfully!")
    elif cmd == "unpin":
        if not message.reply_to_message: return await message.reply_text("🌸 Reply to a message to unpin it!")
        await message.reply_to_message.unpin()
        await message.reply_text("🌸 Message unpinned.")
    elif cmd == "unpinall":
        await client.unpin_all_chat_messages(message.chat.id)
        await message.reply_text("🌸 Cleared! All messages have been unpinned.")

@Client.on_message(filters.command("purge") & filters.group)
@admin_required("can_delete_messages")
@bot_admin_required("can_delete_messages")
async def purge_messages(client: Client, message: Message):
    if not message.reply_to_message: return await message.reply_text("🌸 Reply to the message where you want the purge to begin.")
    start_msg_id = message.reply_to_message.id
    end_msg_id = message.id
    message_ids = list(range(start_msg_id, end_msg_id + 1))
    try:
        for i in range(0, len(message_ids), 100):
            await client.delete_messages(message.chat.id, message_ids[i:i + 100])
        msg = await message.reply_text(f"🌸 Purge complete! Deleted `{len(message_ids)}` messages.")
        import asyncio
        await asyncio.sleep(3)
        await msg.delete()
    except Exception as e:
        await message.reply_text(f"🌸 An error occurred while purging messages: `{e}`")
