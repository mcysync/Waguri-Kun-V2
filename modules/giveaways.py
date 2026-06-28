import logging
import random
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from utils import admin_required
from modules.database import db

logger = logging.getLogger("WaguriBot.Giveaways")

active_giveaways = {}

@Client.on_message(filters.command("giveaway") & filters.group)
@admin_required("can_change_info")
async def start_giveaway(client: Client, message: Message):
    args = message.text.split(None, 1)
    if len(args) < 2:
        return await message.reply_text("🌸 Usage: `/giveaway [Prize Name]`")
        
    prize = args[1]
    
    btn = InlineKeyboardMarkup([[InlineKeyboardButton("🎉 Join Giveaway", callback_data="gaw_join")]])
    
    msg = await message.reply_text(
        f"🌸 **GIVEAWAY TIME!** 🎉\n\n**Prize:** `{prize}`\n**Hosted by:** {message.from_user.mention}\n\nClick the button below to join!",
        reply_markup=btn
    )
    
    active_giveaways[msg.id] = {
        "prize": prize,
        "host": message.from_user.id,
        "participants": set()
    }

@Client.on_callback_query(filters.regex("gaw_join"))
async def join_giveaway(client: Client, callback_query):
    msg_id = callback_query.message.id
    if msg_id not in active_giveaways:
        return await callback_query.answer("🌸 This giveaway has ended!", show_alert=True)
        
    user_id = callback_query.from_user.id
    
    if user_id in active_giveaways[msg_id]["participants"]:
        return await callback_query.answer("🌸 You are already in the giveaway!", show_alert=True)
        
    active_giveaways[msg_id]["participants"].add(user_id)
    await callback_query.answer("🌸 You have successfully joined the giveaway!", show_alert=True)
    
    # Update participant count
    count = len(active_giveaways[msg_id]["participants"])
    prize = active_giveaways[msg_id]["prize"]
    
    btn = InlineKeyboardMarkup([[InlineKeyboardButton(f"🎉 Join Giveaway ({count})", callback_data="gaw_join")]])
    await callback_query.message.edit_text(
        f"🌸 **GIVEAWAY TIME!** 🎉\n\n**Prize:** `{prize}`\n\nParticipants: `{count}`",
        reply_markup=btn
    )

@Client.on_message(filters.command("endgiveaway") & filters.group)
@admin_required("can_change_info")
async def end_giveaway(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("🌸 Reply to the giveaway message to end it.")
        
    msg_id = message.reply_to_message.id
    if msg_id not in active_giveaways:
        return await message.reply_text("🌸 Could not find an active giveaway for that message.")
        
    participants = list(active_giveaways[msg_id]["participants"])
    prize = active_giveaways[msg_id]["prize"]
    
    if not participants:
        await message.reply_text("🌸 Giveaway ended, but nobody joined! 😢")
    else:
        winner_id = random.choice(participants)
        winner = await client.get_users(winner_id)
        
        await message.reply_text(f"🌸 **GIVEAWAY ENDED!** 🎉\n\n**Prize:** `{prize}`\n**Winner:** {winner.mention}\n\nCongratulations! 🎊")
        
    # Clean up button
    await message.reply_to_message.edit_text(
        f"🌸 **GIVEAWAY ENDED!** 🎉\n\n**Prize:** `{prize}`\n(This giveaway is now closed)"
    )
    del active_giveaways[msg_id]
