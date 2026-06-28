import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from utils import extract_target

logger = logging.getLogger("WaguriBot.Info")

@Client.on_message(filters.command(["info", "userinfo"]))
async def user_info(client: Client, message: Message):
    target_id, target_mention, _ = await extract_target(client, message)
    
    # If no target is given, check the person who sent the command
    if not target_id:
        target_id = message.from_user.id if message.from_user else None
        
    if not target_id:
        return await message.reply_text("🌸 I cannot find this user.")
        
    try:
        # Fetch their full profile from Telegram
        user = await client.get_users(target_id)
        
        text = f"🌸 **User Info** 🌸\n\n"
        text += f"**ID:** `{user.id}`\n"
        text += f"**Name:** {user.first_name} {user.last_name or ''}\n"
        text += f"**Username:** @{user.username if user.username else 'None'}\n"
        text += f"**Premium:** {'Yes 🌟' if user.is_premium else 'No'}\n"
        text += f"**DC ID:** `{user.dc_id or 'Unknown'}`\n\n"
        text += f"**Mention:** {user.mention}"
        
        # Try to send their profile picture
        if user.photo:
            async for photo in client.get_chat_photos(user.id, limit=1):
                await message.reply_photo(photo.file_id, caption=text)
                return
                
        # If no profile picture, just send text
        await message.reply_text(text)
        
    except Exception as e:
        await message.reply_text(f"🌸 Could not fetch user info: `{e}`")
