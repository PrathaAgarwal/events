import os
import logging
import psycopg2
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ConversationHandler, ContextTypes
)

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Database connection parameters
DB_PARAMS = {
    "dbname": "all_events",
    "user": "postgres",
    "password": "root",
    "host": "localhost",
    "port": "5432"
}

# Hugging Face Inference API details
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"  
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

# Logging setup
logging.basicConfig(level=logging.INFO)

# Conversation states
EVENT_TYPE, BUDGET, LOCATION = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks for event type."""
    await update.message.reply_text("Welcome! What type of events are you interested in? (e.g., Music, Tech, Sports)")
    return EVENT_TYPE

async def event_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Saves event type and asks for budget."""
    context.user_data['event_type'] = update.message.text
    await update.message.reply_text("Got it! What is your budget range? (e.g., Free, $10-$50, $50-$100)")
    return BUDGET

async def budget(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Saves budget and asks for location."""
    context.user_data['budget'] = update.message.text
    await update.message.reply_text("Where are you located? (e.g., Sydney, Melbourne, etc.)")
    return LOCATION

async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Saves location, stores in DB, and fetches event recommendations."""
    context.user_data['location'] = update.message.text
    user_data = context.user_data
    user_id = update.message.chat_id

    # Save preferences in DB
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO user_preferences (id, event_type, budget, location) VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO UPDATE SET event_type = EXCLUDED.event_type, budget = EXCLUDED.budget, location = EXCLUDED.location",
                    (user_id, user_data['event_type'], user_data['budget'], user_data['location'])
                )
    except Exception as e:
        logging.error(f"Database error: {e}")
        await update.message.reply_text("Error saving preferences! Try again later.")
        return ConversationHandler.END

    # Query the LLM
    query = f"Find me {user_data['event_type']} events in {user_data['location']} under {user_data['budget']} budget."
    response = requests.post(HF_API_URL, headers=HEADERS, json={"inputs": query})

    if response.status_code == 200:
        recommendation = response.json()[0]['generated_text']
    else:
        recommendation = "I couldn't fetch event recommendations right now. Try again later."

    await update.message.reply_text(f"🎟️ **Here are some events for you:**\n{recommendation}")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the conversation."""
    await update.message.reply_text("Okay, no worries! You can start again anytime by typing /start.")
    return ConversationHandler.END

def main():
    """Start the bot."""
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            EVENT_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, event_type)],
            BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, budget)],
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, location)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == '__main__':
    main()
