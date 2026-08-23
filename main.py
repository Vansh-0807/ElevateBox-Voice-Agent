from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Any

app = FastAPI()

import os
from dotenv import load_dotenv
load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
api_key = os.getenv("TWILIO_API_KEY")
api_secret = os.getenv("TWILIO_API_SECRET")
whatsapp_from = os.getenv("TWILIO_WHATSAPP_FROM")
content_id = os.getenv("TWILIO_CONTENT_SID")

from twilio.rest import Client
client = Client(
    api_key,
    api_secret,
    account_sid
)

class VapiWebhookRequest(BaseModel):
    message: dict[str, Any]

class VapiToolRequest(BaseModel):
    message: str
    lead_type: str

class CallEndedRequest(BaseModel):
    call_id: str
    status: str
    transcript: str

def send_whatsapp(phone:str, message:str):
    print("Sending whatsapp message...")
    print("Phone: ", phone)
    print("Message: ", message)

    whatsapp_message = client.messages.create(
        from_="whatsapp:+17372508034",
        to=f"whatsapp:{phone}",
        content_sid = content_id
    )
    print("Twillo Message SID:", whatsapp_message.sid)
    print("Twilio Status: ", whatsapp_message.status)
    return "Whatsapp message sent successfully."

@app.get("/")
async def root():
    return {
        'message': "ElevateBox Voice Agent backend is running"
    }

@app.post("/webhook/vapi")
async def vapi_webhook(request:VapiWebhookRequest):
    message=request.message
    print("Received Vapi webhook:")
    print(message)

    message_type = message.get("type")
    print("Message type = ", message_type)

    if message_type != "tool-calls":
        return{
            "results" : []
        }

    tool_calls = message.get("toolCallList", [])

    results = []

    for tool_call in tool_calls:
        tool_name = tool_call.get("name")
        tool_call_id = tool_call.get("id")
        parameters = tool_call.get("parameters", {})

        if tool_name == "send_whatsapp_midcall":

            phone = parameters.get("phone")
            whatsapp_message = parameters.get("message")

            result = send_whatsapp(
                phone, 
                whatsapp_message
            )
        else:
            result = f"Unknown tool: {tool_name}"
        results.append({
            "toolCallId": tool_call_id,
            "result" : result
        })
    return {
            "results" : results
        }

@app.post("/webhook/vapi-tools")
async def vapi_tools(request: VapiToolRequest):
    message = request.message
    lead_type = request.lead_type

    return{
        "success" : True,
        "message" : message,
        "lead_type" : lead_type
    }

@app.post("/webhook/call_ended")
async def call_ended(request: CallEndedRequest):
    return{
        "success" : True,
        "message" : "Call - ended webhook received"
    }

