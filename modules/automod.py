import logging
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import admin_required
from modules.database import db
from modules.logging import log_event

logger = logging.getLogger("WaguriBot.AutoMod")

async def init_automod_db():
    await db.execute("""
        CREATE TABLE IF NOT EXISTS automod_rules (
            chat_id INTEGER,
            rule_type TEXT,
            action TEXT DEFAULT 'delete',
            PRIMARY KEY (chat_id, rule_type)
        )
    """)

import asyncio
asyncio.get_event_loop().create_task(init_automod_db())

RULE_TYPES = ["links", "invites", "profanity"]

@Client.on_message(filters.command("automod") & filters.group)
@admin_required("can_change_info")
async def configure_automod(client: Client, message: Message):
    args = message.command
    if len(args) < 3:
        return await message.reply_text(f"🌸 Usage: `/automod [rule] [on/off/action]`\nAvailable rules: `{', '.join(RULE_TYPES)}`")
        
    rule = args[1].lower()
    state_or_action = args[2].lower()
    
    if rule not in RULE_TYPES:
        return await message.reply_text(f"🌸 Invalid rule. Choose from: `{', '.join(RULE_TYPES)}`")
        
    if state_or_action == "off":
        await db.execute("DELETE FROM automod_rules WHERE chat_id = ? AND rule_type = ?", message.chat.id, rule)
        await message.reply_text(f"🌸 AutoMod for `{rule}` has been disabled.")
    else:
        action = state_or_action if state_or_action in ["delete", "warn", "mute", "ban"] else "delete"
        await db.execute(
            "INSERT OR REPLACE INTO automod_rules (chat_id, rule_type, action) VALUES (?, ?, ?)",
            message.chat.id, rule, action
        )
        await message.reply_text(f"🌸 AutoMod for `{rule}` enabled! Action set to: **{action.upper()}**")

@Client.on_message(filters.group & ~filters.bot & ~filters.me, group=10)
async def automod_enforcer(client: Client, message: Message):
    if not message.text and not message.caption:
        return
        
    text = (message.text or message.caption).lower()
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else 0
    
    rules = await db.fetchall("SELECT rule_type, action FROM automod_rules WHERE chat_id = ?", chat_id)
    if not rules:
        return
        
    # Exclude admins
    try:
        member = await client.get_chat_member(chat_id, user_id)
        if member.status in ["administrator", "creator"]:
            return
    except Exception:
        pass
        
    rule_dict = {r[0]: r[1] for r in rules}
    
    triggered_rule = None
    
    # Extremely basic profanity filter for demo
    # Enterprise version uses regex and external lists
    bad_words = {"fuck", "shit", "bitch"}
    
    if "invites" in rule_dict and ("t.me/joinchat" in text or "t.me/+" in text):
        triggered_rule = "invites"
    elif "links" in rule_dict and ("http://" in text or "https://" in text):
        triggered_rule = "links"
    elif "profanity" in rule_dict and any(word in text.split() for word in bad_words):
        triggered_rule = "profanity"
        
    if triggered_rule:
        action = rule_dict[triggered_rule]
        
        try:
            if action in ["delete", "warn", "mute", "ban"]:
                await message.delete()
                
            if action == "ban":
                await client.ban_chat_member(chat_id, user_id)
            elif action == "mute":
                from pyrogram.types import ChatPermissions
                await client.restrict_chat_member(chat_id, user_id, ChatPermissions(can_send_messages=False))
                
            await log_event(client, chat_id, f"AutoMod: {message.from_user.mention} triggered `{triggered_rule}`. Action: {action}")
            
        except Exception as e:
            logger.error(f"AutoMod enforcement error: {e}")
