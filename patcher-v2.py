import os

print("🌸 WAGURI ULTIMATE MEGA-PATCHER INITIATED 🌸\n")
os.makedirs("modules", exist_ok=True)

# =========================================================
# 1. AFK MODULE (Fixed)
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
    if message.text and message.text.startswith("/afk"): return
    
    await init_afk()
    record = await db.fetchone("SELECT reason FROM afk_users WHERE user_id = ?", message.from_user.id)
    if record:
        await db.execute("DELETE FROM afk_users WHERE user_id = ?", message.from_user.id)
        await message.reply_text(f"🌸 **{message.from_user.first_name}** is back!")

    if message.reply_to_message and message.reply_to_message.from_user:
        target_id = message.reply_to_message.from_user.id
        if target_id != message.from_user.id:
            rep_record = await db.fetchone("SELECT reason FROM afk_users WHERE user_id = ?", target_id)
            if rep_record:
                await message.reply_text(f"🌸 **{message.reply_to_message.from_user.first_name}** is currently AFK!\\n**Reason:** `{rep_record[0]}`")
"""

# =========================================================
# 2. START / HELP MODULE (Beautiful Redesign)
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
        f"🛡 **Moderation & Federations**\\n"
        f"💴 **Economy & Mystery Boxes**\\n"
        f"🎌 **Anime & Utilities**\\n\\n"
        f"To see everything I can do, just type `/help`!\\n"
        f"Add me to your group using the button below. ✨"
    )
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("🌸 Add Waguri to your Group 🌸", url=f"https://t.me/{me.username}?startgroup=true")]])
    await message.reply_animation(animation=START_GIF, caption=welcome_text, reply_markup=buttons)

@Client.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    help_text = (
        "🌸 **Waguri Enterprise Command Center** 🌸\\n\\n"
        "🛡 **Moderation**\\n"
        "`/ban`, `/tban`, `/mute`, `/tmute`, `/kick`, `/warn`, `/purge`, `/lock`, `/unlock`\\n\\n"
        "🌐 **Federations (Rose-Style)**\\n"
        "`/newfed`, `/joinfed`, `/leavefed`, `/fban`, `/unfban`, `/fedinfo`\\n\\n"
        "🚨 **Security & Anti-Raid**\\n"
        "`/raidmode`, `/antispam`, `/security`, `/captcha`, `/automod`\\n\\n"
        "💰 **Economy & Treasure**\\n"
        "`/daily`, `/bal`, `/pay`, `/rep`, `/treasure`\\n\\n"
        "🎌 **Anime, AI & Fun**\\n"
        "`/ask`, `/anime`, `/waifu`, `/slap`, `/job`, `/quote`, `/weather`\\n\\n"
        "⚙️ **Admin & Group**\\n"
        "`/settings`, `/filter`, `/save`, `/setwelcome`, `/afk`\\n\\n"
        "💻 **Sudo Only:** Use `/developer-options`"
    )
    await message.reply_text(help_text)
"""

# =========================================================
# 3. DEV OPTIONS MODULE (Sudo Only)
# =========================================================
DEV_CODE = """import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from utils import sudo_only
from config import Config

@Client.on_message(filters.command("developer-options"))
@sudo_only
async def dev_options(client: Client, message: Message):
    dev_text = (
        "💻 **Waguri Developer & Sudo Control Panel** 💻\\n\\n"
        "These commands are restricted to users listed in `.env`.\\n\\n"
        "🌍 **Global Actions**\\n"
        "`/gban [user]` - Globally ban across all bot chats.\\n"
        "`/ungban [user]` - Remove global ban.\\n"
        "`/broadcast [reply]` - Send a message to all chats.\\n\\n"
        "🗄 **System & Database**\\n"
        "`/backup` - Download SQLite database.\\n"
        "`/restore` - Overwrite database with a `.db` file.\\n"
        "`/vacuum` - Optimize database size.\\n"
        "`/clearcache` - Clear temp files.\\n\\n"
        "⚡ **Terminal**\\n"
        "`/eval [code]` - Execute raw Python code.\\n"
        "`/restart` - Reboot the Waguri script."
    )
    await message.reply_text(dev_text)
"""

