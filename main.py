import os
import json
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from enum import Enum
from openai import OpenAI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
# install dependencies:
# conda install -c conda-forge fastapi uvicorn python-dotenv
# pip install openai


# --- 1. SETUP & CONFIG ---

# This loads your OPENAI_API_KEY from a file named .env
load_dotenv()

app = FastAPI(title="Smart Grocery Agent Backend")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# **CRITICAL FOR MOBILE APP**
# This middleware allows your React Native / Flutter app to make
# requests to this server from a different "origin" (i.e., your phone).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, etc.)
    allow_headers=["*"],  # Allows all headers
)

# --- 2. HACKATHON "DATABASE" ---

# This global variable will store our *one* demo user's profile.
# This is how we avoid needing a real login!
CURRENT_USER_PROFILE: Dict[str, Any] = {}

# Load the mock grocery store data
try:
    with open("mock_data.json") as f:
        MOCK_DATA = json.load(f)
    print("mock_data.json loaded successfully.")
except FileNotFoundError:
    MOCK_DATA = []
    print("WARNING: 'mock_data.json' not found. The agent will have no groceries to recommend.")


# --- 3. DATA VALIDATION MODELS (PYDANTIC) ---
# These models ensure the data from the frontend is clean.

class Goal(str, Enum):
    lose_weight = "lose_weight"
    gain_muscle = "gain_muscle"
    maintain = "maintain"

class ActivityLevel(str, Enum):
    sedentary = "sedentary"
    light = "light"
    moderate = "moderate"
    active = "active"

# This defines the data for the /onboarding endpoint
class OnboardingData(BaseModel):
    name: str
    age: int
    height: int  # in cm
    weight: int  # in kg
    goal: Goal
    activity_level: ActivityLevel

# This defines the data for the /chat endpoint
class ChatRequest(BaseModel):
    message: str


# --- 4. NUTRITIONAL ENGINE ---

def calculate_targets(data: OnboardingData) -> Dict[str, int]:
    """Calculates TDEE and Macros based on user profile."""
    
    # Using Mifflin-St Jeor equation (assuming male for hackathon simplicity)
    bmr = (10 * data.weight) + (6.25 * data.height) - (5 * data.age) + 5
    
    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725
    }
    tdee = bmr * activity_multipliers[data.activity_level]
    
    # Adjust calories based on goal
    if data.goal == "lose_weight":
        target_calories = tdee - 500
    elif data.goal == "gain_muscle":
        target_calories = tdee + 300
    else:
        target_calories = tdee
        
    # 40c/30p/30f split (as grams)
    target_protein = (target_calories * 0.30) / 4
    target_carbs = (target_calories * 0.40) / 4
    target_fat = (target_calories * 0.30) / 9
    
    return {
        "target_calories": int(target_calories),
        "target_protein": int(target_protein),
        "target_carbs": int(target_carbs),
        "target_fat": int(target_fat)
    }


# --- 5. API ENDPOINTS ---

@app.post("/onboarding")
async def handle_onboarding(data: OnboardingData):
    """
    "Registers" and "Logs In" the user by calculating and saving
    their profile to our global variable. This is where we
    also "fake" the learned trends.
    """
    global CURRENT_USER_PROFILE
    
    print(f"Received onboarding data for: {data.name}")
    
    # 1. Calculate macros
    targets = calculate_targets(data)
    
    # 2. Save user's submitted data to our "database"
    CURRENT_USER_PROFILE = data.model_dump()
    
    # 3. Save calculated targets to our "database"
    CURRENT_USER_PROFILE.update(targets)
    
    # 4. **THE HACKATHON MAGIC**
    # Hardcode the "learned trends" for this user.
    CURRENT_USER_PROFILE["preferences"] = [
        "Prefers almond milk over dairy milk.",
        "Loves avocados.",
        "Prefers chicken and salmon for protein."
    ]
    CURRENT_USER_PROFILE["pantry_items"] = [
        {
            "item_name": "Extra Virgin Olive Oil",
            "purchase_frequency_weeks": 2,
            "last_purchased_days_ago": 13  # Almost 2 weeks!
        },
        {
            "item_name": "Dozen Eggs",
            "purchase_frequency_weeks": 1,
            "last_purchased_days_ago": 2   # Just bought
        }
    ]
    
    print(f"New profile saved: {json.dumps(CURRENT_USER_PROFILE, indent=2)}")
    
    # 5. Return success + targets to frontend
    return {
        "message": f"Welcome, {data.name}! Your profile is set up.",
        "targets": targets
    }


@app.post("/chat")
async def handle_chat(request: ChatRequest):
    """
    Handles chat messages, using the "faked" profile and trends
    to give a smart, personalized response.
    """
    global CURRENT_USER_PROFILE
    
    # Check if user is "logged in"
    if not CURRENT_USER_PROFILE:
        return {
            "response": "Error: User profile not set. Please complete onboarding first."
        }

    user_message = request.message
    
    # 1. Format all your "database" data for the prompt
    available_groceries = json.dumps(MOCK_DATA, indent=2)
    user_preferences = json.dumps(CURRENT_USER_PROFILE.get("preferences", []), indent=2)
    user_pantry = json.dumps(CURRENT_USER_PROFILE.get("pantry_items", []), indent=2)
    
    # 2. Engineer the Advanced Prompt
    system_prompt = f"""
    You are an expert grocery shopping assistant. The user's goal is **{CURRENT_USER_PROFILE.get('goal')}**.
    Their name is {CURRENT_USER_PROFILE.get('name')}.

    Here is the user's profile and known habits:
    ---
    USER PREFERENCES (What they like):
    {user_preferences}
    ---
    USER PANTRY (for tracking re-purchases):
    {user_pantry}
    ---
    AVAILABLE GROCERIES (What's in the store):
    {available_groceries}
    ---
    
    YOUR TASKS:
    1.  **Handle Requests:** Answer the user's message: "{user_message}".
    2.  **Use Preferences:** If the user asks for a generic item (like "milk"), check their PREFERENCES and suggest their preferred item (like "almond milk").
    3.  **Check Pantry:** Look at the PANTRY list. If an item's 'last_purchased_days_ago' is close to their 'purchase_frequency' (in days), proactively suggest re-ordering it. (e.g., 13 days ago is close to 2 weeks/14 days).
    4.  **Tag Items:** When you suggest a *specific* grocery item, you MUST tag it with its ID from the grocery list, e.g., [ITEM:4].
    
    Be friendly, proactive, and justify your suggestions based on their goals and preferences.
    """

    # 3. Call the OpenAI API
    try:
        completion = client.chat.completions.create(
            # Using gpt-4o for best reasoning, but gpt-3.5-turbo is faster/cheaper
            model="gpt-4o", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        ai_response = completion.choices[0].message.content
    
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return {"response": "Sorry, I'm having trouble connecting to my brain. Please try again."}

    # 4. Return the final response
    return {
        "response": ai_response
    }

# --- 6. RUN THE APP ---
if __name__ == "__main__":
    print("--- Starting Smart Grocery Agent Backend ---")
    print("Access the API at http://0.0.0.0:8000")
    print("Ensure 'mock_data.json' and '.env' files are in this directory.")
    
    # Run the server. "0.0.0.0" makes it accessible on your local network
    # so your mobile phone can find it (e.g., at http://192.168.1.10:8000)
    uvicorn.run(app, host="0.0.0.0", port=8000)