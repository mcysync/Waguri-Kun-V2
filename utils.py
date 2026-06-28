import re
from functools import wraps
from typing import Callable, Optional, Union

from pyrogram import Client
from pyrogram.types import Message, CallbackQuery
from pyrogram.enums import ChatMemberStatus, ChatType

from config import Config

TIME_REGEX = re.compile(r"(\d+)([smhd])")

def parse_time(time_str: str) -> Optional[int]:
    match = TIME_REGEX.match(time_str.lower())
    if not match: return None
    value, unit = int(match.group(1)), match.group(2)
    multipliers = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
    return value * multipliers[unit]

def owner_only(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(client: Client, update: Union[Message, CallbackQuery], *args, **kwargs):
        user_id = update.from_user.id if update.from_user else 0
        if user_id != Config.OWNER_ID:
            if isinstance(update, Message): await update.reply_text("🌸 Strictly for my master.")
            else: await update.answer("Strictly for my master!", show_alert=True)
            return
        return await func(client, update, *args, **kwargs)
    return wrapper

def sudo_only(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(client: Client, update: Union[Message, CallbackQuery], *args, **kwargs):
        user_id = update.from_user.id if update.from_user else 0
        if not Config.is_sudo(user_id):
            if isinstance(update, Message): await update.reply_text("🌸 Sudo privileges required!")
            else: await update.answer("Sudo privileges required!", show_alert=True)
            return
        return await func(client, update, *args, **kwargs)
    return wrapper

def admin_required(permissions: Optional[str] = None):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(client: Client, message: Message, *args, **kwargs):
            if message.chat.type == ChatType.PRIVATE:
                return await func(client, message, *args, **kwargs)
            
            if message.sender_chat:
                return await func(client, message, *args, **kwargs)
                
            if not message.from_user:
                return await message.reply_text("🌸 I couldn't identify your user profile.")
                
            user_id = message.from_user.id
            if Config.is_sudo(user_id): 
                return await func(client, message, *args, **kwargs)
                
            try:
                member = await client.get_chat_member(message.chat.id, user_id)
            except Exception:
                return await message.reply_text("🌸 I couldn't verify your admin status.")
            
            if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return await message.reply_text("🌸 You need to be an admin to use this command!")
                
            if permissions and member.status != ChatMemberStatus.OWNER:
                if not getattr(member.privileges, permissions, False):
                    return await message.reply_text(f"🌸 You lack the `{permissions}` privilege!")
                    
            return await func(client, message, *args, **kwargs)
        return wrapper
    return decorator

def bot_admin_required(permissions: Optional[str] = None):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(client: Client, message: Message, *args, **kwargs):
            if message.chat.type == ChatType.PRIVATE:
                return await func(client, message, *args, **kwargs)
                
            try:
                bot_member = await client.get_chat_member(message.chat.id, client.me.id)
            except Exception:
                return await message.reply_text("🌸 Please make me an admin first!")
            
            if bot_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return await message.reply_text("🌸 Please make me an admin first!")
                
            if permissions and bot_member.status != ChatMemberStatus.OWNER:
                if not getattr(bot_member.privileges, permissions, False):
                    return await message.reply_text(f"🌸 I need the `{permissions}` right to do that!")
                    
            return await func(client, message, *args, **kwargs)
        return wrapper
    return decorator

# THE BULLETPROOF TARGET EXTRACTOR
async def extract_target(client: Client, message: Message):
    """Returns (target_id, target_mention, reason) WITHOUT failing on network calls."""
    args = message.text.split() if message.text else []
    reason = None
    
    # 1. IF YOU REPLIED TO A MESSAGE (Zero API calls, instant execution)
    if message.reply_to_message:
        reason = " ".join(args[1:]) if len(args) > 1 else None
        if message.reply_to_message.from_user:
            u = message.reply_to_message.from_user
            return u.id, u.mention, reason
        elif message.reply_to_message.sender_chat:
            c = message.reply_to_message.sender_chat
            return c.id, f"**{c.title}**", reason

    # 2. IF YOU PROVIDED AN ID OR USERNAME IN TEXT
    if len(args) > 1:
        raw_target = args[1]
        reason = " ".join(args[2:]) if len(args) > 2 else None
        
        # If it's a numeric ID
        if raw_target.lstrip("-").isdigit():
            target_id = int(raw_target)
            try:
                user = await client.get_users(target_id)
                return user.id, user.mention, reason
            except Exception:
                return target_id, f"`{target_id}`", reason # Fallback to raw ID immediately
        
        # If it's a username (@name)
        else:
            try:
                user = await client.get_users(raw_target)
                return user.id, user.mention, reason
            except Exception:
                pass
                
    return None, None, None
