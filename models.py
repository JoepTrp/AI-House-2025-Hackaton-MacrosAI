from pydantic import BaseModel

class Macros(BaseModel):
    calories: int
    protein: int
    carbs: int
    fat: int

class GroceryItem(BaseModel):
    name: str
    quantity: str # 1L, 500g, etc.
    macros: Macros
    price: float

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