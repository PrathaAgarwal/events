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
