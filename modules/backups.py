import logging
import os
import shutil
import asyncio
from datetime import datetime
from pathlib import Path
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import sudo_only
from config import Config

logger = logging.getLogger("WaguriBot.Backups")

@Client.on_message(filters.command("backup") & filters.private)
@sudo_only
async def create_backup(client: Client, message: Message):
    await message.reply_text("🌸 Preparing enterprise database backup...")
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = "data/backups"
        db_path = Config.DATABASE_PATH
        backup_path = f"{backup_dir}/waguri_db_backup_{timestamp}.sqlite3"
        
        # We need to lock the database during file copy to avoid corruption.
        # Alternatively, use SQLite's native backup API, but standard file copy works for small-medium sets if WAL is checkpointed.
        from modules.database import db
        
        # Checkpoint WAL safely
        await db.execute("PRAGMA wal_checkpoint(TRUNCATE);")
        
        # Copy the file
        shutil.copy2(db_path, backup_path)
        
        # Send to user
        await client.send_document(
            message.chat.id,
            document=backup_path,
            caption=f"🌸 **Backup Complete!**\n\n**Date:** `{timestamp}`\n**File:** `{os.path.basename(backup_path)}`\n**Size:** `{os.path.getsize(backup_path) / 1024 / 1024:.2f} MB`"
        )
        
    except Exception as e:
        logger.error(f"Backup error: {e}")
        await message.reply_text(f"🌸 Failed to create backup: `{e}`")

@Client.on_message(filters.command("restore") & filters.private)
@sudo_only
async def restore_backup(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document:
        return await message.reply_text("🌸 Please reply to a valid `.sqlite3` or `.db` backup file to restore.")
        
    doc = message.reply_to_message.document
    if not doc.file_name.endswith((".db", ".sqlite3")):
        return await message.reply_text("🌸 Invalid file type. Must be `.db` or `.sqlite3`.")
        
    warning_msg = await message.reply_text(
        "🌸 **WARNING!** 🚨\nRestoring a backup will **OVERWRITE** the current database entirely. "
        "The bot will be temporarily locked during the process.\n\n"
        "Send `/confirm_restore` within 30 seconds to proceed."
    )
    
    try:
        # Simple confirmation check (production bots usually use inline buttons, this is a fast CLI approach)
        response = await client.listen(
            chat_id=message.chat.id,
            user_id=message.from_user.id,
            timeout=30,
            filters=filters.command("confirm_restore")
        )
        
        await warning_msg.edit_text("🌸 Downloading backup file...")
        dl_path = f"data/temp/{doc.file_name}"
        await message.reply_to_message.download(file_name=dl_path)
        
        from modules.database import db
        await warning_msg.edit_text("🌸 Closing active connections...")
        await db.close()
        
        await warning_msg.edit_text("🌸 Overwriting database...")
        shutil.copy2(dl_path, Config.DATABASE_PATH)
        os.remove(dl_path)
        
        await warning_msg.edit_text("🌸 Re-establishing connections...")
        await db.connect()
        
        await warning_msg.edit_text("🌸 **Restore Complete!** ✨ All systems are back online.")
        
    except asyncio.TimeoutError:
        await warning_msg.edit_text("🌸 Restore cancelled. (Timeout)")
    except Exception as e:
        logger.error(f"Restore error: {e}")
        await warning_msg.edit_text(f"🌸 Restore failed: `{e}`")
        # Try to reconnect in case of failure
        from modules.database import db
        await db.connect()
