import logging
import httpx
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction

from config import Config

logger = logging.getLogger("WaguriBot.AI")

# Note: In an enterprise setting, an asynchronous OpenAI client (from `openai` package) is ideal.
# To minimize heavy external dependencies while preserving async HTTP capabilities, we use httpx directly.
# This assumes OPENAI_API_KEY is configured in Config.

async def fetch_openai_response(prompt: str, system_prompt: str = "You are Waguri, a friendly, elegant, anime-inspired AI assistant.") -> str:
    if not Config.OPENAI_API_KEY:
        return "🌸 My AI core is currently offline! (API key missing)"
        
    headers = {
        "Authorization": f"Bearer {Config.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-3.5-turbo", # Can be upgraded to gpt-4
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as http_client:
            resp = await http_client.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload,
                headers=headers
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"OpenAI fetch error: {e}")
        return "🌸 Oh no! My connection to the neural network failed..."

@Client.on_message(filters.command(["ask", "waguri"]) & filters.group)
async def ask_ai(client: Client, message: Message):
    if not Config.ENABLE_AI:
        return await message.reply_text("🌸 AI features are currently disabled by my master.")
        
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply_text("🌸 You need to ask me a question! Example: `/ask What is the speed of light?`")
        
    query = message.text.split(None, 1)[1] if len(message.command) > 1 else message.reply_to_message.text
    
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    response = await fetch_openai_response(query)
    
    await message.reply_text(response)

@Client.on_message(filters.command("summarize") & filters.group)
async def summarize_chat(client: Client, message: Message):
    if not Config.ENABLE_AI:
        return
        
    if not message.reply_to_message:
        return await message.reply_text("🌸 Please reply to the first message of a conversation you want me to summarize.")
        
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    
    # Fetch previous 20 messages for context
    msg_id = message.reply_to_message.id
    history = []
    
    async for msg in client.get_chat_history(message.chat.id, limit=20, offset_id=msg_id + 20):
        if msg.text and not msg.text.startswith("/"):
            author = msg.from_user.first_name if msg.from_user else "Unknown"
            history.append(f"{author}: {msg.text}")
            
    history.reverse()
    
    if not history:
        return await message.reply_text("🌸 I couldn't find enough text to summarize!")
        
    conversation = "\n".join(history)
    prompt = f"Summarize the following chat conversation briefly and elegantly:\n\n{conversation}"
    
    response = await fetch_openai_response(prompt, "You are a professional assistant that provides concise, accurate summaries.")
    
    await message.reply_text(f"🌸 **Conversation Summary:**\n\n{response}")

@Client.on_message(filters.command(["grammar", "correct"]) & filters.group)
async def correct_grammar(client: Client, message: Message):
    if not Config.ENABLE_AI:
        return
        
    if not message.reply_to_message or not message.reply_to_message.text:
        return await message.reply_text("🌸 Please reply to a text message to correct its grammar.")
        
    original_text = message.reply_to_message.text
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    
    prompt = f"Fix all grammatical and spelling errors in this text while preserving the original meaning:\n\n'{original_text}'"
    response = await fetch_openai_response(prompt, "You are a helpful language teacher. Return only the corrected text without any extra chat.")
    
    await message.reply_text(f"🌸 **Corrected Text:**\n\n`{response}`")
