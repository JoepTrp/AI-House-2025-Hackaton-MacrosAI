from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from typing import List, Dict, Optional

class Macros(BaseModel):
    calories: float
    protein: float
    carbs: float
    fat: float

class GroceryItem(BaseModel):
    name: str
    quantity: str # 1L, 500g, etc.

class GroceryList(BaseModel):
    items: list[GroceryItem]
    estimated_price: float

class Meal(BaseModel):
    meal_name: str
    description: str
    recipe_steps: list[str]
    ingredients: list[GroceryItem]

class Suggestion(BaseModel):
    item: GroceryItem
    number: int
    reason: str

class Suggestions(BaseModel):
    suggestions: list[Suggestion]


class PurchaseRecord(BaseModel):
    """Logs a single item purchase with a timestamp."""
    item_name: str
    purchase_date: datetime

class Reminder(BaseModel):
    """A single reminder object to send to the frontend."""
    item_name: str
    last_purchased_days_ago: int
    typical_interval_days: int

class RecipeIdea(BaseModel):
    recipe_title: str
    tags: List[str]
    estimated_macros: Optional[Macros] = None

class RecipeLink(BaseModel):
    title: str
    url: str
    source: str
    ingredients_per_portion: List[GroceryItem]
    

class RecipeSelectionContext(BaseModel):
    user_id: str
    macros: Macros
    goals: Dict[str, str]  # e.g. {"goal": "lose_weight", "diet": "keto"}
    liked_recipes: List[RecipeLink] = Field(default_factory=list)
    disliked_recipes: List[RecipeLink] = Field(default_factory=list)
    maybe_later_recipes: List[RecipeLink] = Field(default_factory=list)
    preference_vector_title: Optional[List[float]] = None
    preference_vector_tags: Optional[List[float]] = None
    purchase_history: List[PurchaseRecord] = Field(default_factory=list) # PurchaseRecord must also be in models.py
    purchase_patterns: Dict[str, float] = Field(default_factory=dict) # e.g., {"milk": 7.3}
