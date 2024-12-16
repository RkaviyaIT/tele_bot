from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telethon import TelegramClient
from nltk.sentiment.vader import SentimentIntensityAnalyzer


TOKEN = '7718098452:AAFNngD67_ymjhO-GzRJkSnyOZ0P4N_OUPA'

# Set up the Telegram Client (using Telethon)
api_id = '29680616'
api_hash = '673acd28ac10e32b05ef7facbdd4d502'
client = TelegramClient('session_name', api_id, api_hash)

# Set up sentiment analyzer and keywords for scam detection
analyzer = SentimentIntensityAnalyzer()
scam_keywords = ["guaranteed returns", "crypto", "forex", "investment", "risk-free", "profits", "scam"]

async def fetch_channel_messages(channel_name):
    async with client:
        messages = []
        async for message in client.iter_messages(channel_name):
            messages.append({
                'sender': message.sender_id,
                'text': message.text,
                'date': message.date
            })
        return messages

def contains_scam_keywords(text: str) -> bool:
    text = text.lower()
    return any(keyword in text for keyword in scam_keywords)

def analyze_investment_scam(text: str):
    sentiment_score = analyzer.polarity_scores(text)
    scam_detected = contains_scam_keywords(text)
    return scam_detected, sentiment_score

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    scam_detected, sentiment_score = analyze_investment_scam(text)
    
    if scam_detected:
        await update.message.reply_text("This looks like a scam!")
    else:
        await update.message.reply_text("This seems safe.")
    
    print(f"Sentiment: {sentiment_score}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! I am your Scam Detection Bot.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I help detect scams and analyze channels. Type a message to get started.")

# Command to fetch messages from a channel
async def analyze_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) > 0:
        channel_name = context.args[0]  # Channel username passed as argument
        messages = await fetch_channel_messages(channel_name)
        
        for message in messages:
            scam_detected, sentiment_score = analyze_investment_scam(message['text'])
            if scam_detected:
                await update.message.reply_text(f"Scam detected: {message['text']}")
            else:
                await update.message.reply_text(f"Normal message: {message['text']}")
    else:
        await update.message.reply_text("Please provide a channel username after the command.(Eg:/analyze_channel channel_name)")

# Set up the Application and Handlers
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler('start', start_command))
app.add_handler(CommandHandler('help', help_command))
app.add_handler(CommandHandler('analyze_channel', analyze_channel))  # Command for channel analysis
app.add_handler(MessageHandler(filters.TEXT, handle_message))

print("Bot is running...")
app.run_polling(poll_interval=3)
