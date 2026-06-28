import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import UserAdminInvalid, ChatAdminRequired, RightForbidden

from utils import admin_required, bot_admin_required, extract_user

logger = logging.getLogger("WaguriBot.Admin")

@Client.on_message(filters.command("promote") & filters.group)
@admin_required("can_promote_members")
@bot_admin_required("can_promote_members")
async def promote_user(client: Client, message: Message):
    user_id, title = extract_user(message)
    
    if not user_id:
        return await message.reply_text("🌸 Please reply to a user or specify their ID/username to promote them.")
        
    try:
        user = await client.get_users(user_id)
        bot_status = await client.get_chat_member(message.chat.id, "me")
        
        # Check bot permissions carefully
        await client.promote_chat_member(
            message.chat.id, 
            user.id,
            privileges=bot_status.privileges
        )
        
        if title:
            await client.set_administrator_title(message.chat.id, user.id, title[:16])
            
        await message.reply_text(f"🌸 Yay! Successfully promoted **{user.first_name}** to admin!\nTitle: `{title or 'Admin'}`")
    except RightForbidden:
        await message.reply_text("🌸 I don't have enough rights to promote this user.")
    except Exception as e:
        logger.error(f"Promote error: {e}")
        await message.reply_text("🌸 Failed to promote the user. They might already be an admin or I don't have the proper permissions.")

@Client.on_message(filters.command("demote") & filters.group)
@admin_required("can_promote_members")
@bot_admin_required("can_promote_members")
async def demote_user(client: Client, message: Message):
    user_id, _ = extract_user(message)
    
    if not user_id:
        return await message.reply_text("🌸 Please reply to an admin or specify their ID/username to demote them.")
        
    try:
        user = await client.get_users(user_id)
        
        # Determine if we can demote them
        member = await client.get_chat_member(message.chat.id, user.id)
        if member.status == "creator":
            return await message.reply_text("🌸 I can't demote the group creator, silly!")
            
        await client.promote_chat_member(
            message.chat.id, 
            user.id,
            is_anonymous=False,
            can_manage_chat=False,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False
        )
        await message.reply_text(f"🌸 Done! **{user.first_name}** has been stripped of their admin privileges.")
    except RightForbidden:
        await message.reply_text("🌸 I can't demote an admin who was promoted by someone else with higher privileges.")
    except Exception as e:
        logger.error(f"Demote error: {e}")
        await message.reply_text("🌸 Oops! Something went wrong while trying to demote.")

@Client.on_message(filters.command(["pin", "unpin", "unpinall"]) & filters.group)
@admin_required("can_pin_messages")
@bot_admin_required("can_pin_messages")
async def pin_handler(client: Client, message: Message):
    cmd = message.command[0].lower()
    
    if cmd == "pin":
        if not message.reply_to_message:
            return await message.reply_text("🌸 Reply to a message to pin it!")
        notify = "silent" not in message.text.lower()
        await message.reply_to_message.pin(disable_notification=not notify)
        await message.reply_text("🌸 Pinned the message successfully!")
        
    elif cmd == "unpin":
        if not message.reply_to_message:
            return await message.reply_text("🌸 Reply to a message to unpin it!")
        await message.reply_to_message.unpin()
        await message.reply_text("🌸 Message unpinned.")
        
    elif cmd == "unpinall":
        await client.unpin_all_chat_messages(message.chat.id)
        await message.reply_text("🌸 Cleared! All messages have been unpinned.")

@Client.on_message(filters.command("purge") & filters.group)
@admin_required("can_delete_messages")
@bot_admin_required("can_delete_messages")
async def purge_messages(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("🌸 Reply to the message where you want the purge to begin.")
        
    start_msg_id = message.reply_to_message.id
    end_msg_id = message.id
    
    message_ids = list(range(start_msg_id, end_msg_id + 1))
    
    try:
        # Pyrogram deletes in chunks of 100
        for i in range(0, len(message_ids), 100):
            chunk = message_ids[i:i + 100]
            await client.delete_messages(message.chat.id, chunk)
            
        msg = await message.reply_text(f"🌸 Purge complete! Deleted `{len(message_ids)}` messages.")
        import asyncio
        await asyncio.sleep(3)
        await msg.delete()
    except Exception as e:
        logger.error(f"Purge error: {e}")
        await message.reply_text("🌸 An error occurred while purging messages.")
