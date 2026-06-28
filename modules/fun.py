import logging
import httpx
from pyrogram import Client, filters
from pyrogram.types import Message

from config import Config

logger = logging.getLogger("WaguriBot.Fun")

@Client.on_message(filters.command("anime") & filters.group)
async def search_anime(client: Client, message: Message):
    if not Config.ENABLE_ANIME: return
    if len(message.command) < 2: return await message.reply_text("🌸 Please provide an anime name. Example: `/anime Naruto`")
        
    query = message.text.split(None, 1)[1]
    
    try:
        async with httpx.AsyncClient() as http_client:
            res = await http_client.get(f"https://api.jikan.moe/v4/anime?q={query}&limit=1")
            res.raise_for_status()
            data = res.json()
            
            if not data.get("data"): return await message.reply_text("🌸 I couldn't find any anime with that name!")
                
            anime = data["data"][0]
            caption = f"🌸 **{anime.get('title')}**\n\n**Episodes:** `{anime.get('episodes', 'Unknown')}`\n**Status:** `{anime.get('status', 'Unknown')}`\n**Score:** ⭐ `{anime.get('score', 'N/A')}`\n\n**Synopsis:** {anime.get('synopsis', 'N/A')[:300]}...\n\n🔗 [More Info]({anime.get('url')})"
            
            # Use raw URL - No downloading required
            await message.reply_photo(photo=str(anime["images"]["jpg"]["large_image_url"]), caption=caption)
            
    except Exception as e:
        await message.reply_text("🌸 Oops! The MyAnimeList API seems to be sleeping.")

@Client.on_message(filters.command("waifu") & filters.group)
async def get_waifu(client: Client, message: Message):
    if not Config.ENABLE_ANIME: return
        
    try:
        async with httpx.AsyncClient() as http_client:
            res = await http_client.get("https://api.waifu.pics/sfw/waifu")
            res.raise_for_status()
            url = res.json()["url"]
            
            # 🔥 CRITICAL FIX: Tell Telegram to fetch the URL directly
            await message.reply_photo(photo=url, caption="🌸 Here is a cute waifu for you! ✨")
    except Exception as e:
        await message.reply_text(f"🌸 I couldn't fetch a picture right now: `{e}`")

@Client.on_message(filters.command("quote") & filters.group)
async def anime_quote(client: Client, message: Message):
    if not Config.ENABLE_ANIME: return
    try:
        async with httpx.AsyncClient() as http_client:
            res = await http_client.get("https://animechan.xyz/api/random")
            res.raise_for_status()
            data = res.json()
            await message.reply_text(f"🌸 *\"{data.get('quote')}\"*\n\n— **{data.get('character')}** ({data.get('anime')})")
    except Exception:
        await message.reply_text("🌸 Could not retrieve a quote at this time.")

@Client.on_message(filters.command("slap") & filters.group)
async def action_slap(client: Client, message: Message):
    if not message.reply_to_message: return await message.reply_text("🌸 Reply to a user to slap them!")
        
    try:
        async with httpx.AsyncClient() as http_client:
            res = await http_client.get("https://api.waifu.pics/sfw/slap")
            url = res.json()["url"]
            
            sender = message.from_user.mention if message.from_user else "Someone"
            target = message.reply_to_message.from_user.mention if message.reply_to_message.from_user else "Someone"
            
            # 🔥 CRITICAL FIX: Tell Telegram to fetch the URL directly
            await message.reply_animation(animation=url, caption=f"💥 **{sender}** violently slapped **{target}**!")
    except Exception:
        await message.reply_text("🌸 *slaps!*")
