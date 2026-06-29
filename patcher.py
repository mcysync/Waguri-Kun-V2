import os

print("🌸 WAGURI ULTIMATE PATCHER INITIATED 🌸\n")
os.makedirs("modules", exist_ok=True)

# =========================================================
# 1. FILTERS (Fixed Double-Reply Bug)
# =========================================================
FILTERS_CODE = """import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from utils import admin_required
from modules.database import db

logger = logging.getLogger("WaguriBot.Filters")

async def get_filter(chat_id: int, name: str):
    return await db.fetchone("SELECT content, file_id, type FROM notes WHERE chat_id = ? AND name = ?", chat_id, name)

@Client.on_message(filters.command("filter") & filters.group)
@admin_required("can_change_info")
async def add_filter(client: Client, message: Message):
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply_text("🌸 Usage: `/filter [keyword] [reply text/media]`")
        
    args = message.text.split(None, 2)
    if len(args) < 2: return await message.reply_text("🌸 Please provide a keyword for the filter.")
    
    keyword = args[1].lower()
    if keyword.startswith("#"):
        return await message.reply_text("🌸 Filters cannot start with `#`. Use `/save` to create a Note instead.")
        
    content, file_id, msg_type = None, None, "text"
    
    if message.reply_to_message:
        replied = message.reply_to_message
        if replied.text: content = replied.text.markdown
        elif replied.photo:
            msg_type, file_id = "photo", replied.photo.file_id
            content = replied.caption.markdown if replied.caption else None
        elif replied.document:
            msg_type, file_id = "document", replied.document.file_id
            content = replied.caption.markdown if replied.caption else None
        elif replied.sticker: msg_type, file_id = "sticker", replied.sticker.file_id
        elif replied.animation:
            msg_type, file_id = "animation", replied.animation.file_id
            content = replied.caption.markdown if replied.caption else None
    else:
        if len(args) > 2: content = args[2]
        else: return await message.reply_text("🌸 You need to provide content or reply to a message!")
            
    await db.execute("INSERT OR REPLACE INTO notes (chat_id, name, content, file_id, type) VALUES (?, ?, ?, ?, ?)", message.chat.id, keyword, content, file_id, msg_type)
    await message.reply_text(f"🌸 Filter `{keyword}` saved successfully!")

@Client.on_message(filters.command(["stop", "unfilter"]) & filters.group)
@admin_required("can_change_info")
async def stop_filter(client: Client, message: Message):
    if len(message.command) < 2: return await message.reply_text("🌸 Please provide the keyword of the filter to stop.")
    keyword = message.command[1].lower()
    if not await get_filter(message.chat.id, keyword): return await message.reply_text(f"🌸 Filter `{keyword}` doesn't exist here!")
    await db.execute("DELETE FROM notes WHERE chat_id = ? AND name = ?", message.chat.id, keyword)
    await message.reply_text(f"🌸 Filter `{keyword}` has been deleted.")

@Client.on_message(filters.command("filters") & filters.group)
async def list_filters(client: Client, message: Message):
    records = await db.fetchall("SELECT name FROM notes WHERE chat_id = ? AND name NOT LIKE '#%'", message.chat.id)
    if not records: return await message.reply_text("🌸 There are no active filters in this chat.")
    text = "🌸 **Active Filters:**\\n\\n"
    for r in records: text += f"• `{r[0]}`\\n"
    await message.reply_text(text)

@Client.on_message(filters.text & filters.group & ~filters.bot, group=1)
async def filter_watcher(client: Client, message: Message):
    if not message.text or message.text.startswith("/"): return
    words = set(message.text.lower().split())
    records = await db.fetchall("SELECT name, content, file_id, type FROM notes WHERE chat_id = ? AND name NOT LIKE '#%'", message.chat.id)
    for record in records:
        keyword, content, file_id, msg_type = record
        if keyword in words:
            try:
                if msg_type == "text": await message.reply_text(content, disable_web_page_preview=True)
                elif msg_type == "photo": await message.reply_photo(file_id, caption=content)
                elif msg_type == "document": await message.reply_document(file_id, caption=content)
                elif msg_type == "sticker": await message.reply_sticker(file_id)
                elif msg_type == "animation": await message.reply_animation(file_id, caption=content)
            except Exception: pass
            break
"""

