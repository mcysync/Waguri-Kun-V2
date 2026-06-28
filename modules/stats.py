import time
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config
from modules.database import db

@Client.on_message(filters.command(["stats", "sysinfo"]))
async def system_stats(client: Client, message: Message):
    db_size = os.path.getsize(Config.DATABASE_PATH) / (1024 * 1024)
    users_count = (await db.fetchone("SELECT COUNT(*) FROM users"))[0]
    chats_count = (await db.fetchone("SELECT COUNT(*) FROM chats"))[0]
    
    stats_text = (
        f"🌸 **Waguri Enterprise Statistics** 🌸\n\n"
        f"**📦 Database Size:** `{db_size:.2f} MB`\n"
        f"**👥 Total Users:** `{users_count}`\n"
        f"**🏠 Total Chats:** `{chats_count}`\n\n"
        f"*(Hardware stats disabled in Mobile Mode)*"
    )
    await message.reply_text(stats_text)

@Client.on_message(filters.command("ping"))
async def ping_cmd(client: Client, message: Message):
    start = time.time()
    msg = await message.reply_text("🌸 Pong!")
    end = time.time()
    await msg.edit_text(f"🌸 **Pong!** 🏓\nLatency: `{((end - start) * 1000):.2f}ms`")
