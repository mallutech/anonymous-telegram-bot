
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

users = {}
waiting_male = []
waiting_female = []
chats = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users[update.effective_user.id] = {"gender": None}
    reply_markup = ReplyKeyboardMarkup([["/gender male"], ["/gender female"]], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Welcome to Anonymous Chat!
Please select your gender:", reply_markup=reply_markup)

async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if len(context.args) != 1 or context.args[0] not in ["male", "female"]:
        await update.message.reply_text("Usage: /gender male or /gender female")
        return

    gender = context.args[0]
    users[user_id]["gender"] = gender
    await update.message.reply_text(f"Gender set to {gender}. Use /find to connect.")

async def find(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_gender = users.get(user_id, {}).get("gender")

    if user_gender not in ["male", "female"]:
        await update.message.reply_text("Please set your gender first using /gender male or /gender female.")
        return

    opposite_list = waiting_female if user_gender == "male" else waiting_male

    if opposite_list:
        partner_id = opposite_list.pop(0)
        chats[user_id] = partner_id
        chats[partner_id] = user_id
        await context.bot.send_message(chat_id=partner_id, text="You're now connected to a stranger. Say hi!")
        await update.message.reply_text("You're now connected to a stranger. Say hi!")
    else:
        wait_list = waiting_male if user_gender == "male" else waiting_female
        wait_list.append(user_id)
        await update.message.reply_text("Waiting for a partner...")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    partner_id = chats.pop(user_id, None)
    if partner_id:
        chats.pop(partner_id, None)
        await context.bot.send_message(chat_id=partner_id, text="The stranger has left the chat.")
        await update.message.reply_text("You left the chat.")
    else:
        await update.message.reply_text("You're not in a chat.")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    partner_id = chats.get(user_id)
    if partner_id:
        await context.bot.send_message(chat_id=partner_id, text=update.message.text)

def main():
    app = ApplicationBuilder().token("YOUR_BOT_TOKEN_HERE").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gender", gender))
    app.add_handler(CommandHandler("find", find))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    app.run_polling()

if __name__ == "__main__":
    main()