# =========================================================
# 2. AFK SYSTEM (Brand New)
# =========================================================
AFK_CODE = """import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from modules.database import db

logger = logging.getLogger("WaguriBot.AFK")

async def init_afk():
    await db.execute("CREATE TABLE IF NOT EXISTS afk_users (user_id INTEGER PRIMARY KEY, reason TEXT)")

@Client.on_message(filters.command("afk"))
async def set_afk(client: Client, message: Message):
    await init_afk()
    if not message.from_user: return
    reason = " ".join(message.command[1:]) if len(message.command) > 1 else "AFK"
    await db.execute("INSERT OR REPLACE INTO afk_users (user_id, reason) VALUES (?, ?)", message.from_user.id, reason)
    await message.reply_text(f"🌸 **{message.from_user.first_name}** is now AFK.\\n**Reason:** `{reason}`")

@Client.on_message(filters.group & ~filters.bot, group=18)
async def afk_watcher(client: Client, message: Message):
    if not message.from_user: return
    await init_afk()
    
    # Check if they are back
    record = await db.fetchone("SELECT reason FROM afk_users WHERE user_id = ?", message.from_user.id)
    if record:
        await db.execute("DELETE FROM afk_users WHERE user_id = ?", message.from_user.id)
        await message.reply_text(f"🌸 **{message.from_user.first_name}** is back!")

    # Check if they replied to someone who is AFK
    if message.reply_to_message and message.reply_to_message.from_user:
        target_id = message.reply_to_message.from_user.id
        if target_id != message.from_user.id:
            rep_record = await db.fetchone("SELECT reason FROM afk_users WHERE user_id = ?", target_id)
            if rep_record:
                await message.reply_text(f"🌸 **{message.reply_to_message.from_user.first_name}** is currently AFK!\\n**Reason:** `{rep_record[0]}`")
"""

# =========================================================
# 3. START COMMAND (With Custom GIF)
# =========================================================
START_CODE = """import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger("WaguriBot.Start")

START_GIF = "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExMHlkY3huNXRtczFxaGp1enR6NmkzdmM3cjRoMjh0aWtvc3l3bXcwdCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/oDyhKNwTv0Zy9TbKtV/giphy.gif"

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    me = await client.get_me()
    welcome_text = (
        f"🌸 **Hello there, {message.from_user.first_name}!**\\n\\n"
        f"I am **{me.first_name}**, an elegant and powerful enterprise bot.\\n\\n"
        f"🛡 **Moderation & Security**\\n"
        f"💴 **Economy & Leveling**\\n"
        f"🎌 **Anime & Utilities**\\n\\n"
        f"To see everything I can do, just type `/help`!\\n"
        f"Add me to your group using the button below. ✨"
    )
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("🌸 Add Waguri to your Group 🌸", url=f"https://t.me/{me.username}?startgroup=true")]])
    await message.reply_animation(animation=START_GIF, caption=welcome_text, reply_markup=buttons)

@Client.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    help_text = (
        "🌸 **Waguri Command Menu** 🌸\\n\\n"
        "**🛡 Moderation:**\\n`/ban`, `/mute`, `/kick`, `/warn`, `/purge`, `/lock`, `/unlock`\\n\\n"
        "**🚨 Security:**\\n`/raidmode`, `/antispam`, `/security`, `/captcha`\\n\\n"
        "**💰 Economy:**\\n`/daily`, `/balance`, `/pay`, `/rank`, `/rep`\\n\\n"
        "**⚙️ Admin:**\\n`/settings`, `/setwelcome`, `/filter`, `/notes`, `/stats`\\n\\n"
        "*(And over 200 more features running silently in the background!)*"
    )
    await message.reply_text(help_text)
"""

