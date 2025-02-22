import requests
from bs4 import BeautifulSoup
import psycopg2

con = psycopg2.connect(
    dbname="all_events",
    user="postgres",
    password="root",
    host="localhost",
    port="5432"
)
cursor=con.cursor()
url = 'https://whatson.cityofsydney.nsw.gov.au/'
response= requests.get(url)
if response.status_code== 200:
    soup= BeautifulSoup(response.text, "html.parser")
    events = soup.find_all('div', class_='slider-tile')
    for event in events:
        print("yes")
        title = event.find('h3').text.strip()
        print(title)
        date = event.find('footer', class_='event_tile-footer').text.strip()
        location = event.find('span', class_='jsx-5de59786dc412860').text.strip()
        link = event.find('a', class_='event_tile-link')['href']
        cursor.execute("INSERT INTO events (title, date, location, link) VALUES (%s, %s, %s, %s) ON CONFLICT (link) DO NOTHING", (title, date, location, link))
        print(f'Title: {title}')
        print(f'Date: {date}')
        print(f'Location: {location}')
        print(f'Link: {link}')
        print('---')
        events.append({"title": title, "date": date, "location": location, "price": price, "link": link})
       
else:
    print("error")

con.commit()
cursor.close()

con.close()
dataset = []

for event in events:
    query = f"Find me {event['title']} in {event['location']} under ${event['price']}"
    response = f"Check out the {event['title']} on {event['date']}, tickets are ${event['price']}."
    dataset.append({"query": query, "response": response})

# Save the dataset to a JSON file
with open("events_dataset.json", "w") as f:
    json.dump(dataset, f, indent=2)

print("events_dataset.json created successfully!")
