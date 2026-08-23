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

messages = client.messages.list(limit=20)

for msg in messages:

    if msg.from_ == "whatsapp:+17372508034":

        print("=" * 60)
        print("SID:", msg.sid)
        print("From:", msg.from_)
        print("To:", msg.to)
        print("Direction:", msg.direction)
        print("Status:", msg.status)
        print("Body:", msg.body)
        

    # Try to get ContentSid
    print("Content SID:", getattr(msg, "content_sid", None))

    # Print all properties returned by Twilio
    if hasattr(msg, "_properties"):
        print("Properties:")
        print(msg._properties)