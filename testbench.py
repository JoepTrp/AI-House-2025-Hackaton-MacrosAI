from openai import OpenAI
from models import *
from recipe_selection import *

# client = OpenAI(
#     api_key = "sk-Q_wlHlL9BIrIBosXizyeSQ",
#     base_url = "https://fj7qg3jbr3.execute-api.eu-west-1.amazonaws.com/v1/chat/completions"
# )

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
    maybe_later_recipes=[],
    preference_vector_title=[0.1, 0.5, 0.2],
    preference_vector_tags=[0.3, 0.4, 0.3]
)

ideas = generate_recipe_ideas(fake_context, 5)
nested_links_list = find_recipe_links(ideas)
print(nested_links_list)