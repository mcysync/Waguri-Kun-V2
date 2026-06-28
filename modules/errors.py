import logging
import traceback
from pyrogram import Client
from pyrogram.errors import RPCError

from config import Config

logger = logging.getLogger("WaguriBot.Errors")

# Pyrogram doesn't have a direct global exception handler decorator for client updates like Discord.py does,
# but we can monkey-patch or subclass the dispatcher if deeply needed.
# Since we asked for standard implementation, we provide a structured logger utility 
# that can be hooked into custom dispatches or called in except blocks.

async def handle_error(client: Client, exception: Exception, context: str = "Unknown"):
    """
    Enterprise Centralized Error Handler.
    Call this inside try/except blocks across the bot to standardize logging and alerting.
    """
    err_text = f"🚨 **CRITICAL ERROR** 🚨\n\n**Context:** `{context}`\n**Type:** `{type(exception).__name__}`\n**Message:** `{str(exception)}`"
    
    logger.error(f"Error in {context}: {exception}")
    logger.debug(traceback.format_exc())
    
    # Optionally send to central log channel
    if Config.LOG_CHANNEL != 0:
        try:
            await client.send_message(Config.LOG_CHANNEL, err_text)
        except RPCError:
            pass # Failsafe if log channel is unreachable

# End of Project - WaguriBot Enterprise System Ready.
logger.info("Error handler module loaded. Waguri System fully operational.")
