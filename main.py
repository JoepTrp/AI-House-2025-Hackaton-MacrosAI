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

# --- 1. SETUP & CONFIG ---
load_dotenv()
app = FastAPI(title="Smart Meal Swiper Backend")
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://fj7qg3jbr3.execute-api.eu-west-1.amazonaws.com/v1/chat/completions"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# This is our hardcoded list of items users probably have.
# We use lowercase for easy matching.
COMMON_PANTRY_STAPLES = {
    "salt", "pepper", "black pepper", "olive oil", "extra virgin olive oil",
    "vegetable oil", "canola oil", "sugar", "flour", "all-purpose flour",
    "butter", "garlic powder", "onion powder", "paprika", "chili powder",
    "soy sauce", "vinegar", "balsamic vinegar", "apple cider vinegar"
}

# --- 2. HACKATHON "DATABASE" ---

CURRENT_USER_PROFILE: Dict[str, Any] = {}
SHOPPING_LIST: List[Dict[str, Any]] = []

try:
    with open("mock_data.json") as f:
        MOCK_DATA = json.load(f)
    print("mock_data.json loaded successfully.")
except FileNotFoundError:
    MOCK_DATA = []
    print("WARNING: 'mock_data.json' not found.")


# --- 3. DATA VALIDATION MODELS (PYDANTIC) ---

# --- Onboarding Models ---
class Goal(str, Enum):
    lose_weight = "lose_weight"
    gain_muscle = "gain_muscle"
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

# --- Shopping List Models ---
class Ingredient(BaseModel):
    item_name: str
    quantity: str
    
class AddToListRequest(BaseModel):
    ingredients: List[Ingredient] = Field(..., example=[{"item_name": "Organic Chicken Breast", "quantity": "2 lbs"}])


# --- 4. NUTRITIONAL ENGINE (Unchanged) ---

def calculate_targets(data: OnboardingData) -> Dict[str, int]:
    # (Same as before: calculates BMR, TDEE, macros)
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


# --- 5. API ENDPOINTS ---

@app.post("/onboarding")
async def handle_onboarding(data: OnboardingData):
    """
    "Logs in" the user, calculates targets, and fakes their trends.
    """
    global CURRENT_USER_PROFILE, SHOPPING_LIST
    
    # Reset for the demo
    SHOPPING_LIST = []
    
    targets = calculate_targets(data)
    CURRENT_USER_PROFILE = data.model_dump()
    CURRENT_USER_PROFILE.update(targets)
    
    # "Fake" learned trends
    CURRENT_USER_PROFILE["preferences"] = [
        "Prefers almond milk over dairy milk.",
        "Loves avocados.",
        "Prefers chicken and salmon for protein."
    ]
    CURRENT_USER_PROFILE["pantry_items"] = [
        {"item_name": "Extra Virgin Olive Oil", "purchase_frequency_weeks": 2, "last_purchased_days_ago": 13},
        {"item_name": "Dozen Eggs", "purchase_frequency_weeks": 1, "last_purchased_days_ago": 2}
    ]
    
    print(f"New profile saved: {json.dumps(CURRENT_USER_PROFILE, indent=2)}")
    return {"message": f"Welcome, {data.name}!", "targets": targets}

