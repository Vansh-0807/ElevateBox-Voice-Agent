from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any
app = FastAPI()

import os
from dotenv import load_dotenv
load_dotenv()

class CallbackRequest(BaseModel):
    phone: str
    callback_datetime: str
    timezone: str 

class LeadQualificationRequest(BaseModel):
    budget:str
    business_type:str
    product_count:str
    timeline:str
    features:str

@app.get("/")
async def root():
    return {
        'message': "ElevateBox Voice Agent backend is running"
    }

@app.post("/webhook/qualify-lead")
async def qualify_lead(request:LeadQualificationRequest):
    score = 0
    signals = []

    # budget signal
    budget = request.budget.lower()
    if any(word in budget for word in[
        "ready",
        "approved",
        "allocated",
        "₹",
        "rs",
        "inr",
        "lakh",
        "thousand"
    ]):
        score+=2
        signals.append("clear budget")

    elif any(word in budget for word in[
        "maybe",
        "around",
        "roughly",
        "not sure",
        "need to decide"
    ]):
        score+=1
        signals.append("uncertain budget")

    elif any(word in budget for word in[
        "unknown",
        "not decided",
        "no budget",
        "none",
        "don't know"
    ]):
        signals.append("no confirmed budget")

    # timeline signal
    timeline = request.timeline.lower()
    if any(word in timeline for word in [
        "today",
        "this week", 
        "next week",
        "within a week",
        "within two weeks",
        "this month", 
        "next month",
        "soon",
        "immediately"
    ]):
        score+=3
        signals.append("near-term launch")

    elif any(word in timeline for word in[
        "few months",
        "3 months",
        "4 months",
        "5 months",
        "6 months"
    ]):
        score+=2
        signals.append("medium-term launch")

    elif any(word in timeline for word in [
        "later",
        "next year",
        "sometime next year",
        "not decided",
        "no timeline"
    ]):
        signals.append("distant or uncertain timeline")

    else:
        score+=1

    # business requirement
    business_type = request.business_type.lower()
    if business_type not in [
        "unknown",
        "not decided",
        "none",
        "just exploring",
        "just researching"
    ]:
        score+=1
        signals.append("clear business requirement")

    # product count signal
    product_count = request.product_count.lower()
    if product_count not in [
        "unknown",
        "not decided",
        "none"
    ]:
        score+=1
        signals.append("defined product catalogue")

    # features/requirementes
    features = request.features.lower()
    if features not in [
        "unknown",
        "not decided",
        "none",
        "just exploring"
    ]:
        score+=2
        signals.append("specific feature requirements")

    # string buying signals
    combined_text = " ".join([
        budget,
        business_type,
        product_count,
        timeline,
        features
    ])

    if any(phrase in combined_text for phrase in [
        "want to start",
        "ready to start",
        "start immediately",
        "start soon",
        "move forward",
        "move ahead",
        "send proposal",
        "send quote",
        "what is the price",
        "how much",
        "next steps"
    ]):
        score+=3
        signals.append("strong buying signal")

    # final lead classfication
    if score>=5:
        lead_type =  "HOT"

    elif score >= 2:
        lead_type =  "WARM"

    else:
        lead_type =  "COLD"

    return{
        "success" : True,
        "lead_type" : lead_type,
        "score" : score,
        "signals" : signals,
        "budget" : request.budget,
        "business_type" : request.business_type,
        "product_count" : request.product_count,
        "timeline" : request.timeline,
        "features" : request.features
    }
            
@app.post("/webhook/call_ended")
async def call_ended(data: dict[str, Any]):
    print("Outpero call-ended webhook received ")

    print("Webhook data:")
    print(data)

    phone = data.get("phone")
    summary = data.get("summary")
    outcome = data.get("outcome")
    transcript = data.get("transcript") 
    captured = data.get("captured")

    print("Phone : ", phone)
    print("Outcome :", outcome)
    print("Summary : ", summary)
    print("Captured: ", captured)
    print("Transcript: ", transcript)


    return {
        "success" : True,
        "message" : "Call-ended webhook received"
    }

