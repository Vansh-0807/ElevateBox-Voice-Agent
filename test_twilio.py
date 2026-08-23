import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
api_key = os.getenv("TWILIO_API_KEY")
api_secret = os.getenv("TWILIO_API_SECRET")

client = Client(
    api_key,
    api_secret,
    account_sid
)

print("Twilio client created successfully.")
print("Account SID:", account_sid)