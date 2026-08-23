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

message = client.messages.create(
    from_="whatsapp:+17372508034",
    to="whatsapp:+916264464754",
    content_sid="HXfe5ab5f00277942d4d4200328b4d403c"
)

print("Message SID:", message.sid)
print("Status:", message.status)