# =========================================================
# 4. FEDERATIONS MODULE (Rose Style)
# =========================================================
FEDS_CODE = """import logging
import uuid
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from utils import admin_required, extract_target
from modules.database import db

logger = logging.getLogger("WaguriBot.Feds")

async def init_feds():
    await db.execute("CREATE TABLE IF NOT EXISTS feds (fed_id TEXT PRIMARY KEY, name TEXT, creator_id INTEGER)")
    await db.execute("CREATE TABLE IF NOT EXISTS fed_chats (chat_id INTEGER PRIMARY KEY, fed_id TEXT)")
    await db.execute("CREATE TABLE IF NOT EXISTS fed_bans (fed_id TEXT, user_id INTEGER, reason TEXT, PRIMARY KEY(fed_id, user_id))")

@Client.on_message(filters.command("newfed") & filters.private)
async def new_fed(client: Client, message: Message):
    await init_feds()
    if len(message.command) < 2: return await message.reply_text("🌸 Usage: `/newfed [Federation Name]`")
    
    fed_name = message.text.split(None, 1)[1]
    fed_id = str(uuid.uuid4())
    
    await db.execute("INSERT INTO feds (fed_id, name, creator_id) VALUES (?, ?, ?)", fed_id, fed_name, message.from_user.id)
    await message.reply_text(f"🌸 **Federation Created!**\\n\\n**Name:** `{fed_name}`\\n**Fed ID:** `{fed_id}`\\n\\nGroup admins can now join your fed using:\\n`/joinfed {fed_id}`")

@Client.on_message(filters.command("joinfed") & filters.group)
@admin_required("can_restrict_members")
async def join_fed(client: Client, message: Message):
    await init_feds()
    if len(message.command) < 2: return await message.reply_text("🌸 Usage: `/joinfed [Fed ID]`")
    
    fed_id = message.command[1]
    record = await db.fetchone("SELECT name FROM feds WHERE fed_id = ?", fed_id)
    if not record: return await message.reply_text("🌸 Invalid Federation ID.")
    
    await db.execute("INSERT OR REPLACE INTO fed_chats (chat_id, fed_id) VALUES (?, ?)", message.chat.id, fed_id)
    await message.reply_text(f"🌸 Successfully joined the Federation: **{record[0]}**!\\nFbans from this fed will now be enforced here.")

@Client.on_message(filters.command("leavefed") & filters.group)
@admin_required("can_restrict_members")
async def leave_fed(client: Client, message: Message):
    await init_feds()
    await db.execute("DELETE FROM fed_chats WHERE chat_id = ?", message.chat.id)
    await message.reply_text("🌸 This chat has left the Federation. Fbans will no longer be enforced.")

@Client.on_message(filters.command("fban"))
async def fban_user(client: Client, message: Message):
    await init_feds()
    target_id, target_mention, reason = await extract_target(client, message)
    if not target_id: return await message.reply_text("🌸 Please specify a user to Fban.")
    
    # Verify sender owns a fed
    fed_record = await db.fetchone("SELECT fed_id, name FROM feds WHERE creator_id = ?", message.from_user.id)
    if not fed_record: return await message.reply_text("🌸 You must be the creator of a Federation to use `/fban`.")
    
    fed_id, fed_name = fed_record
    reason_text = reason or "No reason provided."
    
    await db.execute("INSERT OR REPLACE INTO fed_bans (fed_id, user_id, reason) VALUES (?, ?, ?)", fed_id, target_id, reason_text)
    
    # Apply ban to all chats in this fed
    chats = await db.fetchall("SELECT chat_id FROM fed_chats WHERE fed_id = ?", fed_id)
    banned_count = 0
    for (chat_id,) in chats:
        try:
            await client.ban_chat_member(chat_id, target_id)
            banned_count += 1
        except Exception: pass
            
    await message.reply_text(f"🌸 **New Federation Ban!** 🌐\\n\\n**Fed:** {fed_name}\\n**Target:** {target_mention}\\n**Reason:** `{reason_text}`\\n\\nBanned in `{banned_count}` subbed chats.")

@Client.on_message(filters.command("unfban"))
async def unfban_user(client: Client, message: Message):
    await init_feds()
    target_id, target_mention, _ = await extract_target(client, message)
    if not target_id: return await message.reply_text("🌸 Please specify a user to Un-Fban.")
    
    fed_record = await db.fetchone("SELECT fed_id FROM feds WHERE creator_id = ?", message.from_user.id)
    if not fed_record: return await message.reply_text("🌸 You do not own a Federation.")
    
    fed_id = fed_record[0]
    await db.execute("DELETE FROM fed_bans WHERE fed_id = ? AND user_id = ?", fed_id, target_id)
    
    chats = await db.fetchall("SELECT chat_id FROM fed_chats WHERE fed_id = ?", fed_id)
    for (chat_id,) in chats:
        try: await client.unban_chat_member(chat_id, target_id)
        except Exception: pass
            
    await message.reply_text(f"🌸 **Un-Fbanned** {target_mention} from the Federation.")

@Client.on_message(filters.new_chat_members, group=21)
async def fed_enforcer(client: Client, message: Message):
    chat_id = message.chat.id
    fed_record = await db.fetchone("SELECT fed_id FROM fed_chats WHERE chat_id = ?", chat_id)
    if not fed_record: return
    
    fed_id = fed_record[0]
    for user in message.new_chat_members:
        ban_record = await db.fetchone("SELECT reason FROM fed_bans WHERE fed_id = ? AND user_id = ?", fed_id, user.id)
        if ban_record:
            try:
                await client.ban_chat_member(chat_id, user.id)
                await message.reply_text(f"🌸 **Federation Shield Triggered!** 🌐\\n{user.mention} was removed because they are F-Banned in this chat's linked Federation.\\n**Reason:** `{ban_record[0]}`")
            except Exception: pass
"""

