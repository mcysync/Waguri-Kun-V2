import os
import logging
import httpx
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config

logger = logging.getLogger("WaguriBot.Fun")

@Client.on_message(filters.command("waifu") & filters.group)
async def get_waifu(client: Client, message: Message):
    if not Config.ENABLE_ANIME: return
    msg = await message.reply_text("🌸 Fetching a cute waifu...")
    try:
        async with httpx.AsyncClient(timeout=15.0) as http_client:
            res = await http_client.get("https://api.waifu.pics/sfw/waifu")
            img_res = await http_client.get(res.json()["url"])
            
            # 🔥 CRITICAL TERMUX FIX: Physical file writing
            filename = f"waifu_{message.id}.jpg"
            with open(filename, "wb") as f:
                f.write(img_res.content)
            
            await message.reply_photo(photo=filename, caption="🌸 Here is a cute waifu for you! ✨")
            await msg.delete()
            
            if os.path.exists(filename):
                os.remove(filename)
    except Exception as e:
        await msg.edit_text(f"🌸 Failed: `{e}`")

@Client.on_message(filters.command("slap") & filters.group)
async def action_slap(client: Client, message: Message):
    if not message.reply_to_message: return await message.reply_text("🌸 Reply to a user to slap them!")
    try:
        async with httpx.AsyncClient(timeout=15.0) as http_client:
            res = await http_client.get("https://api.waifu.pics/sfw/slap")
            img_res = await http_client.get(res.json()["url"])
            
            filename = f"slap_{message.id}.gif"
            with open(filename, "wb") as f:
                f.write(img_res.content)
            
            sender = message.from_user.mention if message.from_user else "Someone"
            target = message.reply_to_message.from_user.mention if message.reply_to_message.from_user else "Someone"
            await message.reply_animation(animation=filename, caption=f"💥 **{sender}** violently slapped **{target}**!")
            
            if os.path.exists(filename):
                os.remove(filename)
    except Exception:
        await message.reply_text("🌸 *slaps!*")
