import os

print("🌸 WAGURI ULTIMATE MEGA-PATCHER V5 INITIATED 🌸\n")
os.makedirs("modules", exist_ok=True)

# =========================================================
# 1. START / HELP MODULE (With Full Descriptions)
# =========================================================
START_CODE = """import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

logger = logging.getLogger("WaguriBot.Start")
START_GIF = "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExMHlkY3huNXRtczFxaGp1enR6NmkzdmM3cjRoMjh0aWtvc3l3bXcwdCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/oDyhKNwTv0Zy9TbKtV/giphy.gif"

HELP_TEXT = (
    "🌸 **Welcome to the Waguri Command Center!** 🌸\\n\\n"
    "Choose a module below to see all available commands and their descriptions."
)

# Detailed descriptions for every single command
HELP_PAGES = {
    "mod": (
        "🛡 **Moderation Commands**\\n\\n"
        "**Bans & Kicks**\\n"
        "• `/ban` - Permanently ban a user from the chat.\\n"
        "• `/tban [time]` - Temporarily ban a user.\\n"
        "• `/sban` / `/shadowban` - Ban a user and delete their message silently.\\n"
        "• `/unban` - Remove a user's ban.\\n"
        "• `/kick` - Kick a user out (they can rejoin).\\n\\n"
        "**Mutes & Restrictions**\\n"
        "• `/mute` - Mute a user from sending messages.\\n"
        "• `/tmute [time]` - Temporarily mute a user.\\n"
        "• `/smute` - Silently mute a user.\\n"
        "• `/unmute` - Restore a user's ability to chat.\\n"
        "• `/mutemedia` / `/mutevoice` - Restrict specific message types.\\n\\n"
        "**Warns & Purges**\\n"
        "• `/warn` - Add a warning to a user.\\n"
        "• `/swarn` - Warn a user silently.\\n"
        "• `/warnings` - Check a user's warning status.\\n"
        "• `/clearwarns` / `/rmwarns` - Reset a user's warnings.\\n"
        "• `/purge` - Delete all messages replied to.\\n\\n"
        "**Chat Locks**\\n"
        "• `/lock [type]` - Lock media, stickers, or links.\\n"
        "• `/unlock [type]` - Unlock restricted items.\\n"
        "• `/locks` - View current chat locks."
    ),
    "admin": (
        "⚙️ **Admin & Setup Commands**\\n\\n"
        "**General Setup**\\n"
        "• `/settings` - Open interactive chat settings.\\n"
        "• `/setlang` / `/set-language` - Set bot language.\\n"
        "• `/setwelcome` / `/welcome` - Set the welcome message.\\n"
        "• `/setgoodbye` / `/goodbye` - Set the leave message.\\n"
        "• `/setlog` / `/unsetlog` - Manage moderation logs.\\n"
        "• `/afk` - Set yourself as AFK.\\n"
        "• `/leavechat` - Make the bot leave.\\n\\n"
        "**Chat Actions**\\n"
        "• `/pin` / `/unpin` / `/unpinall` - Manage pinned messages.\\n"
        "• `/promote` / `/demote` - Manage admin rights.\\n"
        "• `/tagall` / `/all` - Mention everyone in the group.\\n"
        "• `/stopall` / `/cancelall` - Stop the tagall process.\\n"
        "• `/report` / `/reports` - Notify admins of bad behavior.\\n\\n"
        "**Filters & Notes**\\n"
        "• `/filter` / `/stop` / `/filters` - Manage automated text replies.\\n"
        "• `/save` / `/get` / `/clear` / `/notes` - Manage saved notes.\\n\\n"
        "**Lists & Verification**\\n"
        "• `/blacklist` / `/unblacklist` - Block specific words.\\n"
        "• `/whitelist` / `/unwhitelist` - Exempt users from rules.\\n"
        "• `/verify` / `/approve` - Approve users to chat."
    ),
    "sec": (
        "🚨 **Security & Anti-Raid**\\n\\n"
        "**Spam & Flooding**\\n"
        "• `/antispam` - Toggle advanced anti-spam checks.\\n"
        "• `/setflood` / `/floodmode` - Limit message frequency.\\n\\n"
        "**Raid Protection**\\n"
        "• `/raidmode` - Instantly mute/kick all new members.\\n"
        "• `/lockdown` - Completely lock the group down.\\n"
        "• `/captcha` - Force new members to pass a button test.\\n\\n"
        "**System**\\n"
        "• `/automod` - Setup auto-punishments for bad words.\\n"
        "• `/security` - View your group's current security setup."
    ),
    "eco": (
        "💴 **Economy & Premium**\\n\\n"
        "**Wallet & Trading**\\n"
        "• `/daily` - Claim your daily login coins.\\n"
        "• `/balance` / `/bal` / `/wallet` - Check your total wealth.\\n"
        "• `/pay` - Send money to another user.\\n\\n"
        "**Progression**\\n"
        "• `/rank` / `/level` - See your current chat activity level.\\n"
        "• `/rep` - Give +1 reputation to a helpful user.\\n\\n"
        "**Events**\\n"
        "• `/treasure` - Enable random mystery coin box drops.\\n\\n"
        "**Premium System**\\n"
        "• `/mypremium` - Check your premium status.\\n"
        "• `/addpremium` / `/rmpremium` - (Admin) Manage premium."
    ),
    "anime": (
        "🎌 **Anime, AI & Fun**\\n\\n"
        "**AI Utilities**\\n"
        "• `/ask` / `/waguri` - Chat with Waguri's AI.\\n"
        "• `/summarize` - Summarize the last few messages.\\n"
        "• `/grammar` / `/correct` - Fix text grammar automatically.\\n\\n"
        "**Anime & Roleplay**\\n"
        "• `/anime` - Search for an anime synopsis.\\n"
        "• `/waifu` - Get a random 2D waifu image.\\n"
        "• `/quote` - Get a random anime quote.\\n"
        "• `/slap` - Virtually slap a user.\\n\\n"
        "**Events & Tools**\\n"
        "• `/weather` - Check global weather.\\n"
        "• `/poll` - Create a custom poll.\\n"
        "• `/giveaway` / `/endgiveaway` - Host group giveaways.\\n"
        "• `/remind` / `/schedule` - Set a timed reminder.\\n"
        "• `/top` / `/mystats` - View the most active users."
    ),
    "sys": (
        "🛠 **System, Tools & Feds**\\n\\n"
        "**General Information**\\n"
        "• `/start` / `/help` - Bot instructions.\\n"
        "• `/version` - Check bot version.\\n"
        "• `/ping` / `/stats` / `/sysinfo` - Check bot performance.\\n"
        "• `/info` / `/userinfo` - Get user ID and details.\\n\\n"
        "**Federations**\\n"
        "• `/newfed` - Create a global ban network.\\n"
        "• `/joinfed` - Link your chat to a network.\\n\\n"
        "**Developer Tools**\\n"
        "• `/base64` / `/hash` / `/uuid` / `/json` - Encoding tools.\\n\\n"
        "**Sudo / Owner Only**\\n"
        "• `/developer-options` - Show dev menu.\\n"
        "• `/gban` / `/ungban` - Globally ban a user everywhere.\\n"
        "• `/broadcast` - Message all chats.\\n"
        "• `/backup` / `/restore` - Download/upload database.\\n"
        "• `/vacuum` / `/clearcache` / `/restart` - Optimize system.\\n"
        "• `/exec` / `/eval` - Run raw code."
    )
}

def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛡 Moderation", callback_data="help_mod"), InlineKeyboardButton("⚙️ Admin & Setup", callback_data="help_admin")],
        [InlineKeyboardButton("🚨 Security", callback_data="help_sec"), InlineKeyboardButton("💴 Economy", callback_data="help_eco")],
        [InlineKeyboardButton("🎌 Anime & Fun", callback_data="help_anime"), InlineKeyboardButton("🛠 System & Feds", callback_data="help_sys")],
        [InlineKeyboardButton("🌐 Language Settings", callback_data="help_lang")]
    ])

def get_back_button():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="help_main")]])

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    me = await client.get_me()
    welcome_text = (
        f"🌸 **Hello there, {message.from_user.first_name if message.from_user else 'User'}!**\\n\\n"
        f"I am **{me.first_name}**, an elegant and powerful enterprise bot.\\n\\n"
        f"To see everything I can do, just type `/help`!\\n"
        f"Add me to your group using the button below. ✨"
    )
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("🌸 Add Waguri to your Group 🌸", url=f"https://t.me/{me.username}?startgroup=true")]])
    await message.reply_animation(animation=START_GIF, caption=welcome_text, reply_markup=buttons)

@Client.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    await message.reply_text(HELP_TEXT, reply_markup=get_main_menu())

@Client.on_callback_query(filters.regex(r"^help_(.*)$"))
async def help_callback(client: Client, query: CallbackQuery):
    cat = query.matches[0].group(1)
    
    if cat == "main":
        return await query.message.edit_text(HELP_TEXT, reply_markup=get_main_menu())
        
    if cat == "lang":
        text = "🌸 **Language Settings**\\n\\nUse `/setlang` or `/set-language` to change the bot's language for your specific chat.\\n\\nCurrently supported: English, Español, 日本語, Русский, Português, and Bahasa Indonesia!"
        return await query.message.edit_text(text, reply_markup=get_back_button())
        
    if cat in HELP_PAGES:
        await query.message.edit_text(HELP_PAGES[cat], reply_markup=get_back_button())
"""

