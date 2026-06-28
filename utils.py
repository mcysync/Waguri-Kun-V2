import re
import time
import asyncio
from functools import wraps
from typing import Callable, Any, Optional, Union

from pyrogram import Client
from pyrogram.types import Message, CallbackQuery, ChatPermissions
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import MessageNotModified, UserAdminInvalid, ChatAdminRequired

from config import Config

# Time parsers
TIME_REGEX = re.compile(r"(\d+)([smhd])")

def parse_time(time_str: str) -> Optional[int]:
    """Parses a time string like '1d', '2h', '30m' to seconds."""
    match = TIME_REGEX.match(time_str.lower())
    if not match:
        return None
    value, unit = int(match.group(1)), match.group(2)
    multipliers = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
    return value * multipliers[unit]

def format_time(seconds: int) -> str:
    """Formats seconds into a human-readable string."""
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    parts = []
    if d: parts.append(f"{d}d")
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}m")
    if s: parts.append(f"{s}s")
    return " ".join(parts) if parts else "0s"

# Decorators for permissions
def owner_only(func: Callable) -> Callable:
    """Decorator to restrict commands to the bot owner."""
    @wraps(func)
    async def wrapper(client: Client, update: Union[Message, CallbackQuery], *args, **kwargs):
        user_id = update.from_user.id if update.from_user else 0
        if user_id != Config.OWNER_ID:
            if isinstance(update, Message):
                await update.reply_text("🌸 Gomen'nasai! This command is strictly for my master.")
            else:
                await update.answer("Strictly for my master!", show_alert=True)
            return
        return await func(client, update, *args, **kwargs)
    return wrapper

def sudo_only(func: Callable) -> Callable:
    """Decorator to restrict commands to sudo users."""
    @wraps(func)
    async def wrapper(client: Client, update: Union[Message, CallbackQuery], *args, **kwargs):
        user_id = update.from_user.id if update.from_user else 0
        if not Config.is_sudo(user_id):
            if isinstance(update, Message):
                await update.reply_text("🌸 You don't have enough privileges to use this, sweetheart!")
            else:
                await update.answer("Sudo privileges required!", show_alert=True)
            return
        return await func(client, update, *args, **kwargs)
    return wrapper

def admin_required(permissions: Optional[str] = None):
    """
    Decorator to check if a user is an admin, and optionally check specific permissions.
    E.g., @admin_required("can_restrict_members")
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(client: Client, message: Message, *args, **kwargs):
            if message.chat.type == ChatType.PRIVATE:
                return await func(client, message, *args, **kwargs)
            
            user_id = message.from_user.id if message.from_user else 0
            
            # Sudo users bypass admin checks
            if Config.is_sudo(user_id):
                return await func(client, message, *args, **kwargs)
                
            member = await client.get_chat_member(message.chat.id, user_id)
            
            if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                await message.reply_text("🌸 You need to be an admin to use this command!")
                return
                
            if permissions and not getattr(member.privileges, permissions, False) and member.status != ChatMemberStatus.OWNER:
                await message.reply_text(f"🌸 You lack the `{permissions}` privilege required for this action!")
                return
                
            return await func(client, message, *args, **kwargs)
        return wrapper
    return decorator

def bot_admin_required(permissions: Optional[str] = None):
    """
    Decorator to check if the bot is an admin with required privileges.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(client: Client, message: Message, *args, **kwargs):
            if message.chat.type == ChatType.PRIVATE:
                return await func(client, message, *args, **kwargs)
                
            bot_member = await client.get_chat_member(message.chat.id, "me")
            
            if bot_member.status != ChatMemberStatus.ADMINISTRATOR:
                await message.reply_text("🌸 Please make me an admin first so I can help you properly!")
                return
                
            if permissions and not getattr(bot_member.privileges, permissions, False):
                await message.reply_text(f"🌸 I need the `{permissions}` right to do that!")
                return
                
            return await func(client, message, *args, **kwargs)
        return wrapper
    return decorator

# Text formatting utilities
def escape_markdown(text: str) -> str:
    """Escapes markdown characters in text."""
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)

def extract_user(message: Message) -> tuple[Optional[int], Optional[str]]:
    """Extracts target user ID and reason from a message (handles replies and mentions)."""
    user_id = None
    reason = None
    args = message.text.split()

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        reason = " ".join(args[1:]) if len(args) > 1 else None
    else:
        if len(args) > 1:
            if args[1].isdigit():
                user_id = int(args[1])
                reason = " ".join(args[2:]) if len(args) > 2 else None
            elif args[1].startswith("@"):
                user_id = args[1] # Will need to be resolved by Pyrogram
                reason = " ".join(args[2:]) if len(args) > 2 else None
                
    return user_id, reason
