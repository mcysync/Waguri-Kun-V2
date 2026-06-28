import logging
import os
import shutil
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import owner_only
from modules.database import db

logger = logging.getLogger("WaguriBot.Maintenance")

@Client.on_message(filters.command("vacuum") & filters.private)
@owner_only
async def vacuum_database(client: Client, message: Message):
    msg = await message.reply_text("🌸 Initiating database VACUUM...")
    
    try:
        # Reclaims unused space in SQLite
        await db.execute("VACUUM;")
        
        size = os.path.getsize("data/database.db") / (1024 * 1024)
        await msg.edit_text(f"🌸 **VACUUM Complete!** ✨\n\nOptimized DB. Current Size: `{size:.2f} MB`")
    except Exception as e:
        await msg.edit_text(f"🌸 Failed to vacuum database: `{e}`")

@Client.on_message(filters.command("clearcache") & filters.private)
@owner_only
async def clear_cache(client: Client, message: Message):
    msg = await message.reply_text("🌸 Clearing temp and cache directories...")
    
    dirs_to_clean = ["data/temp", "data/cache"]
    freed_space = 0
    
    try:
        for d in dirs_to_clean:
            if os.path.exists(d):
                for root, _, files in os.walk(d):
                    for file in files:
                        filepath = os.path.join(root, file)
                        freed_space += os.path.getsize(filepath)
                        os.remove(filepath)
                        
        await msg.edit_text(f"🌸 **Cache Cleared!** 🧹\n\nFreed Space: `{freed_space / 1024 / 1024:.2f} MB`")
    except Exception as e:
        await msg.edit_text(f"🌸 Error clearing cache: `{e}`")

@Client.on_message(filters.command("restart") & filters.private)
@owner_only
async def restart_bot(client: Client, message: Message):
    await message.reply_text("🌸 Restarting Waguri System... BRB! ✨")
    
    # Save active state or checkpoint DB
    await db.close()
    
    logger.info("Bot restarting from command...")
    
    import sys
    os.execl(sys.executable, sys.executable, *sys.argv)