# =========================================================
# 2. VERSION MODULE
# =========================================================
VERSION_CODE = """import logging
from pyrogram import Client, filters
from pyrogram.types import Message

logger = logging.getLogger("WaguriBot.Version")

@Client.on_message(filters.command("version"))
async def version_command(client: Client, message: Message):
    version_text = (
        "🌸 **Waguri Enterprise System** 🌸\\n\\n"
        "**Current Version:** `v2.0 {BETA}`\\n"
        "**System Status:** Online & Fully Operational ✨\\n"
        "**Core:** Pyrogram & SQLite"
    )
    await message.reply_text(version_text)
"""

# =========================================================
# 3. LANGUAGE MODULE
# =========================================================
LANG_CODE = """import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ChatMemberStatus
from modules.database import db

logger = logging.getLogger("WaguriBot.Language")

LANGUAGES = {
    "en": {"name": "🇬🇧 English", "set": "🌸 Language has been set to **English**!"},
    "es": {"name": "🇪🇸 Español", "set": "🌸 ¡El idioma se ha configurado en **Español**!"},
    "ja": {"name": "🇯🇵 日本語", "set": "🌸 言語が**日本語**に設定されました！"},
    "ru": {"name": "🇷🇺 Русский", "set": "🌸 Язык был установлен на **Русский**!"},
    "pt": {"name": "🇧🇷 Português", "set": "🌸 O idioma foi definido para **Português**!"},
    "id": {"name": "🇮🇩 Bahasa Indonesia", "set": "🌸 Bahasa telah diatur ke **Bahasa Indonesia**!"}
}

async def init_lang():
    await db.execute("CREATE TABLE IF NOT EXISTS chat_langs (chat_id INTEGER PRIMARY KEY, lang TEXT DEFAULT 'en')")

async def get_lang(chat_id):
    await init_lang()
    record = await db.fetchone("SELECT lang FROM chat_langs WHERE chat_id = ?", chat_id)
    return record[0] if record else "en"

@Client.on_message(filters.command(["setlang", "set-language"]))
async def set_language_cmd(client: Client, message: Message):
    await init_lang()
    if message.chat.type in ["group", "supergroup"]:
        user_id = message.from_user.id if message.from_user else message.sender_chat.id
        if message.from_user:
            member = await client.get_chat_member(message.chat.id, user_id)
            if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                return await message.reply_text("🌸 Only group admins can change the language!")

    current_lang = await get_lang(message.chat.id)
    buttons = []
    row = []
    for code, lang_data in LANGUAGES.items():
        prefix = "✅ " if code == current_lang else ""
        row.append(InlineKeyboardButton(f"{prefix}{lang_data['name']}", callback_data=f"setlang_{code}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row: buttons.append(row)

    await message.reply_text("🌸 **Choose the language for this chat:**", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"^setlang_(.*)$"))
async def lang_callback(client: Client, query: CallbackQuery):
    code = query.matches[0].group(1)
    chat_id = query.message.chat.id
    if query.message.chat.type in ["group", "supergroup"]:
        member = await client.get_chat_member(chat_id, query.from_user.id)
        if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            return await query.answer("🌸 You must be an admin to change this!", show_alert=True)

    if code not in LANGUAGES: return await query.answer("Invalid Language!", show_alert=True)

    await db.execute("INSERT OR REPLACE INTO chat_langs (chat_id, lang) VALUES (?, ?)", chat_id, code)
    await query.message.edit_text(LANGUAGES[code]["set"])
"""

