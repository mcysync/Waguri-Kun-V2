import logging
import base64
import uuid
import hashlib
import json
import urllib.parse
from pyrogram import Client, filters
from pyrogram.types import Message
import httpx

from config import Config

logger = logging.getLogger("WaguriBot.Utility")

@Client.on_message(filters.command("base64"))
async def encode_decode_b64(client: Client, message: Message):
    args = message.text.split(None, 2)
    if len(args) < 3:
        return await message.reply_text("🌸 Usage: `/base64 [encode|decode] [text]`")
        
    action = args[1].lower()
    text = args[2]
    
    try:
        if action == "encode":
            result = base64.b64encode(text.encode()).decode()
            await message.reply_text(f"🌸 **Encoded Base64:**\n`{result}`")
        elif action == "decode":
            result = base64.b64decode(text.encode()).decode()
            await message.reply_text(f"🌸 **Decoded Text:**\n`{result}`")
        else:
            await message.reply_text("🌸 Use `encode` or `decode`.")
    except Exception:
        await message.reply_text("🌸 Failed to process. Are you sure it's valid Base64?")

@Client.on_message(filters.command("uuid"))
async def generate_uuid(client: Client, message: Message):
    val = str(uuid.uuid4())
    await message.reply_text(f"🌸 **Generated UUID (v4):**\n`{val}`")

@Client.on_message(filters.command("hash"))
async def hash_string(client: Client, message: Message):
    args = message.text.split(None, 2)
    if len(args) < 3:
        return await message.reply_text("🌸 Usage: `/hash [md5|sha1|sha256] [text]`")
        
    algo = args[1].lower()
    text = args[2].encode()
    
    if algo == "md5":
        res = hashlib.md5(text).hexdigest()
    elif algo == "sha1":
        res = hashlib.sha1(text).hexdigest()
    elif algo == "sha256":
        res = hashlib.sha256(text).hexdigest()
    else:
        return await message.reply_text("🌸 Unsupported algorithm! Use md5, sha1, or sha256.")
        
    await message.reply_text(f"🌸 **{algo.upper()} Hash:**\n`{res}`")

@Client.on_message(filters.command("weather"))
async def get_weather(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("🌸 Usage: `/weather [city]`")
        
    city = urllib.parse.quote(message.text.split(None, 1)[1])
    
    try:
        # Using wttr.in for simple format without needing an API key, 
        # though OpenWeather is better for enterprise.
        async with httpx.AsyncClient() as http_client:
            res = await http_client.get(f"https://wttr.in/{city}?format=3")
            res.raise_for_status()
            weather = res.text.strip()
            
            if not weather:
                return await message.reply_text("🌸 Couldn't find weather for that location.")
                
            await message.reply_text(f"🌸 **Weather Report:**\n\n`{weather}`")
    except Exception as e:
        logger.error(f"Weather error: {e}")
        await message.reply_text("🌸 Failed to retrieve weather data.")

@Client.on_message(filters.command("json"))
async def format_json(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.text:
        return await message.reply_text("🌸 Reply to a message containing JSON to prettify it.")
        
    try:
        parsed = json.loads(message.reply_to_message.text)
        pretty = json.dumps(parsed, indent=4)
        
        # Max message length check
        if len(pretty) > 4000:
            return await message.reply_text("🌸 The output JSON is too large for Telegram.")
            
        await message.reply_text(f"🌸 **Prettified JSON:**\n```json\n{pretty}\n```")
    except json.JSONDecodeError:
        await message.reply_text("🌸 Invalid JSON string provided!")
