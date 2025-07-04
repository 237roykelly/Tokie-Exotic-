from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from googletrans import Translator

BOT_TOKEN = "8025046328:AAHircViAz-OWHEVp3DNX_06-WzfVSxtDa8"
translator = Translator()

SELECT_COUNTRY, SELECT_CATEGORY, SELECT_QUANTITY, ASK_ADDRESS, PAYMENT_PROOF = range(5)
user_data = {}

country_currency = {
    '🇩🇪': 'EUR', '🇮🇹': 'EUR', '🇳🇱': 'EUR', '🇷🇴': 'RON',
    '🇹🇷': 'TRY', '🇺🇸': 'USD', '🇫🇷': 'EUR'
}

category_prices = {
    '💳Cloned Cards💳': ['€300', '€500', '€1000', '€5000'],
    '🪪ID Cards🪪': ['€1500 (Deposit €1000, rest on delivery)'],
    '🪪Drivers License🪪': ['$1000 (Deposit €700, rest on delivery)'],
    '💶Bills💶': ['€300', '€500', '€1000', '€5000']
}

bitcoin_address = "bitcoin:1EqfhYsqgcwPb8TfG4T2tm7XeRiMutsdPj"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton(c) for c in country_currency.keys()]]
    await update.message.reply_text("🌍 Which country are you from?", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return SELECT_COUNTRY

async def select_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_data[chat_id] = {'country': update.message.text}
    keyboard = [[KeyboardButton("💳Cloned Cards💳"), KeyboardButton("🪪ID Cards🪪")], [KeyboardButton("🪪Drivers License🪪"), KeyboardButton("💶Bills💶")]]
    await update.message.reply_text("🛍️ What would you like to shop?", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return SELECT_CATEGORY

async def select_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_data[chat_id]['category'] = update.message.text
    await update.message.reply_text("🔢 How many would you like to buy? (1, 2, 3...)")
    return SELECT_QUANTITY

async def select_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_data[chat_id]['quantity'] = update.message.text
    category = user_data[chat_id]['category']
    country = user_data[chat_id]['country']
    prices = category_prices.get(category, [])

    await update.message.reply_text(f"💰 Prices for {category}:\n" + "\n".join(prices))
    await update.message.reply_text(f"🪙 Pay via Bitcoin to:\n`{bitcoin_address}`\nThen send us a screenshot.")
    await update.message.reply_text("📦 Please enter your shipping address:")
    return ASK_ADDRESS

async def ask_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_data[chat_id]['address'] = update.message.text
    await update.message.reply_text("📸 Upload payment screenshot:")
    return PAYMENT_PROOF

async def payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        await update.message.reply_text("✅ Payment received! Order processing.\nNeed help? Contact @Leopold_MMM.")
    else:
        await update.message.reply_text("⚠️ Please send the payment screenshot as an image.")
        return PAYMENT_PROOF
    return ConversationHandler.END

app = ApplicationBuilder().token(BOT_TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        SELECT_COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_country)],
        SELECT_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_category)],
        SELECT_QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_quantity)],
        ASK_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_address)],
        PAYMENT_PROOF: [MessageHandler(filters.PHOTO, payment_proof)],
    },
    fallbacks=[],
)

app.add_handler(conv_handler)

if __name__ == '__main__':
    app.run_polling()