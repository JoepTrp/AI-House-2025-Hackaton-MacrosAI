
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from enum import Enum
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from openai import OpenAI

from recipe_selection import generate_recipe_ideas
from recipe_selection import find_recipe_links
import models
import smart_reminders

# --------------------------- config ---------------------------
load_dotenv()
app = FastAPI(title="Smart Meal Swiper Backend")
client = OpenAI(
    api_key = "sk-Q_wlHlL9BIrIBosXizyeSQ",
    base_url = "https://fj7qg3jbr3.execute-api.eu-west-1.amazonaws.com/v1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------- onboarding models ----------------
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

# --------------------------- global variable ------------------
# This is a replacement for a database later on, for now we just save data locally
CURRENT_USER_CONTEXT: Optional[models.RecipeSelectionContext] = None

# --------------------------- helper ---------------------------
def calculate_targets(data: OnboardingData) -> Dict[str, int]:
    bmr = (10 * data.weight) + (6.25 * data.height) - (5 * data.age) + 5
    activity_multipliers = {
        "sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725
    }
    tdee = bmr * activity_multipliers[data.activity_level]
    
    if data.goal == "lose weight": target_calories = tdee - 500
    elif data.goal == "gain muscle": target_calories = tdee + 300
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
    global CURRENT_USER_CONTEXT
    
    targets = calculate_targets(data)

    user_macros = models.Macros(
        calories=targets.get("target_calories"),
        protein=targets.get("target_protein"),
        carbs=targets.get("target_carbs"),
        fat=targets.get("target_fat")
    )
    user_goals = {"goal": data.goal.value}

    CURRENT_USER_CONTEXT = models.RecipeSelectionContext(
        user_id=data.name, 
        macros=user_macros,
        goals=user_goals
    )

    # ----------------- FAKED USER HABBITS -------------------
    today = datetime.now()
    CURRENT_USER_CONTEXT.purchase_history.append(
        models.PurchaseRecord(item_name="milk", purchase_date=today - timedelta(days=15))
    )
    CURRENT_USER_CONTEXT.purchase_history.append(
        models.PurchaseRecord(item_name="milk", purchase_date=today - timedelta(days=8))
    )
    CURRENT_USER_CONTEXT.purchase_history.append(
        models.PurchaseRecord(item_name="eggs", purchase_date=today - timedelta(days=10))
    )
    CURRENT_USER_CONTEXT.purchase_history.append(
        models.PurchaseRecord(item_name="eggs", purchase_date=today - timedelta(days=5))
    )
    CURRENT_USER_CONTEXT.purchase_patterns = smart_reminders.update_purchase_patterns(
        CURRENT_USER_CONTEXT.purchase_history
    )
    
    print(f"New profile saved: {CURRENT_USER_CONTEXT.model_dump_json(indent=2)}")
    return {"success"}

# generate new recipe cards
@app.get("/get-meal-batch")
async def get_meal_batch():
    print("batch is being obtained")
    global CURRENT_USER_CONTEXT
    if not CURRENT_USER_CONTEXT:
        return {"error": "User profile not set. Please complete onboarding first."}
    
    context = CURRENT_USER_CONTEXT 
    try:
        ideas = generate_recipe_ideas(context, 5)
        print(ideas.ideas)
        nested_links_list = find_recipe_links(ideas.ideas)
        flat_links_list = [link for sublist in nested_links_list for link in sublist]
        print("recipies received.")

        return {"links": flat_links_list, "ideas": ideas.ideas}
        
    except Exception as e:
        print(f"Error in recipe pipeline: {e}")
        return {"error": "Failed to generate recipes."}

# log purchased items to track and update patterns
@app.post("/checkout")
async def checkout_cart(cart: models.Cart):
    global CURRENT_USER_CONTEXT
    if not CURRENT_USER_CONTEXT:
        return {"error": "User profile not set. Please complete onboarding first."}

    context = CURRENT_USER_CONTEXT
    now = datetime.now()

    for item in cart.items:
        record = models.PurchaseRecord(
            item_name=item.name.lower().strip(),
            purchase_date=now
        )
        context.purchase_history.append(record)

    context.purchase_patterns = smart_reminders.update_purchase_patterns(context.purchase_history)
    
    print(f"Checkout complete. New patterns: {context.purchase_patterns}")
    return {"success"}

# returns reminders for items that the user may want to re-stock based on user purchase patterns
@app.get("/get-reminders", response_model=Dict[str, List[models.Reminder]])
async def get_reminders():
    global CURRENT_USER_CONTEXT
    if not CURRENT_USER_CONTEXT:
        return {"reminders": []}

    context = CURRENT_USER_CONTEXT
    today = datetime.now()
    reminders = []
    
    latest_purchase_dates = smart_reminders.get_latest_purchase_dates(context.purchase_history)

    for item_name, avg_interval in context.purchase_patterns.items():
        if item_name not in latest_purchase_dates:
            continue
            
        last_purchase_date = latest_purchase_dates[item_name]
        days_since_last_purchase = (today - last_purchase_date).days
        
        if days_since_last_purchase > avg_interval:
            reminder = models.Reminder(
                item_name=item_name.title(),
                last_purchased_days_ago=days_since_last_purchase,
                typical_interval_days=int(avg_interval)
            )
            reminders.append(reminder)
            
    return {"reminders": reminders}

# main
if __name__ == "__main__":
    print("Running on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)