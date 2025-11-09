from typing import List

from openai import OpenAI
from pydantic import BaseModel, Field

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
        calories=2000,
        protein=150,
        carbs=250,
        fat=70
    ),
    goals={"goal": "lose_weight", "diet": "keto"},
    liked_recipes=[],
    disliked_recipes=[],
    maybe_later_recipes=[]
)

def generate_recipe_ideas(context: RecipeSelectionContext, n_ideas: int = 5) -> RecipeIdea | None:
    """Use OpenAI model to generate structured recipe ideas given user macros and goals"""

    prompt = f"""
    Think of a creative, healthy recipe idea for someone who wants to {context.goals.get('goal')}
    with these daily macros:
    Calories: {context.macros.calories}, Protein: {context.macros.protein}g,
    Carbs: {context.macros.carbs}g, Fat: {context.macros.fat}g.
    Each recipe should have a title, description, and about 5 relevant tags describing cuisine type, flavor profile, and key condiments.
    """
    response = client.responses.parse(
        model="gpt-5-nano",
        input=[
            {"role": "system", "content": "Your name is Sarah Brown. You are an expert nutritionist and recipe planning assistant."},
            {
                "role": "user",
                "content": prompt,
            },
        ],
        text_format=RecipeIdea,
    )

    return response.output_parsed

res = generate_recipe_ideas(fake_context, n_ideas=5)

print(res)
