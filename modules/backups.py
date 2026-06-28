import logging
import os
import shutil
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import sudo_only
from config import Config
from modules.database import db

logger = logging.getLogger("WaguriBot.Backups")

@Client.on_message(filters.command("backup") & filters.private)
@sudo_only
async def create_backup(client: Client, message: Message):
    await message.reply_text("🌸 Preparing enterprise database backup...")
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"data/backups/waguri_db_{timestamp}.sqlite3"
        
        await db.execute("PRAGMA wal_checkpoint(TRUNCATE);")
        shutil.copy2(Config.DATABASE_PATH, backup_path)
        
        await client.send_document(
            message.chat.id,
            document=backup_path,
            caption=f"🌸 **Backup Complete!**\n**Date:** `{timestamp}`"
        )
    except Exception as e:
        await message.reply_text(f"🌸 Failed to create backup: `{e}`")
