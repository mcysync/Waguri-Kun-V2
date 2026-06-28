import logging
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message

from config import Config
from modules.database import db

logger = logging.getLogger("WaguriBot.Economy")

# Using the pre-defined 'economy' schema from database.py

@Client.on_message(filters.command("daily"))
async def daily_reward(client: Client, message: Message):
    if not Config.ENABLE_ECONOMY:
        return
        
    user_id = message.from_user.id
    
    # Ensure user exists in users table
    await db.execute("INSERT OR IGNORE INTO users (user_id, first_name) VALUES (?, ?)", user_id, message.from_user.first_name)
    
    record = await db.fetchone("SELECT last_daily FROM economy WHERE user_id = ?", user_id)
    
    now = datetime.now()
    if record and record[0]:
        last_daily = datetime.strptime(record[0], "%Y-%m-%d %H:%M:%S.%f")
        if now < last_daily + timedelta(days=1):
            time_left = (last_daily + timedelta(days=1)) - now
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return await message.reply_text(f"🌸 You already claimed your daily reward!\nCome back in `{hours}h {minutes}m`.")
            
    reward = 500
    
    await db.execute(
        "INSERT OR REPLACE INTO economy (user_id, wallet, bank, last_daily) "
        "VALUES (?, COALESCE((SELECT wallet FROM economy WHERE user_id = ?), 0) + ?, "
        "COALESCE((SELECT bank FROM economy WHERE user_id = ?), 0), ?)",
        user_id, user_id, reward, user_id, now
    )
    
    await message.reply_text(f"🌸 Yay! You claimed your daily reward of 🪙 **{reward} Coins**!")

@Client.on_message(filters.command(["balance", "bal", "wallet"]))
async def check_balance(client: Client, message: Message):
    if not Config.ENABLE_ECONOMY:
        return
        
    user_id = message.from_user.id
    
    record = await db.fetchone("SELECT wallet, bank FROM economy WHERE user_id = ?", user_id)
    wallet = record[0] if record else 0
    bank = record[1] if record else 0
    
    text = f"🌸 **{message.from_user.first_name}'s Balance:**\n\n"
    text += f"👛 **Wallet:** `{wallet}` Coins\n"
    text += f"🏦 **Bank:** `{bank}` Coins\n"
    text += f"💰 **Total:** `{wallet + bank}` Coins\n"
    
    await message.reply_text(text)

@Client.on_message(filters.command("pay") & filters.group)
async def pay_user(client: Client, message: Message):
    if not Config.ENABLE_ECONOMY:
        return
        
    if not message.reply_to_message:
        return await message.reply_text("🌸 Reply to a user to send them money.")
        
    args = message.command
    if len(args) < 2:
        return await message.reply_text("🌸 Usage: `/pay [amount]`")
        
    try:
        amount = int(args[1])
        if amount <= 0:
            raise ValueError
    except ValueError:
        return await message.reply_text("🌸 Please provide a valid positive amount.")
        
    sender_id = message.from_user.id
    receiver_id = message.reply_to_message.from_user.id
    
    if sender_id == receiver_id:
        return await message.reply_text("🌸 You can't pay yourself!")
        
    sender_rec = await db.fetchone("SELECT wallet FROM economy WHERE user_id = ?", sender_id)
    if not sender_rec or sender_rec[0] < amount:
        return await message.reply_text("🌸 You don't have enough coins in your wallet!")
        
    # Process transaction
    await db.execute("UPDATE economy SET wallet = wallet - ? WHERE user_id = ?", amount, sender_id)
    await db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", receiver_id)
    await db.execute(
        "INSERT OR REPLACE INTO economy (user_id, wallet, bank) VALUES (?, COALESCE((SELECT wallet FROM economy WHERE user_id = ?), 0) + ?, COALESCE((SELECT bank FROM economy WHERE user_id = ?), 0))",
        receiver_id, receiver_id, amount, receiver_id
    )
    
    await message.reply_text(f"🌸 Transaction Successful! 💸\nYou sent **{amount} Coins** to {message.reply_to_message.from_user.mention}.")
