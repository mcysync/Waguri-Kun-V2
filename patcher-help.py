import os

print("🌸 WAGURI ULTIMATE MEGA-PATCHER INITIATED 🌸\n")
os.makedirs("modules", exist_ok=True)

# =========================================================
# 1. START / HELP MODULE (Ultimate Buttons Edition)
# =========================================================
START_CODE = """import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

logger = logging.getLogger("WaguriBot.Start")
START_GIF = "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExMHlkY3huNXRtczFxaGp1enR6NmkzdmM3cjRoMjh0aWtvc3l3bXcwdCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/oDyhKNwTv0Zy9TbKtV/giphy.gif"

# Categorized commands for the ultimate button grid
CMDS = {
    "mod": ["ban", "tban", "sban", "shadowban", "unban", "mute", "tmute", "smute", "unmute", "kick", "purge", "warn", "swarn", "warnings", "clearwarns", "rmwarns", "lock", "unlock", "locks", "mutemedia", "mutevoice"],
    "admin": ["settings", "setlang", "setwelcome", "welcome", "setgoodbye", "goodbye", "setlog", "unsetlog", "pin", "unpin", "unpinall", "promote", "demote", "tagall", "all", "stopall", "cancelall", "report", "reports", "filter", "stop", "unfilter", "filters", "save", "note", "get", "clear", "notes", "saved", "blacklist", "unblacklist", "blacklisted", "whitelist", "unwhitelist", "approve", "disapprove", "verify", "unverify", "isverified", "afk", "leavechat"],
    "sec": ["antispam", "setflood", "floodmode", "raidmode", "lockdown", "captcha", "automod", "security"],
    "eco": ["daily", "balance", "bal", "wallet", "pay", "rank", "level", "rep", "treasure", "addpremium", "rmpremium", "mypremium"],
    "anime": ["ask", "waguri", "summarize", "grammar", "correct", "anime", "waifu", "quote", "slap", "weather", "poll", "giveaway", "endgiveaway", "schedule", "remind", "remindme", "reminders", "top", "topusers", "mystats"],
    "sys": ["start", "help", "ping", "stats", "sysinfo", "info", "userinfo", "base64", "hash", "uuid", "json", "joinfed", "newfed", "gban", "ungban", "broadcast", "backup", "restore", "vacuum", "clearcache", "restart", "exec", "eval", "webhook_info", "developer-options"]
}

HELP_TEXT = "🌸 **Here are all the commands available for Your lovely anime themed bot!** 🌸\\n\\nChoose a category below:"

def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛡 Moderation", callback_data="help_mod"), InlineKeyboardButton("⚙️ Admin & Setup", callback_data="help_admin")],
        [InlineKeyboardButton("🚨 Security", callback_data="help_sec"), InlineKeyboardButton("💴 Economy", callback_data="help_eco")],
        [InlineKeyboardButton("🎌 Anime & Fun", callback_data="help_anime"), InlineKeyboardButton("🛠 System & Feds", callback_data="help_sys")]
    ])

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
        
    if cat in CMDS:
        cmds_list = CMDS[cat]
        buttons = []
        row = []
        # Generate dynamic 3-column buttons
        for cmd in cmds_list:
            # Tap the button to automatically paste the command in chat!
            row.append(InlineKeyboardButton(f"/{cmd}", switch_inline_query_current_chat=f"/{cmd} "))
            if len(row) == 3:
                buttons.append(row)
                row = []
        if row: buttons.append(row)
        
        buttons.append([InlineKeyboardButton("🔙 Back to Main Menu", callback_data="help_main")])
        
        category_names = {"mod": "🛡 Moderation", "admin": "⚙️ Admin & Setup", "sec": "🚨 Security", "eco": "💴 Economy", "anime": "🎌 Anime & Fun", "sys": "🛠 System & Feds"}
        text = f"🌸 **{category_names[cat]} Commands**\\n\\nTap any button below to instantly type the command!"
        
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
"""

# =========================================================
# 2. FEDERATIONS MODULE (Fixed & Bulletproof)
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
    if len(message.command) < 2: 
        return await message.reply_text("🌸 Usage: `/newfed [Federation Name]`")
    
    fed_name = message.text.split(None, 1)[1]
    fed_id = str(uuid.uuid4())[:8] # Short, clean 8-character ID
    
    # Handle Anonymous Admins properly to prevent crash
    user_id = message.from_user.id if message.from_user else message.sender_chat.id
    
    try:
        await db.execute("INSERT INTO feds (fed_id, name, creator_id) VALUES (?, ?, ?)", fed_id, fed_name, user_id)
        await message.reply_text(f"🌸 **Federation Created!**\\n\\n**Name:** `{fed_name}`\\n**Fed ID:** `{fed_id}`\\n\\nGroup admins can now join your fed using:\\n`/joinfed {fed_id}`")
    except Exception as e:
        await message.reply_text("🌸 Error creating federation. You might already own one!")

@Client.on_message(filters.command("joinfed") & filters.group)
async def join_fed(client: Client, message: Message):
    await init_feds()
    if len(message.command) < 2: 
        return await message.reply_text("🌸 Usage: `/joinfed [Fed ID]`")
    
    # Native Admin Check (Bypasses faulty decorators)
    user_id = message.from_user.id if message.from_user else None
    if user_id:
        member = await client.get_chat_member(message.chat.id, user_id)
        if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            return await message.reply_text("🌸 Only group admins can link this chat to a Federation!")
            
    fed_id = message.command[1]
    record = await db.fetchone("SELECT name FROM feds WHERE fed_id = ?", fed_id)
    
    if not record: 
        return await message.reply_text("🌸 Invalid Federation ID. Please check the ID and try again.")
    
    await db.execute("INSERT OR REPLACE INTO fed_chats (chat_id, fed_id) VALUES (?, ?)", message.chat.id, fed_id)
    await message.reply_text(f"🌸 Successfully joined the Federation: **{record[0]}**!\\nFbans from this fed will now be enforced here.")
"""

# =========================================================
# WRITE THE FILES (Keeping existing good modules intact)
# =========================================================
files_to_write = {
    "modules/start.py": START_CODE,
    "modules/feds.py": FEDS_CODE,
}

for filepath, content in files_to_write.items():
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Successfully wrote and patched {filepath}")

print("\n🚀 WAGURI ULTIMATE PATCH COMPLETE. Restart your bot: python bot.py")
