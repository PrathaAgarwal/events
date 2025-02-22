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

from datetime import datetime, timedelta

def parse_event_date(event_date_str):
    if not event_date_str or event_date_str.strip() == "":
        print(f"⚠️ Warning: Empty date value received.")
        return "1970-01-01"  # Fallback to prevent NULL errors

    event_date_str = event_date_str.lower().strip()
    
    # Handle "Today" and "Tomorrow"
    if "Today" in event_date_str:
        return datetime.today().strftime("%Y-%m-%d")

    elif "Tomorrow" in event_date_str:
        return (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")

    # Handle dates in format like "March 5, 2025"
    try:
        return datetime.strptime(event_date_str, "%B %d, %Y").strftime("%Y-%m-%d")
    except ValueError:
        pass

    print(f"⚠️ Warning: Could not parse date '{event_date_str}', using fallback.")
    return "1970-01-01"  # Default fallback (so it never returns NULL)
# If format is unknown

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
