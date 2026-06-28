import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from utils import extract_target

logger = logging.getLogger("WaguriBot.Info")

@Client.on_message(filters.command(["info", "userinfo"]))
async def user_info(client: Client, message: Message):
    target_id, target_mention, _ = await extract_target(client, message)
    
    if not target_id:
        target_id = message.from_user.id if message.from_user else None
        
    if not target_id:
        return await message.reply_text("🌸 I cannot find this user.")
        
    try:
        user = await client.get_users(target_id)
        text = f"🌸 **User Info** 🌸\n\n**ID:** `{user.id}`\n**Name:** {user.first_name} {user.last_name or ''}\n**Username:** @{user.username if user.username else 'None'}\n**Premium:** {'Yes 🌟' if user.is_premium else 'No'}\n**DC ID:** `{user.dc_id or 'Unknown'}`\n\n**Mention:** {user.mention}"
        
        if user.photo:
            async for photo in client.get_chat_photos(user.id, limit=1):
                await message.reply_photo(photo.file_id, caption=text)
                return
                
        await message.reply_text(text)
    except Exception as e:
        await message.reply_text(f"🌸 Could not fetch user info. Try checking someone who has spoken here recently! (`{e}`)")
