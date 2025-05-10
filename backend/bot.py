import os
import logging
import firebase_admin
from firebase_admin import credentials, db
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ConversationHandler, ContextTypes
)

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
service_account_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")  # Firebase credentials
DATABASE_URL = os.getenv("FIREBASE_DB_URL")

# Initialize Firebase
cred = credentials.Certificate(service_account_path)
firebase_admin.initialize_app(cred, {"databaseURL": DATABASE_URL})

# Load FLAN-T5 Model (Small)
model_name = "google/flan-t5-small"
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

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
    """Saves location, stores in Firebase, and fetches event recommendations."""
    context.user_data['location'] = update.message.text
    user_data = context.user_data
    user_id = str(update.message.chat_id)  # Convert to string for Firebase keys

    # Save preferences in Firebase
    try:
        ref = db.reference(f"user_preferences/{user_id}")
        ref.set({
            "event_type": user_data['event_type'],
            "budget": user_data['budget'],
            "location": user_data['location']
        })
    except Exception as e:
        logging.error(f"Firebase error: {e}")
        await update.message.reply_text("Error saving preferences! Try again later.")
        return ConversationHandler.END

    # Query FLAN-T5 Model
    query = f"Find me {user_data['event_type']} events in {user_data['location']} under {user_data['budget']} budget."
    
    inputs = tokenizer(query, return_tensors="pt")
    with torch.no_grad():
        output = model.generate(**inputs, max_length=50)
    
    recommendation = tokenizer.decode(output[0], skip_special_tokens=True)

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
