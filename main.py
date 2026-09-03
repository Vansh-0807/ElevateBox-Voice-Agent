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

    phone = data.get("to_number")
    outcome = data.get("outcome")
    summary = data.get("summary")
    transcript = data.get("transcript", []) 
    captured = data.get("captured", {})

    # convert transcript into readable text
    transcript_text = ""

    if isinstance(transcript, list):
        for message in transcript:
            role = message.get("role", "")
            content = message.get("content", "")

            transcript_text += f"{role}: {content}\n"

    follow_up_context = {
        "phone" : phone,
        "outcome" : outcome,
        "summary" : summary,
        "captured" : captured,
        "transcript" : transcript_text.strip()
    }
    print("------FOLLOW-UP CONTEXT------")
    print("Phone : ", follow_up_context["phone"])
    print("Outcome :", follow_up_context["outcome"])
    print("Summary : ", follow_up_context["summary"])
    print("Captured: ", follow_up_context["captured"])
    print("Transcript: ", follow_up_context["transcript"])

    follow_up_message = generate_follow_up_message(
        phone=phone,
        summary=summary,
        outcome=outcome,
        captured=captured
    )

    print("=====Follow Up Message====")
    print(follow_up_message)

    return {
        "success" : True,
        "message" : "Call-ended webhook received",
        "follow_up_context": follow_up_context,
        "follow_up_message" : follow_up_message
    }   

def generate_follow_up_message(
        phone,
        summary,
        outcome,
        captured
):
    products = captured.get("products")
    required_features = captured.get("required_features")
    budget = captured.get("budget")
    timeline = captured.get("timeline")
    interest_level = captured.get("interest_level")
    next_step = captured.get("next_step")

    message = "Hi, thank you for speaking with me today. "

    if summary:
        message += f"Based on our conversation, {summary}"

    if products:
        message += f"Your current budget discussed was {budget}. "

    if required_features:
        message += (
            f"The key e-commerce requirements you mentioned were "
            f"{required_features}."
        )

    if budget:
        message += f"Your current budget discussed was {budget}. "

    if timeline:
        message += f"You mentioned a timeline of {timeline}."

    if interest_level:
        message += (
            f"Based on our conversatiom, your current interest level"
            f"is {interest_level}. "
        )
    if next_step:
        message += f"Our next step is {next_step}." 

    message += (
        "I'm sharing my resume and a brief architecture overview "
        "for your reference. "
    )   

    if phone:
        message += f"You can reach me at {phone}. "

    message += (
        "Please feel free to reach out if you like to discuss"
        "the e-commerce solution further."
    )
    return message