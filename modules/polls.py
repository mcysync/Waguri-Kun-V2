import logging
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import admin_required

logger = logging.getLogger("WaguriBot.Polls")

@Client.on_message(filters.command("poll") & filters.group)
@admin_required("can_send_messages")
async def create_poll(client: Client, message: Message):
    args = message.text.split(None, 1)
    if len(args) < 2:
        return await message.reply_text("🌸 Usage: `/poll Question | Option1 | Option2 | ...`")
        
    data = args[1].split("|")
    if len(data) < 3:
        return await message.reply_text("🌸 Please provide a question and at least two options separated by `|`.")
        
    question = data[0].strip()
    options = [opt.strip() for opt in data[1:] if opt.strip()]
    
    if len(options) < 2 or len(options) > 10:
        return await message.reply_text("🌸 A poll needs between 2 and 10 options.")
        
    try:
        await client.send_poll(
            chat_id=message.chat.id,
            question=question,
            options=options,
            is_anonymous=False
        )
        await message.delete()
    except Exception as e:
        logger.error(f"Poll creation error: {e}")
        await message.reply_text("🌸 Failed to create the poll.")
