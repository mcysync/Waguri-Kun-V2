import logging
from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio

from utils import admin_required

logger = logging.getLogger("WaguriBot.Tags")

@Client.on_message(filters.command(["tagall", "mentionall", "all"]) & filters.group)
@admin_required("can_restrict_members")
async def tag_all(client: Client, message: Message):
    args = message.text.split(None, 1)
    custom_msg = args[1] if len(args) > 1 else "🌸 Wake up, everyone!"
    
    await message.reply_text(f"🌸 Gathering everyone... This might take a moment!")
    
    members = []
    async for member in client.get_chat_members(message.chat.id):
        if not member.user.is_bot and not member.user.is_deleted:
            members.append(member.user)
            
    if not members:
        return await message.reply_text("🌸 No users found to tag!")
        
    # Chunk tagging to avoid huge messages (Telegram max entity limit)
    chunk_size = 5
    for i in range(0, len(members), chunk_size):
        chunk = members[i:i + chunk_size]
        text = f"{custom_msg}\n\n"
        for user in chunk:
            text += f"• [‎](tg://user?id={user.id}){user.first_name}\n"
            
        await client.send_message(message.chat.id, text)
        await asyncio.sleep(2) # Prevent flood waits
        
@Client.on_message(filters.command(["stopall", "cancelall"]) & filters.group)
@admin_required("can_restrict_members")
async def stop_all_tags(client: Client, message: Message):
    # For a fully abortable system we would use global task cancellation flags.
    # For now, we notify the user.
    await message.reply_text("🌸 Tagging queue is processed synchronously in chunks. Currently active tags will finish shortly.")
