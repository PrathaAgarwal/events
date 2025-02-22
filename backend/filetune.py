import os
import requests
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("HUGGINGFACE_API_KEY")

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def get_event_recommendation(user_preferences):
    """
    Fetches event recommendations based on user preferences using Hugging Face's Mistral model.
    """
    prompt = f"Recommend 3 upcoming events in {user_preferences['city']} for someone interested in {user_preferences['category']}."
    
    payload = {"inputs": prompt}
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        return response.json()[0]["generated_text"]
    else:
        return f"Error: {response.text}"

# Example usage
if __name__ == "__main__":
    user_preferences = {"city": "Sydney", "category": "live music"}
    recommendation = get_event_recommendation(user_preferences)
    print(recommendation)