# ---
# ENDPOINT 2: THE MEAL SWIPER (*** MODIFIED ***)
# ---
@app.post("/get-meal-batch")
async def get_meal_batch():
    """
    **AI ENDPOINT 1:** Generates a batch of 5 meal-swipe cards.
    Filters ingredients into "to buy" and "you have" lists.
    """
    if not CURRENT_USER_PROFILE:
        return {"error": "User profile not set. Please complete onboarding first."}

    profile_summary = json.dumps(CURRENT_USER_PROFILE, indent=2)
    available_groceries = json.dumps(MOCK_DATA, indent=2)

    system_prompt = f"""
    You are a meal-planning expert. Your goal is to generate 5 meal ideas
    for the user based on their profile.
    
    USER PROFILE:
    {profile_summary}
    
    AVAILABLE GROCERIES (Use only these items):
    {available_groceries}
    
    You MUST respond with *only* a valid JSON object. Do not include
    any text before or after the JSON.
    Your response must match this exact structure:
    
    {{
      "meals": [
        {{
          "meal_name": "Example: High-Protein Chicken Salad",
          "description": "A short, enticing description.",
          "recipe_steps": [
            "1. Chop chicken.",
            "2. Mix with avocado.",
            "3. Serve."
          ],
          "ingredients": [
            {{"item_name": "Organic Chicken Breast", "quantity": "100g"}},
            {{"item_name": "Avocado", "quantity": "1 whole"}},
            {{"item_name": "Extra Virgin Olive Oil", "quantity": "1 tbsp"}},
            {{"item_name": "Salt", "quantity": "1 pinch"}}
          ]
        }}
      ]
    }}
    
    Ensure ingredients are *only* from the AVAILABLE GROCERIES list.
    """

    try:
        completion = client.chat.comD.create(
            model="gpt-4o", 
            messages=[{"role": "system", "content": system_prompt}],
            response_format={"type": "json_object"} 
        )
        
        response_text = completion.choices[0].message.content
        json_response = json.loads(response_text)
        
        # 1. Get the user's "running low" list
        running_low_items = {
            item['item_name'].lower()
            for item in CURRENT_USER_PROFILE.get("pantry_items", [])
            if item['last_purchased_days_ago'] >= (item['purchase_frequency_weeks'] * 7) - 3 # (e.g., 13 days is >= 14-3)
        }
        
        # 2. Process each meal from the AI
        for meal in json_response.get("meals", []):
            ingredients_to_buy = []
            ingredients_you_have = []
            
            original_ingredients = meal.get("ingredients", [])
            
            for ing in original_ingredients:
                item_name_lower = ing.get("item_name", "").lower()
                
                # Logic:
                # 1. Is it on the "running low" list?
                if item_name_lower in running_low_items:
                    ingredients_to_buy.append(ing)
                # 2. Is it a common staple (and not running low)?
                elif item_name_lower in COMMON_PANTRY_STAPLES:
                    ingredients_you_have.append(ing)
                # 3. Otherwise, it's a regular item to buy.
                else:
                    ingredients_to_buy.append(ing)
            
            # 3. Add our new, smart lists to the meal object
            meal["ingredients_to_buy"] = ingredients_to_buy
            meal["ingredients_you_have"] = ingredients_you_have
            
            # 4. Remove the original messy list
            if "ingredients" in meal:
                del meal["ingredients"]
                
        # Send the modified, smarter JSON to the frontend
        return json_response

    except Exception as e:
        print(f"AI/JSON Error: {e}")
        return {"error": f"Failed to generate meals: {e}"}

# ---
# ENDPOINT 3: THE SHOPPING LIST
# ---
@app.post("/add-to-list")
async def add_to_list(request: AddToListRequest):
    """
    **NON-AI ENDPOINT:** Adds ingredients from a "swipe right"
    to the global shopping list.
    """
    global SHOPPING_LIST
    
    for ingredient in request.ingredients:
        # Simple add for the demo. A real app would check for duplicates.
        SHOPPING_LIST.append(ingredient.model_dump())
    
    print(f"Updated Shopping List: {SHOPPING_LIST}")
    
    # Return the complete new list
    return {"shopping_list": SHOPPING_LIST}

# ---
# ENDPOINT 4: THE PANTRY CHECK
# ---
@app.post("/check-pantry")
async def check_pantry():
    """
    **AI ENDPOINT 2:** Checks user's pantry trends and suggests
    items to re-order, formatted as JSON.
    """
    if not CURRENT_USER_PROFILE:
        return {"error": "User profile not set."}

    profile_summary = json.dumps(CURRENT_USER_PROFILE, indent=2)

    system_prompt = f"""
    You are a proactive pantry assistant. Analyze the user's profile,
    specifically their 'pantry_items' and 'preferences'.
    
    USER PROFILE:
    {profile_summary}
    
    Your goal is to find items the user might be running low on or
    would prefer.
    
    You MUST respond with *only* a valid JSON object, structured like this:
    {{
      "suggestions": [
        {{
          "item_name": "Extra Virgin Olive Oil",
          "reason": "It looks like you're running low (you buy it every 2 weeks).",
          "ingredient_to_add": {{"item_name": "Extra Virgin Olive Oil", "quantity": "1 bottle"}}
        }},
        {{
          "item_name": "Almond Milk",
          "reason": "You prefer this over dairy milk.",
          "ingredient_to_add": {{"item_name": "Unsweetened Almond Milk", "quantity": "1 carton"}}
        }}
      ]
    }}
    
    If there are no suggestions, return {{"suggestions": []}}.
    """
    
    try:
        completion = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[{"role": "system", "content": system_prompt}],
            response_format={"type": "json_object"}
        )
        response_text = completion.choices[0].message.content
        json_response = json.loads(response_text)
        
        return json_response

    except Exception as e:
        print(f"AI/JSON Error: {e}")
        return {"error": f"Failed to check pantry: {e}"}

# --- 6. RUN THE APP ---
if __name__ == "__main__":
    print("--- Starting Smart Meal Swiper Backend ---")
    print("Running on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)