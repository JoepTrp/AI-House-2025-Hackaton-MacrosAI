from typing import List
from urllib.parse import urlparse

from openai import OpenAI
from pydantic import BaseModel, Field

from models import GroceryList, GroceryItem, Links
from recipe_selection import RecipeLink, compute_grocery_items

client = OpenAI(
    api_key = "sk-Q_wlHlL9BIrIBosXizyeSQ",
    base_url = "https://fj7qg3jbr3.execute-api.eu-west-1.amazonaws.com/v1"
)


class Macros(BaseModel):
    calories: int
    protein: int
    carbs: int
    fat: int



class RecipeIdea(BaseModel):
    recipe_title: str
    main_ingredients: list[str]
    tags: list[str]

class Ideas(BaseModel):
    ideas: list[RecipeIdea]


class RecipeSelectionContext(BaseModel):
    user_id: str
    macros: Macros
    goals: dict[str, str] # e.g. {"goal": "lose_weight", "diet": "keto"}
    liked_recipes: List[RecipeIdea] = Field(default_factory=list)
    disliked_recipes: List[RecipeIdea] = Field(default_factory=list)
    maybe_later_recipes: List[RecipeIdea] = Field(default_factory=list)

fake_context = RecipeSelectionContext(
    user_id="user_123",
    macros=Macros(
        calories=2500,
        protein=100,
        carbs=120,
        fat=70
    ),
    goals={"goal": "gain muscle", "diet": "high-protein"},
    liked_recipes=[],
    disliked_recipes=[],
    maybe_later_recipes=[]
)

recipe_link_1 = RecipeLink(
    title="One Pot Cajun Chicken and Rice",
    url="https://www.lecremedelacrumb.com/one-pot-spicy-cajun-chicken-rice/",
    source="Creme de la Crumb",
    ingredients_per_portion=[
        GroceryItem(name="chicken breast", quantity="200g"),
        GroceryItem(name="long grain rice", quantity="100g"),
        GroceryItem(name="chicken broth", quantity="250ml"),
        GroceryItem(name="cajun seasoning", quantity="1 tbsp"),
        GroceryItem(name="olive oil", quantity="1 tbsp"),
        GroceryItem(name="bell pepper", quantity="1/2"),
    ],
)

recipe_link_2 = RecipeLink(
    title="Grilled Salmon with Garlic and Herbs",
    url="https://www.dinneratthezoo.com/grilled-salmon/",
    source="Dinner at the Zoo",
    ingredients_per_portion=[
        GroceryItem(name="salmon fillet", quantity="150g"),
        GroceryItem(name="olive oil", quantity="1 tbsp"),
        GroceryItem(name="garlic cloves", quantity="2"),
        GroceryItem(name="tomato juice", quantity="3 tbsp"),
        GroceryItem(name="fresh parsley", quantity="1 tbsp"),
        GroceryItem(name="salt and pepper", quantity="to taste"),
    ],
)

selected_recipes_test = [recipe_link_2, recipe_link_1]

res = compute_grocery_items(fake_context, Links(links=selected_recipes_test))

print(res)