# =========================================================
# 4. FUN COMMANDS (With Waifu, Slaps, and Job GIFs)
# =========================================================
FUN_CODE = """import logging
import httpx
import random
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config

logger = logging.getLogger("WaguriBot.Fun")

WAIFU_GIF = "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExc21uY3piOTVrZGF2azlzMGRlcHFyeW51NHdsbTVnN2R4eG5uZ2NvOCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Gm5QmoMQjbf68sGEeD/giphy.gif"
JOB_GIF = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNTlvZnkwaGluNTRnOWZ3a2o0NWZ0dXlsbGdsYXNyajM0MWllZzVrMSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/Pswv7i25VZG6TxcKuv/giphy.gif"
SLAP_GIFS = [
    "https://media.giphy.com/media/Gf3AUz3eA4pQC/giphy.gif",
    "https://media.giphy.com/media/Zau0yrl17uzdK/giphy.gif",
    "https://media.giphy.com/media/uG3lKkAuh53xe/giphy.gif",
    "https://media.giphy.com/media/RXGNsyRb1hDJm/giphy.gif",
    "https://media.giphy.com/media/10hzvF9FTulBte/giphy.gif"
]

@Client.on_message(filters.command("anime") & filters.group)
async def search_anime(client: Client, message: Message):
    if not Config.ENABLE_ANIME: return
    if len(message.command) < 2: return await message.reply_text("🌸 Please provide an anime name. Example: `/anime Naruto`")
    query = message.text.split(None, 1)[1]
    try:
        async with httpx.AsyncClient() as http_client:
            res = await http_client.get(f"https://api.jikan.moe/v4/anime?q={query}&limit=1")
            data = res.json()
            if not data.get("data"): return await message.reply_text("🌸 I couldn't find any anime with that name!")
            anime = data["data"][0]
            caption = f"🌸 **{anime.get('title')}**\\n\\n**Episodes:** `{anime.get('episodes', 'Unknown')}`\\n**Status:** `{anime.get('status', 'Unknown')}`\\n**Score:** ⭐ `{anime.get('score', 'N/A')}`\\n\\n**Synopsis:** {anime.get('synopsis', 'N/A')[:300]}...\\n\\n🔗 [More Info]({anime.get('url')})"
            await message.reply_photo(photo=str(anime["images"]["jpg"]["large_image_url"]), caption=caption)
    except Exception:
        await message.reply_text("🌸 Oops! The MyAnimeList API seems to be sleeping.")

@Client.on_message(filters.command("waifu") & filters.group)
async def get_waifu(client: Client, message: Message):
    if not Config.ENABLE_ANIME: return
    await message.reply_animation(animation=WAIFU_GIF, caption="🌸 Here is a cute waifu for you! ✨")

@Client.on_message(filters.command("quote") & filters.group)
async def anime_quote(client: Client, message: Message):
    if not Config.ENABLE_ANIME: return
    try:
        async with httpx.AsyncClient() as http_client:
            res = await http_client.get("https://animechan.xyz/api/random")
            data = res.json()
            await message.reply_text(f"🌸 *\\"{data.get('quote')}\\"*\\n\\n— **{data.get('character')}** ({data.get('anime')})")
    except Exception:
        await message.reply_text("🌸 Could not retrieve a quote at this time.")

@Client.on_message(filters.command("slap") & filters.group)
async def action_slap(client: Client, message: Message):
    if not message.reply_to_message: return await message.reply_text("🌸 Reply to a user to slap them!")
    sender = message.from_user.mention if message.from_user else "Someone"
    target = message.reply_to_message.from_user.mention if message.reply_to_message.from_user else "Someone"
    chosen_gif = random.choice(SLAP_GIFS)
    await message.reply_animation(animation=chosen_gif, caption=f"💥 **{sender}** violently slapped **{target}**!")

@Client.on_message(filters.command("job") & filters.group)
async def action_job(client: Client, message: Message):
    if not message.reply_to_message: return await message.reply_text("🌸 Reply to a user to give them a job!")
    sender = message.from_user.mention if message.from_user else "Someone"
    target = message.reply_to_message.from_user.mention if message.reply_to_message.from_user else "Someone"
    await message.reply_animation(animation=JOB_GIF, caption=f"💼 **{sender}** just assigned a job to **{target}**! Get to work!")
"""

# =========================================================
# WRITE THE FILES
# =========================================================
files_to_write = {
    "modules/filters.py": FILTERS_CODE,
    "modules/afk.py": AFK_CODE,
    "modules/start.py": START_CODE,
    "modules/fun.py": FUN_CODE
}

for filepath, content in files_to_write.items():
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Successfully wrote {filepath}")

print("\n🚀 ALL MODULES PATCHED AND READY. Run: python bot.py")