# =========================================================
# 5. CAPTCHA MODULE (Interactive & Beautiful)
# =========================================================
CAPTCHA_CODE = """import logging
import random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions, CallbackQuery
from utils import admin_required
from modules.database import db

logger = logging.getLogger("WaguriBot.Captcha")

async def init_captcha():
    await db.execute("CREATE TABLE IF NOT EXISTS captcha_settings (chat_id INTEGER PRIMARY KEY, is_enabled BOOLEAN DEFAULT 0)")

@Client.on_message(filters.command("captcha") & filters.group)
@admin_required("can_restrict_members")
async def toggle_captcha(client: Client, message: Message):
    await init_captcha()
    args = message.command
    if len(args) < 2: return await message.reply_text("🌸 Usage: `/captcha on` or `/captcha off`")
    state = args[1].lower() == "on"
    await db.execute("INSERT OR REPLACE INTO captcha_settings (chat_id, is_enabled) VALUES (?, ?)", message.chat.id, state)
    await message.reply_text(f"🌸 Welcome Captcha is now {'activated ✅' if state else 'deactivated ❌'}.")

@Client.on_message(filters.new_chat_members, group=5)
async def captcha_new_member(client: Client, message: Message):
    await init_captcha()
    chat_id = message.chat.id
    settings = await db.fetchone("SELECT is_enabled FROM captcha_settings WHERE chat_id = ?", chat_id)
    if not settings or not settings[0]: return
    
    for user in message.new_chat_members:
        if user.is_bot: continue
        try:
            await client.restrict_chat_member(chat_id, user.id, ChatPermissions(can_send_messages=False))
            
            buttons = [
                InlineKeyboardButton("🌸 I am Human", callback_data=f"captcayes_{user.id}"),
                InlineKeyboardButton("🤖 I am Bot", callback_data=f"captchano_{user.id}"),
                InlineKeyboardButton("👽 Alien", callback_data=f"captchano_{user.id}")
            ]
            random.shuffle(buttons)
            markup = InlineKeyboardMarkup([[buttons[0]], [buttons[1], buttons[2]]])
            
            await message.reply_text(
                f"🌸 Hello {user.mention}! Welcome.\\n\\n🛡 **Anti-Bot Security Check**\\nPlease prove you are human by clicking the correct button below. You are muted until you pass.",
                reply_markup=markup
            )
        except Exception as e: pass

@Client.on_callback_query(filters.regex(r"^captca(yes|no)_(\d+)$"))
async def captcha_callback(client: Client, callback_query: CallbackQuery):
    action = callback_query.matches[0].group(1)
    target_id = int(callback_query.matches[0].group(2))
    
    if callback_query.from_user.id != target_id:
        return await callback_query.answer("🌸 This is not your captcha!", show_alert=True)
        
    chat_id = callback_query.message.chat.id
    
    if action == "yes":
        try:
            chat = await client.get_chat(chat_id)
            await client.restrict_chat_member(chat_id, target_id, chat.permissions)
            await callback_query.answer("🌸 Verified! You can now chat.", show_alert=True)
            await callback_query.message.delete()
        except Exception:
            await callback_query.answer("Failed to unmute. Ask an admin.", show_alert=True)
    else:
        try:
            await client.ban_chat_member(chat_id, target_id)
            await callback_query.message.edit_text(f"🌸 Verification failed. User banned.")
        except Exception: pass
"""

