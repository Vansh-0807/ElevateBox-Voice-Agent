import os
import json
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
    content_sid="HXb5b62575e6e4ff6129ad7c8efe1f983e",
    content_variables=json.dumps({
        "1": "23 August 2026",
        "2": "3:30pm"
    })
)

print("Message SID:", message.sid)
print("Status:", message.status)