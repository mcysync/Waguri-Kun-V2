import logging
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import admin_required
from modules.database import db

logger = logging.getLogger("WaguriBot.Notes")

@Client.on_message(filters.command(["save", "note"]) & filters.group)
@admin_required("can_change_info")
async def save_note(client: Client, message: Message):
    args = message.text.split(None, 2)
    
    if len(args) < 2:
        return await message.reply_text("🌸 Usage: `/save [notename] [content/reply]`")
        
    note_name = f"#{args[1].lower()}"
    
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
    else:
        if len(args) > 2:
            content = args[2]
        else:
            return await message.reply_text("🌸 Provide note content or reply to a message!")
            
    await db.execute(
        "INSERT OR REPLACE INTO notes (chat_id, name, content, file_id, type) VALUES (?, ?, ?, ?, ?)",
        message.chat.id, note_name, content, file_id, msg_type
    )
    
    await message.reply_text(f"🌸 Note saved! Access it using `/get {note_name[1:]}` or just typing `{note_name}`")

@Client.on_message(filters.command(["get"]) & filters.group)
async def get_note_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("🌸 Specify a note name!")
        
    note_name = f"#{message.command[1].lower()}"
    await trigger_note(client, message, note_name)

@Client.on_message(filters.command(["clear"]) & filters.group)
@admin_required("can_change_info")
async def clear_note(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("🌸 Specify a note to delete.")
        
    note_name = f"#{message.command[1].lower()}"
    
    record = await db.fetchone("SELECT name FROM notes WHERE chat_id = ? AND name = ?", message.chat.id, note_name)
    if not record:
        return await message.reply_text("🌸 Note not found!")
        
    await db.execute("DELETE FROM notes WHERE chat_id = ? AND name = ?", message.chat.id, note_name)
    await message.reply_text(f"🌸 Note `{note_name}` cleared!")

@Client.on_message(filters.command(["notes", "saved"]) & filters.group)
async def list_notes(client: Client, message: Message):
    records = await db.fetchall("SELECT name FROM notes WHERE chat_id = ? AND name LIKE '#%'", message.chat.id)
    
    if not records:
        return await message.reply_text("🌸 No saved notes here.")
        
    text = "🌸 **Saved Notes:**\n\n"
    for r in records:
        # Strip the '#' for clean display
        text += f"• `{r[0][1:]}`\n"
        
    await message.reply_text(text)

# Listen to hashtags to trigger notes
@Client.on_message(filters.regex(r"^#\w+") & filters.group)
async def note_watcher(client: Client, message: Message):
    note_name = message.text.split()[0].lower()
    await trigger_note(client, message, note_name)
    
async def trigger_note(client, message, note_name):
    record = await db.fetchone("SELECT content, file_id, type FROM notes WHERE chat_id = ? AND name = ?", message.chat.id, note_name)
    
    if not record:
        return
        
    content, file_id, msg_type = record
    
    if msg_type == "text":
        await message.reply_text(content, disable_web_page_preview=True)
    elif msg_type == "photo":
        await message.reply_photo(file_id, caption=content)
    elif msg_type == "document":
        await message.reply_document(file_id, caption=content)
    elif msg_type == "sticker":
        await message.reply_sticker(file_id)