# =========================================================
# 6. MYSTERY BOX / TREASURE MODULE (Hourly Drops)
# =========================================================
TREASURE_CODE = """import logging
import random
import time
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from utils import admin_required
from modules.database import db

logger = logging.getLogger("WaguriBot.Treasure")

# Memory tracker: {chat_id: last_drop_timestamp}
drop_cooldowns = {}

async def init_treasure():
    await db.execute("CREATE TABLE IF NOT EXISTS treasure_settings (chat_id INTEGER PRIMARY KEY, is_enabled BOOLEAN DEFAULT 0)")
    await db.execute("CREATE TABLE IF NOT EXISTS economy (user_id INTEGER PRIMARY KEY, wallet INTEGER DEFAULT 0, bank INTEGER DEFAULT 0, last_daily TIMESTAMP)")

@Client.on_message(filters.command("treasure") & filters.group)
@admin_required("can_change_info")
async def toggle_treasure(client: Client, message: Message):
    await init_treasure()
    args = message.command
    if len(args) < 2: return await message.reply_text("🌸 Usage: `/treasure on` or `/treasure off`")
    state = args[1].lower() == "on"
    await db.execute("INSERT OR REPLACE INTO treasure_settings (chat_id, is_enabled) VALUES (?, ?)", message.chat.id, state)
    await message.reply_text(f"🌸 Mystery Box drops are now {'enabled ✅' if state else 'disabled ❌'}!")

@Client.on_message(filters.group & ~filters.bot, group=19)
async def treasure_watcher(client: Client, message: Message):
    chat_id = message.chat.id
    await init_treasure()
    
    settings = await db.fetchone("SELECT is_enabled FROM treasure_settings WHERE chat_id = ?", chat_id)
    if not settings or not settings[0]: return
    
    now = time.time()
    last_drop = drop_cooldowns.get(chat_id, 0)
    
    # DROP EVERY 60 MINUTES (3600 seconds) IF CHAT IS ACTIVE
    if now - last_drop > 3600:
        drop_cooldowns[chat_id] = now
        
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🎁 Claim Treasure", callback_data="claim_treasure")]])
        await message.reply_text(
            "🎁 **A Mystery Box has appeared!**\\n\\nThe first person to click the button claims the loot!",
            reply_markup=markup
        )

@Client.on_callback_query(filters.regex("^claim_treasure$"))
async def claim_treasure(client: Client, callback_query: CallbackQuery):
    user = callback_query.from_user
    
    # 30% chance it's empty, 70% chance for 10-100 coins
    if random.random() < 0.3:
        await callback_query.message.edit_text(f"💨 **Aww...** {user.mention} opened the Mystery Box, but it was completely empty!")
    else:
        reward = random.randint(10, 100)
        await db.execute("INSERT OR IGNORE INTO economy (user_id) VALUES (?)", user.id)
        await db.execute("UPDATE economy SET wallet = wallet + ? WHERE user_id = ?", reward, user.id)
        await callback_query.message.edit_text(f"🎉 **Treasure Claimed!**\\n\\n{user.mention} opened the Mystery Box and found 🪙 **{reward} Coins**!")
"""

# =========================================================
# WRITE THE FILES
# =========================================================
files_to_write = {
    "modules/afk.py": AFK_CODE,
    "modules/start.py": START_CODE,
    "modules/dev.py": DEV_CODE,
    "modules/feds.py": FEDS_CODE,
    "modules/captcha.py": CAPTCHA_CODE,
    "modules/treasure.py": TREASURE_CODE
}

for filepath, content in files_to_write.items():
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Successfully wrote {filepath}")

print("\n🚀 THE ULTIMATE UPGRADE IS COMPLETE. Run: python bot.py")
