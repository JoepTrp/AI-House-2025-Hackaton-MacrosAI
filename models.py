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
    quantity: str

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
    item_name: str
    purchase_date: datetime

class Reminder(BaseModel):
    item_name: str
    last_purchased_days_ago: int
    typical_interval_days: int

class Cart(BaseModel):
    items: List[GroceryItem]

class RecipeIdea(BaseModel):
    recipe_title: str
    tags: List[str]
    estimated_macros: Optional[Macros] = None

class RecipeLink(BaseModel):
    title: str
    ingredients_per_portion: List[GroceryItem]
    url: str
    source: str

class RecipeSelectionContext(BaseModel):
    user_id: str
    macros: Macros
    goals: Dict[str, str]
    liked_recipes: List[RecipeLink] = Field(default_factory=list)
    disliked_recipes: List[RecipeLink] = Field(default_factory=list)
    maybe_later_recipes: List[RecipeLink] = Field(default_factory=list)
    preference_vector_title: Optional[List[float]] = None
    preference_vector_tags: Optional[List[float]] = None
    purchase_history: List[PurchaseRecord] = Field(default_factory=list)
    purchase_patterns: Dict[str, float] = Field(default_factory=dict)

class Ideas(BaseModel):
    ideas: list[RecipeIdea]

class Links(BaseModel):
    links: list[RecipeLink]