"""
recipe_agent_pipeline.py
Boilerplate for an AI Recipe Generation Pipeline using OpenAI models and web search
"""
from urllib.parse import urlparse

import numpy as np
from openai import OpenAI
from pydantic import BaseModel, Field
from models import Macros, GroceryList, GroceryItem, RecipeIdea, RecipeLink


# -----------------------
# STEP 0: Define Models
# -----------------------

class Ideas(BaseModel):
    ideas: list[RecipeIdea]

class Links(BaseModel):
    links: list[RecipeLink]

class RecipeSelectionContext(BaseModel):
    user_id: str
    macros: Macros
    goals: dict[str, str] # e.g. {"goal": "lose_weight", "diet": "keto"}
    liked_recipes: list[RecipeIdea] = Field(default_factory=list)
    disliked_recipes: list[RecipeIdea] = Field(default_factory=list)
    maybe_later_recipes: list[RecipeIdea] = Field(default_factory=list)


client = OpenAI(
    api_key = "sk-Q_wlHlL9BIrIBosXizyeSQ",
    base_url = "https://fj7qg3jbr3.execute-api.eu-west-1.amazonaws.com/v1"
)

def get_embedding(text: str) -> np.ndarray:
    """Compute embedding for a given text using OpenAI embeddings API."""
    if not text.strip():
        return np.zeros(1536)  # text-embedding-3-large dimension
    resp = client.embeddings.create(
        model="text-embedding-3-large",
        input=text
    )
    return np.array(resp.data[0].embedding)

# def summarize_preferences(context: RecipeSelectionContext) -> str:
#     """Convert user preference vectors into a natural language summary via embedding similarity."""
#
#     if context.preference_vector_title is None:
#         return "No inferred preferences from the user"
#
#     # We need a small reference vocabulary of culinary concepts, tags, cuisines, etc.
#     reference_tags = [
#         "spicy", "mild", "vegetarian", "vegan", "nutty", "tangy", "herbs", "keto", "paleo", "high-protein", "asian",
#         "italian", "indian", "mexican", "french", "african", "middle-eastern", "mediterranean",
#         "south american", "game", "poultry", "low-carb", "slow-cooked",
#         "comfort food", "easy to make", "fresh", "grilled",
#         "seafood", "fish", "chicken", "beef", "pasta", "salad", "sweet", "savory", "soupy", "mushrooms", "filling"
#     ]
#
#     def most_similar_concepts(user_vec, concepts):
#         similarities = []
#         for tag in concepts:
#             tag_embedding = get_embedding(tag)
#             cosine_similarity = np.dot(user_vec, tag_embedding) / (np.linalg.norm(user_vec) * np.linalg.norm(tag_embedding) + 1e-9)
#             similarities.append((tag, cosine_similarity))
#         # take top few
#         top = sorted(similarities, key=lambda x: x[1], reverse=True)[:5]
#         return [t for t, _ in top]
#
#     title_prefs = most_similar_concepts(np.array(context.preference_vector_title), reference_tags)
#     tag_prefs = most_similar_concepts(np.array(context.preference_vector_tags), reference_tags)
#
#     # Merge and lightly describe
#     return f"User tends to enjoy recipes with themes like {', '.join(set(title_prefs + tag_prefs))}."


# -----------------------
# STEP 1: Recipe Idea Generation
# -----------------------

def generate_recipe_ideas(context: RecipeSelectionContext, n_ideas: int = 5) -> Ideas | None:
    """Use OpenAI model to generate structured recipe ideas given user macros and goals"""

    prompt = f"""
    Think of {n_ideas} creative, healthy recipe ideas for someone who wants to {context.goals.get('goal')}
    with these daily macros:
    Calories: {context.macros.calories}, Protein: {context.macros.protein}g,
    Carbs: {context.macros.carbs}g, Fat: {context.macros.fat}g.
    Each recipe should have a title, description, and about 5 relevant tags describing cuisine type, flavor profile, and key condiments.
    """
    response = client.responses.parse(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": "Your name is Sarah Brown. You are an expert nutritionist and recipe planning assistant."},
            {
                "role": "user",
                "content": prompt,
            },
        ],
        text_format=Ideas,
    )
    return response.output_parsed

# -----------------------
# STEP 2: Find Recipe Links (Web Search)
# -----------------------

def find_recipe_links(ideas: list[RecipeIdea]) -> list[RecipeLink]:
    """
    Uses OpenAI web_search tool to find recipes biased toward highly rated and widely reviewed recipes.
    """
    results: list[RecipeLink] = []
    for idea in ideas:
        print(ideas)
        prompt = f"""
        Find healthy recipes online for the following recipe idea: {idea.recipe_title}.
        Prefer recipes that are:
          - Highly rated (ideally 4 stars or higher)
          - Rated by a large number of users (more than 50)
        Only include recipes that are accessible online.
        Also, retrieve the main grocery items needed (name and quantities) for one portion
        """

        link_associated_with_this_idea = client.responses.parse(
            model="gpt-4.1-mini",
            tools=[{"type": "web_search", "external_web_access": True}],
            tool_choice="auto",
            input=[{"role": "system", "content": "Your name is Michael Douglas. You have are a well-experienced home cook, with a critical eye and attention to detail."},
                {
                "role": "user",
                "content": prompt,
                },
            ],
            text_format=RecipeLink,
        )

        results.append(link_associated_with_this_idea.output_parsed)

    return results


