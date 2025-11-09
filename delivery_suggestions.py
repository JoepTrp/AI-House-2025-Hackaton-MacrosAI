from openai import OpenAI
from typing import List, Optional

from pydantic import BaseModel

from main import client
from models import RecipeSelectionContext

class DeliverySuggestion(BaseModel):
    restaurant_name: str
    food_item: str
    description: str
    estimated_macros: Optional[Macros] = None
    price_estimate: Optional[float] = None
    delivery_platform: Optional[str] = None  # e.g., "Thuisbezorgd", "UberEats", "Deliveroo"
    url: Optional[str] = None


def generate_takeaway_suggestions(context: RecipeSelectionContext, user_location: str, n_suggestions: int = 5) -> List[
    DeliverySuggestion]:
    """
    Generate healthy, personalized takeaway/food delivery suggestions based on user context.
    Uses web search to find local options and GPT to reason about best matches.
    """

    # Summarize user preferences into natural language, same as before
    # user_taste_summary = summarize_preferences(context)


    prompt = f"""
    You are Sarah Brown, a nutrition expert and food recommendation assistant.
    Suggest {n_suggestions} nearby takeaway dishes for a user in {user_location}.
    The user wants to {context.goals.get('goal')} and typically enjoys: {user_taste_summary}.
    Consider their daily macros:
    - Calories: {context.macros.calories}
    - Protein: {context.macros.protein}g
    - Carbs: {context.macros.carbs}g
    - Fat: {context.macros.fat}g

    Search for healthy restaurants or takeaway meals available on Thuisbezorgd or other delivery platforms in that area.
    Return structured JSON with restaurant name, food item, short description, estimated macros, price estimate, and URL.
    """

    response = client.responses.parse(
        model="gpt-5",
        tools=[{"type": "web_search", "external_web_access": True}],
        tool_choice="auto",
        input=[
            {"role": "user", "content": prompt},
        ],
        text_format=List[DeliverySuggestion],
    )

    return response.output_parsed