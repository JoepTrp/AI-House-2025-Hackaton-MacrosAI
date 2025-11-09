from typing import List
from urllib.parse import urlparse

from openai import OpenAI
from pydantic import BaseModel, Field

from models import GroceryList
from recipe_selection import RecipeLink

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

recipe_link_1 = RecipeLink(title="One Pot Cajun Chicken and Rice",
                         url="https://www.lecremedelacrumb.com/one-pot-spicy-cajun-chicken-rice/",
                         source="Creme de la Crumb")

recipe_link_2 = RecipeLink(title="Grilled Salmon with Garlic and Herbs",
                         url="https://www.dinneratthezoo.com/grilled-salmon/",
                         source="Dinner at the Zoo")


selected_recipes_test = [recipe_link_2, recipe_link_1]

def compute_grocery_items(context: RecipeSelectionContext, selected_recipes: list[RecipeLink]) -> GroceryList:
    """
    Compute grocery list and estimated price for the selected recipe URLs,
    using OpenAI web_search and structured parsing.
    """

    # Collect allowed domains from the recipe URLs
    allowed_domains = [
        urlparse(recipe.url).netloc for recipe in selected_recipes
    ]

    # Build a simple textual instruction
    recipe_text = "\n".join([f"- {r.title}: {r.url}" for r in selected_recipes])
    prompt = f"""
    You are an expert nutritionist, with an affinity for mathematics and psychology.
    You are building a grocery list for a person who has the following daily macro requirements:
    Calories: {context.macros.calories}, Protein: {context.macros.protein}g,
    Fat: {context.macros.fat}g, Carbs: {context.macros.carbs}g.
    The user has selected some recipes to cook for next week.
    Visit each of the following recipe URLs, extract their ingredient lists,
    and return a combined grocery list in JSON format with item name, quantity, and estimated price.
    You should estimate a reasonable number of servings so that the diet is varied and balanced, for one week.
    Merge duplicates (e.g., multiple 'sugar' entries should be combined).
    Use metric units where possible (Liters L for liquids, grams g for solid foods)

    Recipes:
    {recipe_text}
    """

    # Call the Responses API with web_search restricted to the recipe URLs
    response = client.responses.parse(
        model="gpt-5",
        tools=[
            {
                "type": "web_search",
                "filters": {
                    "allowed_domains": allowed_domains
                },
            }
        ],
        tool_choice="auto",
        include=["web_search_call.action.sources"],
        input=prompt,
        text_format=GroceryList,
    )

    # Parse the model output directly into the GroceryList schema


    return response.output_parsed

res = compute_grocery_items(fake_context, selected_recipes_test)

print(res)
