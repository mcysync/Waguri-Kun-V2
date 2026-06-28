import logging
import importlib
import os
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import owner_only

logger = logging.getLogger("WaguriBot.Plugins")

@Client.on_message(filters.command(["load", "reload"]) & filters.private)
@owner_only
async def load_plugin(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.reply_text("🌸 Master, provide a module name. Example: `/load fun`")
        
    module_name = args[1].lower()
    full_path = f"modules.{module_name}"
    
    try:
        # Check if file exists
        if not os.path.isfile(f"modules/{module_name}.py"):
            return await message.reply_text(f"🌸 Module `{module_name}` does not exist.")
            
        import sys
        if full_path in sys.modules:
            importlib.reload(sys.modules[full_path])
            action = "reloaded"
        else:
            importlib.import_module(full_path)
            action = "loaded"
            
        await message.reply_text(f"🌸 Module `{module_name}` {action} successfully! ✨")
    except Exception as e:
        logger.error(f"Plugin load error: {e}")
        await message.reply_text(f"🌸 Failed to load module `{module_name}`:\n`{e}`")
        
# Note: Unloading in Python is complex because references remain in memory, 
# especially with decorators like Pyrogram's @Client.on_message. 
# Production bot unloading requires tracking handler objects and calling client.remove_handler().
