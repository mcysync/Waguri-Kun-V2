import time
import os
import psutil
import logging
from pyrogram import Client, filters
from pyrogram.types import Message

from config import Config
from modules.database import db

logger = logging.getLogger("WaguriBot.Stats")

def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)
    return ping_time

@Client.on_message(filters.command(["stats", "sysinfo"]))
async def system_stats(client: Client, message: Message):
    msg = await message.reply_text("🌸 Fetching enterprise metrics...")
    
    start_time = time.time()
    
    # OS Metrics
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    
    # DB Metrics
    db_size = os.path.getsize(Config.DATABASE_PATH) / (1024 * 1024)
    users_count = (await db.fetchone("SELECT COUNT(*) FROM users"))[0]
    chats_count = (await db.fetchone("SELECT COUNT(*) FROM chats"))[0]
    
    # Uptime
    bot_uptime = get_readable_time(time.time() - client.start_time.timestamp())
    
    ping = (time.time() - start_time) * 1000
    
    stats_text = (
        f"🌸 **Waguri Enterprise Statistics** 🌸\n\n"
        f"**🤖 Bot Uptime:** `{bot_uptime}`\n"
        f"**⚡ Ping:** `{ping:.2f} ms`\n"
        f"**📦 Database Size:** `{db_size:.2f} MB`\n\n"
        f"**👥 Total Users:** `{users_count}`\n"
        f"**🏠 Total Chats:** `{chats_count}`\n\n"
        f"**💻 CPU Usage:** `{cpu}%`\n"
        f"**🧠 RAM Usage:** `{ram.percent}%` ({ram.used / 1024**3:.2f} GB / {ram.total / 1024**3:.2f} GB)\n"
        f"**💽 Disk Usage:** `{disk.percent}%`"
    )
    
    await msg.edit_text(stats_text)

@Client.on_message(filters.command("ping"))
async def ping_cmd(client: Client, message: Message):
    start = time.time()
    msg = await message.reply_text("🌸 Pong!")
    end = time.time()
    
    await msg.edit_text(f"🌸 **Pong!** 🏓\nLatency: `{((end - start) * 1000):.2f}ms`")
