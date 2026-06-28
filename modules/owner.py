import logging
import traceback
import io
from contextlib import redirect_stdout
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import owner_only
from modules.database import db

logger = logging.getLogger("WaguriBot.Owner")

@Client.on_message(filters.command(["exec", "eval"]) & filters.private)
@owner_only
async def eval_code(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("🌸 Master, you need to provide code to execute!")
        
    code = message.text.split(None, 1)[1]
    
    # Set up the environment
    local_vars = {
        "client": client,
        "message": message,
        "db": db,
        "bot": client
    }
    
    stdout = io.StringIO()
    
    # Wrap in async function for awaiting
    wrapped_code = f"async def __ex():\n" + "".join(f"    {line}\n" for line in code.split("\n"))
    
    try:
        exec(wrapped_code, globals(), local_vars)
        func = local_vars["__ex"]
        
        with redirect_stdout(stdout):
            ret = await func()
            
        output = stdout.getvalue()
        
        if ret is not None:
            output += f"\nReturn: {ret}"
            
        if not output.strip():
            output = "Code executed successfully with no output."
            
        # Handle long outputs
        if len(output) > 4000:
            with open("data/temp/eval_output.txt", "w") as f:
                f.write(output)
            await message.reply_document("data/temp/eval_output.txt", caption="🌸 Output too long, sent as file.")
        else:
            await message.reply_text(f"🌸 **Eval Results:**\n\n```python\n{output}\n```")
            
    except Exception as e:
        err = traceback.format_exc()
        await message.reply_text(f"🌸 **Error:**\n\n```python\n{err}\n```")

@Client.on_message(filters.command("broadcast") & filters.private)
@owner_only
async def broadcast_message(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("🌸 Master, please reply to the message you want to broadcast.")
        
    msg = await message.reply_text("🌸 Fetching chat list and starting broadcast...")
    
    records = await db.fetchall("SELECT chat_id FROM chats")
    success = 0
    failed = 0
    
    for (chat_id,) in records:
        try:
            await message.reply_to_message.copy(chat_id)
            success += 1
        except Exception:
            failed += 1
            # Usually happens if the bot is kicked from the chat
            await db.execute("DELETE FROM chats WHERE chat_id = ?", chat_id)
            
    await msg.edit_text(f"🌸 **Broadcast Complete!** ✨\n\n✅ Sent to: `{success}` chats\n❌ Failed: `{failed}` chats")

@Client.on_message(filters.command("leavechat") & filters.private)
@owner_only
async def force_leave(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.reply_text("🌸 Provide the Chat ID to leave.")
        
    try:
        chat_id = int(args[1])
        await client.leave_chat(chat_id)
        await db.execute("DELETE FROM chats WHERE chat_id = ?", chat_id)
        await message.reply_text(f"🌸 Successfully left the chat `{chat_id}`.")
    except ValueError:
        await message.reply_text("🌸 Invalid Chat ID format.")
    except Exception as e:
        await message.reply_text(f"🌸 Failed to leave chat: `{e}`")
