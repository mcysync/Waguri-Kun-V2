import logging
import time
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions

from utils import admin_required, bot_admin_required
from modules.database import db

logger = logging.getLogger("WaguriBot.AntiRaid")

async def init_raid_db():
    await db.execute("""
        CREATE TABLE IF NOT EXISTS raid_settings (
            chat_id INTEGER PRIMARY KEY,
            is_active BOOLEAN DEFAULT 0,
            action TEXT DEFAULT 'kick',
            trigger_count INTEGER DEFAULT 5,
            time_window INTEGER DEFAULT 10
        )
    """)

import asyncio
asyncio.get_event_loop().create_task(init_raid_db())

# Memory state for joins
# {chat_id: [timestamps_of_recent_joins]}
join_tracker = {}

@Client.on_message(filters.command("raidmode") & filters.group)
@admin_required("can_restrict_members")
async def toggle_raidmode(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.reply_text("🌸 Usage: `/raidmode on` or `/raidmode off`")
        
    state = args[1].lower() == "on"
    
    await db.execute(
        "INSERT OR REPLACE INTO raid_settings (chat_id, is_active) VALUES (?, ?)",
        message.chat.id, state
    )
    
    if state:
        await message.reply_text("🌸 **Raid Mode ACTIVATED!** 🚨\nI will aggressively filter and remove fast-joining users.")
    else:
        await message.reply_text("🌸 **Raid Mode Deactivated.**\nThings look safe again. ✨")

@Client.on_message(filters.command("lockdown") & filters.group)
@admin_required("can_restrict_members")
@bot_admin_required("can_restrict_members")
async def group_lockdown(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.reply_text("🌸 Usage: `/lockdown on` or `/lockdown off`")
        
    state = args[1].lower() == "on"
    
    try:
        if state:
            permissions = ChatPermissions(can_send_messages=False)
            await client.set_chat_permissions(message.chat.id, permissions)
            await message.reply_text("🌸 **LOCKDOWN INITIATED!** 🔒\nThe chat has been completely locked. Regular members cannot send messages.")
        else:
            # Restore defaults (simplified to base permissions)
            permissions = ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
            await client.set_chat_permissions(message.chat.id, permissions)
            await message.reply_text("🌸 **Lockdown Lifted!** 🔓\nThe chat is open again.")
    except Exception as e:
        logger.error(f"Lockdown error: {e}")
        await message.reply_text("🌸 I failed to alter the chat permissions. Do I have the right rights?")

@Client.on_message(filters.new_chat_members, group=4)
async def antiraid_watcher(client: Client, message: Message):
    chat_id = message.chat.id
    
    settings = await db.fetchone("SELECT is_active, action, trigger_count, time_window FROM raid_settings WHERE chat_id = ?", chat_id)
    if not settings:
        return
        
    is_active, action, trigger_count, time_window = settings
    
    now = time.time()
    
    if chat_id not in join_tracker:
        join_tracker[chat_id] = []
        
    # Clean up old joins
    join_tracker[chat_id] = [ts for ts in join_tracker[chat_id] if now - ts <= time_window]
    
    # Process new members
    for new_member in message.new_chat_members:
        if new_member.is_bot:
            continue
            
        join_tracker[chat_id].append(now)
        
        # If raid mode is active, or trigger count exceeded
        if is_active or len(join_tracker[chat_id]) >= trigger_count:
            if not is_active:
                # Auto-activate raid mode if threshold met
                await db.execute("UPDATE raid_settings SET is_active = 1 WHERE chat_id = ?", chat_id)
                await message.reply_text("🌸 **EMERGENCY! Raid Detected!** 🚨\nAuto-enabling Raid Mode to protect the group.")
                is_active = True
                
            try:
                if action == "ban":
                    await client.ban_chat_member(chat_id, new_member.id)
                else: # default kick
                    await client.ban_chat_member(chat_id, new_member.id)
                    await client.unban_chat_member(chat_id, new_member.id)
            except Exception as e:
                logger.error(f"AntiRaid removal error: {e}")
