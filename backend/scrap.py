import os
import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging

# Set up logging for better control over messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from the .env file
load_dotenv()

# Fetch database URL and service account key from environment variables
database_url = os.environ.get("DATABASE_URL")
service_account_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Check if environment variables are present
if not database_url:
    logger.error("DATABASE_URL not found in .env file")
    exit(1)

if not service_account_path:
    logger.error("GOOGLE_APPLICATION_CREDENTIALS not found in .env file")
    exit(1)

# Initialize Firebase
try:
    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred, {"databaseURL": database_url})
    ref = db.reference("scrapedData")
    logger.info("Firebase initialized successfully.")
except Exception as e:
    logger.error(f"Error initializing Firebase: {e}")
    exit(1)
logger.info("Fetching website...")
# Scrape event data from the specified URL
url = 'https://allevents.in/'
logger.info("Fetched")
# Request with user-agent header to avoid scraping issues
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
response = requests.get(url, headers=headers)
# Check for 404 or other errors
if response.status_code == 404:
    logger.error(f"Page not found: {url}")
    exit(1)
elif response.status_code != 200:
    logger.error(f"Failed to fetch the page. Status code: {response.status_code}")
    exit(1)

# If the page was found, proceed with parsing
soup = BeautifulSoup(response.text, "html.parser")
events = soup.find_all('li', class_='event-card')
for event in events:
   
    try:
        title_element = event.find('div', class_='title')
        logger.info(title_element)
        logger.info("---------------------------------------------------------------------------------")
        image_element = event.find('div', class_='banner-cont')
        logger.info(image_element)
        logger.info("---------------------------------------------------------------------------------")
        date_element = event.find('div', class_='date')
        logger.info(date_element)
        logger.info("---------------------------------------------------------------------------------")
        price_element = event.find('span', class_='price')
        logger.info(price_element)
        logger.info("---------------------------------------------------------------------------------")
        if title_element and date_element and image_element and price_element:
            title = title_element.text.strip()
            date = date_element.text.strip()
            location = price_element.text.strip()
            link = image_element['data-src']
            logger.info(title, date,location,link)
            data = {
                'title': title,
                'date': date,
                'location': location,
                'link': link,
                'timestamp': datetime.now().isoformat()
            }
            try:
                logger.info("---------------------------------------------------------------------------------")
                ref.push(data)
                logger.info("Data written to Firebase successfully!")
            except firebase_admin.exceptions.FirebaseError as firebase_error:
                logger.error(f"Error writing data to Firebase: {firebase_error}")
                logger.info("---------------------------------------------------------------------------------")

            logger.info(f"Title: {title}\nDate: {date}\nLocation: {location}\nLink: {link}\n---")
        else:
            logger.warning("Warning: Missing element in event data.")
    except Exception as scraping_error:
        logger.error(f"Error processing event: {scraping_error}")
