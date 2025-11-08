import os
import json
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field
from enum import Enum
from openai import OpenAI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
# conda install -c conda-forge fastapi uvicorn python-dotenv
# pip install openai

# --------------------------- config ---------------------------
load_dotenv()
app = FastAPI(title="Smart Meal Swiper Backend")
client = OpenAI(
    api_key = "sk-FAyzaUaK8JlUzvrmIU2XlA",
    base_url = "https://fj7qg3jbr3.execute-api.eu-west-1.amazonaws.com/v1/chat/completions"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# init global variables
CURRENT_USER_PROFILE: Dict[str, Any] = {}

# onboarding models
class Goal(str, Enum):
    lose_weight = "lose weight"
    gain_muscle = "gain muscle"
    maintain = "maintain"

class ActivityLevel(str, Enum):
    sedentary = "sedentary"
    light = "light"
    moderate = "moderate"
    active = "active"

class OnboardingData(BaseModel):
    name: str
    age: int
    height: int
    weight: int
    goal: Goal
    activity_level: ActivityLevel

# calculate macros
def calculate_targets(data: OnboardingData) -> Dict[str, int]:
    bmr = (10 * data.weight) + (6.25 * data.height) - (5 * data.age) + 5
    activity_multipliers = {
        "sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725
    }
    tdee = bmr * activity_multipliers[data.activity_level]
    
    if data.goal == "lose_weight": target_calories = tdee - 500
    elif data.goal == "gain_muscle": target_calories = tdee + 300
    else: target_calories = tdee
        
    return {
        "target_calories": int(target_calories),
        "target_protein": int((target_calories * 0.30) / 4),
        "target_carbs": int((target_calories * 0.40) / 4),
        "target_fat": int((target_calories * 0.30) / 9)
    }


# --------------------------- actual endpoints -----------------

# initialize user profile
@app.post("/onboarding")
async def handle_onboarding(data: OnboardingData):
    global CURRENT_USER_PROFILE
    
    targets = calculate_targets(data)
    CURRENT_USER_PROFILE = data.model_dump()
    CURRENT_USER_PROFILE.update(targets)
    
    print(f"New profile saved: {json.dumps(CURRENT_USER_PROFILE, indent=2)}")
    return {"message": f"Welcome, {data.name}!", "targets": targets}

@app.post("/get-meal-batch")
async def get_meal_batch():
    if not CURRENT_USER_PROFILE:
        return {"error": "User profile not set. Please complete onboarding first."}
    
    return("fitting json")

# main
if __name__ == "__main__":
    print("Running on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)