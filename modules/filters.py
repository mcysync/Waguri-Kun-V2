import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from utils import admin_required
from modules.database import db

logger = logging.getLogger("WaguriBot.Filters")

async def get_filter(chat_id: int, name: str):
    query = "SELECT content, file_id, type FROM notes WHERE chat_id = ? AND name = ?"
    return await db.fetchone(query, chat_id, name)

@Client.on_message(filters.command("filter") & filters.group)
@admin_required("can_change_info")
async def add_filter(client: Client, message: Message):
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply_text("🌸 Usage: `/filter [keyword] [reply text/media]`")
        
    args = message.text.split(None, 2)
    
    if len(args) < 2:
        return await message.reply_text("🌸 Please provide a keyword for the filter.")
        
    keyword = args[1].lower()
    
    content = None
    file_id = None
    msg_type = "text"
    
    if message.reply_to_message:
        replied = message.reply_to_message
        if replied.text:
            content = replied.text.markdown
        elif replied.photo:
            msg_type = "photo"
            file_id = replied.photo.file_id
            content = replied.caption.markdown if replied.caption else None
        elif replied.document:
            msg_type = "document"
            file_id = replied.document.file_id
            content = replied.caption.markdown if replied.caption else None
        elif replied.sticker:
            msg_type = "sticker"
            file_id = replied.sticker.file_id
        elif replied.animation:
            msg_type = "animation"
            file_id = replied.animation.file_id
            content = replied.caption.markdown if replied.caption else None
    else:
        if len(args) > 2:
            content = args[2]
        else:
            return await message.reply_text("🌸 You need to provide the content for the filter or reply to a message!")
            
    await db.execute(
        "INSERT OR REPLACE INTO notes (chat_id, name, content, file_id, type) VALUES (?, ?, ?, ?, ?)",
        message.chat.id, keyword, content, file_id, msg_type
    )
    
    await message.reply_text(f"🌸 Filter `{keyword}` saved successfully! I'll watch out for it.")

@Client.on_message(filters.command(["stop", "unfilter"]) & filters.group)
@admin_required("can_change_info")
async def stop_filter(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("🌸 Please provide the keyword of the filter to stop.")
        
    keyword = message.command[1].lower()
    
    existing = await get_filter(message.chat.id, keyword)
    if not existing:
        return await message.reply_text(f"🌸 Filter `{keyword}` doesn't exist here!")
        
    await db.execute("DELETE FROM notes WHERE chat_id = ? AND name = ?", message.chat.id, keyword)
    await message.reply_text(f"🌸 Filter `{keyword}` has been deleted.")

@Client.on_message(filters.command("filters") & filters.group)
async def list_filters(client: Client, message: Message):
    records = await db.fetchall("SELECT name FROM notes WHERE chat_id = ?", message.chat.id)
    
    if not records:
        return await message.reply_text("🌸 There are no active filters in this chat.")
        
    text = "🌸 **Active Filters:**\n\n"
    for r in records:
        text += f"• `{r[0]}`\n"
        
    await message.reply_text(text)

# Listen to all messages in groups to catch filters
@Client.on_message(filters.text & filters.group & ~filters.bot, group=1)
async def filter_watcher(client: Client, message: Message):
    if not message.text or message.text.startswith("/"):
        return
        
    words = set(message.text.lower().split())
    
    # In a highly active group, hitting the DB for every message is slow.
    # For Enterprise production, we would use a Redis/Memcached layer here,
    # but since strictly local DB is requested, we query SQLite directly.
    # Aiosqlite is fast enough for reasonable scale.
    
    records = await db.fetchall("SELECT name, content, file_id, type FROM notes WHERE chat_id = ?", message.chat.id)
    
    for record in records:
        keyword, content, file_id, msg_type = record
        # Simple exact word match
        if keyword in words:
            if msg_type == "text":
                await message.reply_text(content, disable_web_page_preview=True)
            elif msg_type == "photo":
                await message.reply_photo(file_id, caption=content)
            elif msg_type == "document":
                await message.reply_document(file_id, caption=content)
            elif msg_type == "sticker":
                await message.reply_sticker(file_id)
            elif msg_type == "animation":
                await message.reply_animation(file_id, caption=content)
            break
