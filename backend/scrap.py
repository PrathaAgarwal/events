import os
import requests
from bs4 import BeautifulSoup
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

con = psycopg2.connect(DATABASE_URL)
cursor = con.cursor()

url = 'https://whatson.cityofsydney.nsw.gov.au/'
response = requests.get(url)
from datetime import datetime, timedelta

def parse_event_date(event_date_str):
    if not event_date_str or event_date_str.strip() == "":
        print(f"⚠️ Warning: Empty date value received.")
        return "1970-01-01"  # Fallback to prevent NULL errors

    event_date_str = event_date_str.lower().strip()

    # Handle "Today" and "Tomorrow"
    if "today" in event_date_str:
        return datetime.today().strftime("%Y-%m-%d")

    if "tomorrow" in event_date_str:
        return (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")

    # Handle dates in format like "26 Feb 2025" or "5 Apr 2025"
    try:
        return datetime.strptime(event_date_str, "%d %b %Y").strftime("%Y-%m-%d")
    except ValueError:
        pass

    # Handle cases like "Today 10am to 5pm" (extracting only 'Today')
    if event_date_str.startswith("today"):
        return datetime.today().strftime("%Y-%m-%d")
    
    if event_date_str.startswith("tomorrow"):
        return (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")

    print(f"⚠️ Warning: Could not parse date '{event_date_str}', using fallback.")
    return "1970-01-01"  # Default fallback (so it never returns NULL)


if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    events = soup.find_all('div', class_='slider-tile')

    for event in events:
        title = event.find('h3').text.strip()
        date = event.find('footer', class_='event_tile-footer').text.strip()
        location = event.find('span', class_='jsx-5de59786dc412860').text.strip()
        link = event.find('a', class_='event_tile-link')['href']

        cursor.execute(
            "INSERT INTO events (title, date, location, link) VALUES (%s, %s, %s, %s) ON CONFLICT (link) DO NOTHING",
            (title, parse_event_date(date), location, link)
        )

        print(f"Title: {title}\nDate: {date}\nLocation: {location}\nLink: {link}\n---")

else:
    print("Error fetching events")

con.commit()
cursor.close()
con.close()
