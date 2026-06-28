import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger("WaguriBot.Start")

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    # Get bot info to generate the invite link
    me = await client.get_me()
    
    welcome_text = (
        f"🌸 **Hello there, {message.from_user.first_name}!**\n\n"
        f"I am **{me.first_name}**, an elegant and powerful enterprise bot.\n\n"
        f"🛡 **Moderation & Security**\n"
        f"💴 **Economy & Leveling**\n"
        f"🎌 **Anime & Utilities**\n\n"
        f"To see everything I can do, just type `/help`!\n"
        f"Add me to your group using the button below. ✨"
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌸 Add Waguri to your Group 🌸", url=f"https://t.me/{me.username}?startgroup=true")]
    ])
    
    await message.reply_text(welcome_text, reply_markup=buttons)

@Client.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    help_text = (
        "🌸 **Waguri Command Menu** 🌸\n\n"
        "**🛡 Moderation:**\n`/ban`, `/mute`, `/kick`, `/warn`, `/purge`, `/lock`, `/unlock`\n\n"
        "**🚨 Security:**\n`/raidmode`, `/antispam`, `/security`, `/captcha`\n\n"
        "**💰 Economy:**\n`/daily`, `/balance`, `/pay`, `/rank`, `/rep`\n\n"
        "**⚙️ Admin:**\n`/settings`, `/setwelcome`, `/filter`, `/notes`, `/stats`\n\n"
        "*(And over 200 more features running silently in the background!)*"
    )
    await message.reply_text(help_text)