# =========================================================
# 4. FEDERATIONS MODULE (Fixed & Anonymous Admin Checked)
# =========================================================
FEDS_CODE = """import logging
import uuid
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from modules.database import db

logger = logging.getLogger("WaguriBot.Feds")

async def init_feds():
    await db.execute("CREATE TABLE IF NOT EXISTS feds (fed_id TEXT PRIMARY KEY, name TEXT, creator_id INTEGER)")
    await db.execute("CREATE TABLE IF NOT EXISTS fed_chats (chat_id INTEGER PRIMARY KEY, fed_id TEXT)")
    await db.execute("CREATE TABLE IF NOT EXISTS fed_bans (fed_id TEXT, user_id INTEGER, reason TEXT, PRIMARY KEY(fed_id, user_id))")

@Client.on_message(filters.command("newfed"))
async def new_fed(client: Client, message: Message):
    await init_feds()
    if len(message.command) < 2: return await message.reply_text("🌸 Usage: `/newfed [Federation Name]`")
    
    fed_name = message.text.split(None, 1)[1]
    fed_id = str(uuid.uuid4())[:8]
    user_id = message.from_user.id if message.from_user else message.sender_chat.id
    
    try:
        await db.execute("INSERT INTO feds (fed_id, name, creator_id) VALUES (?, ?, ?)", fed_id, fed_name, user_id)
        await message.reply_text(f"🌸 **Federation Created!**\\n\\n**Name:** `{fed_name}`\\n**Fed ID:** `{fed_id}`\\n\\nGroup admins can now join your fed using:\\n`/joinfed {fed_id}`")
    except Exception as e:
        await message.reply_text("🌸 Error creating federation. You might already own one!")

@Client.on_message(filters.command("joinfed") & filters.group)
async def join_fed(client: Client, message: Message):
    await init_feds()
    if len(message.command) < 2: return await message.reply_text("🌸 Usage: `/joinfed [Fed ID]`")
    
    user_id = message.from_user.id if message.from_user else None
    if user_id:
        member = await client.get_chat_member(message.chat.id, user_id)
        if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            return await message.reply_text("🌸 Only group admins can link this chat to a Federation!")
            
    fed_id = message.command[1]
    record = await db.fetchone("SELECT name FROM feds WHERE fed_id = ?", fed_id)
    if not record: return await message.reply_text("🌸 Invalid Federation ID. Please check the ID and try again.")
    
    await db.execute("INSERT OR REPLACE INTO fed_chats (chat_id, fed_id) VALUES (?, ?)", message.chat.id, fed_id)
    await message.reply_text(f"🌸 Successfully joined the Federation: **{record[0]}**!\\nFbans from this fed will now be enforced here.")
"""

# =========================================================
# WRITE THE FILES 
# =========================================================
files_to_write = {
    "modules/start.py": START_CODE,
    "modules/version.py": VERSION_CODE,
    "modules/language.py": LANG_CODE,
    "modules/feds.py": FEDS_CODE,
}

for filepath, content in files_to_write.items():
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Successfully wrote and patched {filepath}")

print("\n🚀 WAGURI ULTIMATE PATCH V5 COMPLETE! Restart your bot: python bot.py")