# -----------------------
# STEP 3: Update User Preferences (Learning/Adaptation)
# -----------------------

# def update_user_preferences(context: RecipeSelectionContext, alpha: float = 0.5) -> RecipeSelectionContext:
#     """
#     Update user preference vectors (title and tags) based on likes/dislikes/maybe-laters.
#     Uses a simple reinforcement-like weighted averaging approach.
#     - alpha: learning rate (0 < alpha <= 1)
#     """
#
#     # Reward mapping
#     reward_map = {"like": 1.0, "dislike": -1.0, "maybe": -0.1}
#
#     # Collect recipes with associated rewards
#     interactions = (
#         [(r, reward_map["like"]) for r in context.liked_recipes] +
#         [(r, reward_map["dislike"]) for r in context.disliked_recipes] +
#         [(r, reward_map["maybe"]) for r in context.maybe_later_recipes]
#     )
#
#     if not interactions:
#         return context  # nothing new to update
#
#     # Initialize preference vectors if missing
#     if context.preference_vector_title is None:
#         context.preference_vector_title = [0.0] * 1536
#     if context.preference_vector_tags is None:
#         context.preference_vector_tags = [0.0] * 1536
#
#     pref_title = np.array(context.preference_vector_title)
#     pref_tags = np.array(context.preference_vector_tags)
#     alpha_titles = 0.4
#     alpha_tags = 0.05
#
#     for recipe, reward in interactions:
#         # --- Title embedding update ---
#         title_emb = get_embedding(recipe.title)
#         pref_title = (1 - alpha_titles) * pref_title + alpha_titles * (reward * title_emb)
#
#         # --- Tag embeddings: update locally per tag ---
#         if hasattr(recipe, "tags") and recipe.tags:
#             for tag in recipe.tags:
#                 tag_emb = get_embedding(tag)
#                 # each tag nudges the preference vector a little
#                 pref_tags = (1 - alpha_tags) * pref_tags + alpha_tags * (reward * tag_emb)
#
#     # Update context
#     context.preference_vector_title = pref_title.tolist()
#     context.preference_vector_tags = pref_tags.tolist()
#
#     return context


# -----------------------
# STEP 4: Compute Grocery List
# -----------------------

def compute_grocery_items(context: RecipeSelectionContext, selected_recipes: Links) -> GroceryList:
    """
    Compute grocery list and estimated price for the selected recipe URLs,
    using OpenAI web_search and structured parsing.
    """

    # Build a simple textual instruction
    recipe_text = "\n".join([f"- {r.title}: {r.ingredients_per_portion}" for r in selected_recipes.links])
    prompt = f"""
    You are building a grocery list for a person who has the following daily macro requirements:
    Calories: {context.macros.calories}, Protein: {context.macros.protein}g,
    Fat: {context.macros.fat}g, Carbs: {context.macros.carbs}g.
    The user has selected some recipes to cook for next week. You may find the ingredients per portion for each of the recipes.
    Compose a grocery list, which allows the user to cook a couple portions of the selected recipes, in a balanced way.
    If very similar ingredients appear in multiple lists, only include one of that ingredient type in the final grocery list, adding the quantities and multiplying by serving size.
    Avoid ingredients everyone disposes of (salt, pepper and water) and do not include ingredient mechanical descriptors (instead of chopped cucumbers, just keep cucumbers).
    For the already defined items: replace the names and quantities with purchasable groceries (replace all tablespoons, teaspoons, with purchasable items or metric units)
        - Instead of lemon juice, say one lemon
        - Instead of a tbsp of paprika: say paprika, and give the gram-age of a bottle as quantity
        - Instead of a tbsp of parsley: say parsley, and give the gram-age of a handful of parsley.
        - Instead of a cup of milk, olive oil, tomato sauce... replace with multiples of entire containers. For instance, for a cup of milk: add a milk item, which has a quantity of 1L (typical carton)
    Finally, estimate the total price up to two decimal digits in euros for the grocery list in the Netherlands.
    Recipes:
    {recipe_text}
    """

    print(prompt)

    # Call the Responses API with web_search restricted to the recipe URLs
    response = client.responses.parse(
        model="gpt-4.1-mini",
        input=[{"role": "system", "content": "You are an James Oliver, an expert nutritionist, with an affinity for mathematics and psychology."},
                {
                "role": "user",
                "content": prompt,
                },
            ],
        text_format=GroceryList,
    )
    return response.output_parsed


# -----------------------
# STEP 5: Pipeline Orchestration
# -----------------------

# def run_pipeline():
#     # Example user setup
#     user_context = RecipeSelectionContext(
#         user_id="u123",
#         macros=Macros(calories=2000, protein=150, carbs=200, fat=60),
#         goals={"goal": "gain_muscle", "diet": "balanced"}
#     )
#
#     # Generate ideas
#     ideas = generate_recipe_ideas(user_context)
#     print("Generated Ideas:", [i.title for i in ideas])
#
#     # Find web links
#     links = find_recipe_links(ideas)
#     print("Found Links:", [l.url for l in links])
#
#     # Simulate user liking 3 recipes
#     user_context.liked_recipes = links[:3]
#     user_context = update_user_preferences(user_context)
#
#     # # Compute grocery list
#     # groceries = compute_grocery_items(user_context.liked_recipes)
#     # print("Grocery List:", [g.name for g in groceries])
#     #
#     # return groceries


if __name__ == "__main__":
    # groceries = run_pipeline()
    print("Pipeline completed.")