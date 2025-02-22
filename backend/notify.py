import psycopg2
from telegram import Bot
from datetime import datetime
import logging

import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

con = psycopg2.connect(DATABASE_URL)


# Set up Telegram bot
bot = Bot(token="YOUR_TELEGRAM_BOT_TOKEN")

# Function to send notifications
def send_notifications():
    try:
        with psycopg2.connect(**DB_PARAMS) as con:
            with con.cursor() as cursor:
                # Fetch all users and their preferences
                cursor.execute("SELECT user_id, event_type, budget, location FROM user_preferences")
                users = cursor.fetchall()

                # Fetch upcoming events
                cursor.execute("SELECT title, date, location, link FROM events WHERE date >= %s", (datetime.now(),))
                events = cursor.fetchall()

                for user in users:
                    user_id, event_type, budget, location = user

                    # Check if any event matches user preferences
                    for event in events:
                        title, date, location_event, link = event
                        if event_type.lower() in title.lower() and location.lower() in location_event.lower():
                            # Send a notification to the user
                            message = f"New event: {title}\nDate: {date}\nLocation: {location_event}\nCheck it out: {link}"
                            bot.send_message(chat_id=user_id, text=message)
                            logging.info(f"Sent notification to {user_id}: {message}")
    except Exception as e:
        logging.error(f"Error sending notifications: {e}")
