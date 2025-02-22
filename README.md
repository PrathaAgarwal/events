Overview
The Event Recommendation System is an MVP designed to help users discover relevant events in Sydney based on their preferences. It uses a fine-tuned Mistral-7B model with LangChain for event matching and sends notifications via WhatsApp (Twilio) and Telegram Bot API.
Features
•	Collects user preferences (event type, budget, location) through a chatbot.
•	Matches preferences with local events using a fine-tuned LLM.
•	Notifies users about matching events via WhatsApp and Telegram.
Prerequisites
•	Python 3.8+
•	Node.js 14+
•	PostgreSQL (or preferred database)
•	Twilio account (for WhatsApp notifications)
•	Telegram Bot API token
•	LangChain for backend processing
Setup
1. Clone the Repository
git clone https://github.com/your-username/event-recommendation-system.git
cd event-recommendation-system
2. Backend Setup
Install Python dependencies
cd backend
pip install -r requirements.txt
Configure Environment Variables
Create a .env file and add the following:
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TELEGRAM_BOT_API_KEY=your_telegram_bot_api_key
DATABASE_URL=your_database_url
3. Frontend Setup
cd frontend
npm install
4. Run the Application
Backend
cd backend
python app.py
Frontend
cd frontend
npm start
Testing
Interact with the chatbot to input preferences, receive event recommendations, and get notified via WhatsApp or Telegram.
