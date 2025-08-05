import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Stores users looking for chat
waiting_users = []
active_chats = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to Anonymous Chat Bot! Use /find to start chatting.")

async def find(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in active_chats:
        await update.message.reply_text("You are already in a chat. Use /stop to leave.")
        return
    if waiting_users:
        partner_id = waiting_users.pop(0)
        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id
        await context.bot.send_message(chat_id=partner_id, text="🔗 You are now connected to a stranger. Say hi!")
        await update.message.reply_text("🔗 You are now connected to a stranger. Say hi!")
    else:
        waiting_users.append(user_id)
        await update.message.reply_text("⏳ Waiting for someone to connect...")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in active_chats:
        partner_id = active_chats.pop(user_id)
        active_chats.pop(partner_id, None)
        await context.bot.send_message(chat_id=partner_id, text="❌ Stranger has left the chat.")
        await update.message.reply_text("❌ You left the chat.")
    else:
        if user_id in waiting_users:
            waiting_users.remove(user_id)
        await update.message.reply_text("❌ You are not in any chat.")

async def relay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        try:
            await context.bot.send_message(chat_id=partner_id, text=update.message.text)
        except:
            await update.message.reply_text("❌ Message delivery failed.")
    else:
        await update.message.reply_text("❗ Use /find to start a chat.")

def main():
    import os
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        print("❌ Please set your BOT_TOKEN environment variable.")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("find", find))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, relay))

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
