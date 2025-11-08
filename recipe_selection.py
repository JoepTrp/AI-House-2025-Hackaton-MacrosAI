"""
recipe_agent_pipeline.py
Boilerplate for an AI Recipe Generation Pipeline using OpenAI models and web search
"""
import numpy as np
from openai import OpenAI
from pydantic import BaseModel, Field
<<<<<<< HEAD
from typing import List, Dict, Optional
import json
import openai
import requests
from dataclasses import dataclass

=======
>>>>>>> backend
from models import Macros


# -----------------------
# STEP 0: Define Models
# -----------------------

<<<<<<< HEAD
client = OpenAI(
    api_key = "sk-FAyzaUaK8JlUzvrmIU2XlA",
    base_url = "https://fj7qg3jbr3.execute-api.eu-west-1.amazonaws.com/v1/chat/completions"
)

def get_embedding(text: str) -> np.ndarray:
    """Compute embedding for a given text using OpenAI embeddings."""
=======
class RecipeIdea(BaseModel):
    recipe_title: str
    main_ingredients: list[str]
    tags: list[str]

class Ideas(BaseModel):
    ideas: list[RecipeIdea]



class RecipeLink(BaseModel):
    title: str
    url: str
    source: str


class RecipeSelectionContext(BaseModel):
    user_id: str
    macros: Macros
    goals: dict[str, str] # e.g. {"goal": "lose_weight", "diet": "keto"}
    liked_recipes: list[RecipeIdea] = Field(default_factory=list)
    disliked_recipes: list[RecipeIdea] = Field(default_factory=list)
    maybe_later_recipes: list[RecipeIdea] = Field(default_factory=list)


client = OpenAI(
    api_key = "sk-FAyzaUaK8JlUzvrmIU2XlA",
    base_url = "https://fj7qg3jbr3.execute-api.eu-west-1.amazonaws.com/v1"
)

def get_embedding(text: str) -> np.ndarray:
    """Compute embedding for a given text using OpenAI embeddings API."""
    if not text.strip():
        return np.zeros(1536)  # text-embedding-3-large dimension
>>>>>>> backend
    resp = client.embeddings.create(
        model="text-embedding-3-large",
        input=text
    )
    return np.array(resp.data[0].embedding)

<<<<<<< HEAD
=======
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


>>>>>>> backend
# -----------------------
# STEP 1: Recipe Idea Generation
# -----------------------

<<<<<<< HEAD
def generate_recipe_ideas(context: RecipeSelectionContext, n_ideas: int = 5) -> List[RecipeIdea] | None:
    """Use OpenAI model to generate structured recipe ideas given user macros and goals"""
=======
def generate_recipe_ideas(context: RecipeSelectionContext, n_ideas: int = 5) -> Ideas | None:
    """Use OpenAI model to generate structured recipe ideas given user macros and goals"""

>>>>>>> backend
    prompt = f"""
    Think of {n_ideas} creative, healthy recipe ideas for someone who wants to {context.goals.get('goal')}
    with these daily macros:
    Calories: {context.macros.calories}, Protein: {context.macros.protein}g,
    Carbs: {context.macros.carbs}g, Fat: {context.macros.fat}g.
<<<<<<< HEAD
    Fill the tags field with relevant descriptors on cuisine type, flavor profile, key condiments, ... (at most 6-7)
    """
    response = client.responses.parse(
        model="gpt-5",
=======
    Each recipe should have a title, description, and about 5 relevant tags describing cuisine type, flavor profile, and key condiments.
    """
    response = client.responses.parse(
        model="gpt-5-nano",
>>>>>>> backend
        input=[
            {"role": "system", "content": "Your name is Sarah Brown. You are an expert nutritionist and recipe planning assistant."},
            {
                "role": "user",
                "content": prompt,
            },
        ],
<<<<<<< HEAD
        text_format=List[RecipeIdea],
=======
        text_format=Ideas,
>>>>>>> backend
    )

    return response.output_parsed

# -----------------------
# STEP 2: Find Recipe Links (Web Search)
# -----------------------

<<<<<<< HEAD
def find_recipe_links(ideas: List[RecipeIdea]) -> List[List[RecipeLink]]:
    """
    Uses OpenAI web_search tool to find recipes biased toward highly rated and widely reviewed recipes.
    """
    results: List[List[RecipeLink]] = []
=======
def find_recipe_links(ideas: list[RecipeIdea]) -> list[list[RecipeLink]]:
    """
    Uses OpenAI web_search tool to find recipes biased toward highly rated and widely reviewed recipes.
    """
    results: list[list[RecipeLink]] = []
>>>>>>> backend

    for idea in ideas:

        prompt = f"""
        Find 1-3 healthy recipes online for the following recipe idea: "{idea.title}".
        Prefer recipes that are:
          - Highly rated (ideally 4 stars or higher)
          - Rated by a large number of users (hundreds or thousands)
        Only include recipes that are accessible online.
        """

        links_associated_with_this_idea = client.responses.parse(
            model="gpt-5",
            tools=[{"type": "web_search", "external_web_access": True}],
            tool_choice="auto",
            input=[{"role": "system", "content": "Your name is Michael Douglas. You have are a well-experienced home cook, with a critical eye and attention to detail."},
                {
                "role": "user",
                "content": prompt,
                },
            ],
<<<<<<< HEAD
            text_format=List[RecipeLink],
=======
            text_format=list[RecipeLink],
>>>>>>> backend
        )

        results.append(links_associated_with_this_idea.output_parsed)

    return results


# -----------------------
# STEP 3: Update User Preferences (Learning/Adaptation)
# -----------------------

<<<<<<< HEAD
def update_user_preferences(context: RecipeSelectionContext) -> RecipeSelectionContext:
    """
    Update the user's preference vector based on liked, disliked, and maybe-later recipes.
    We use embeddings of recipe titles/tags and weighted averaging.
    """
    all_recipes = (
        [(r, 1.0) for r in context.liked_recipes] +
        [(r, -1.0) for r in context.disliked_recipes] +
        [(r, -0.1) for r in context.maybe_later_recipes]
    )

    if not all_recipes:
        # Nothing to update
        return context

    # Compute weighted sum of embeddings
    weighted_embeddings = []
    total_weight = 0.0
    # Assign different weights for title vs. tags

    for recipe, weight in all_recipes:
        # We could use tags + title for embedding
        title_embedding = get_embedding(recipe.title)
        tag_embeddings = [get_embedding(tag) for tag in recipe.tags]
        title_weight = 0.2
        tag_weight = 0.8 / len(tag_embeddings) if tag_embeddings else 0.0
        weighted_emb = title_embedding * title_weight
        for t_emb in tag_embeddings:
            weighted_emb += t_emb * tag_weight
        weighted_embeddings.append(emb * weight)
        total_weight += abs(weight)

    if weighted_embeddings:
        # Weighted average
        preference_vector = np.sum(weighted_embeddings, axis=0) / total_weight
        alpha = 0.5  # learning rate
        context.preference_vector = alpha * new_vector + (1 - alpha) * np.array(context.preference_vector or 0)
        context.preference_vector = preference_vector.tolist()

    return context
=======
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
>>>>>>> backend


# -----------------------
# STEP 4: Compute Grocery List
# -----------------------

<<<<<<< HEAD
def compute_grocery_items(selected_recipes: List[RecipeLink]) -> List[GroceryItem]:
    """Compute grocery list and macros for selected recipes."""
    # Placeholder: In reality, you'd scrape ingredients and estimate macros per ingredient
    dummy_macros = Macros(calories=100, protein=5, carbs=10, fat=2)
    grocery_items = [
        GroceryItem(name="Chicken Breast", quantity="500g", macros=dummy_macros, price=5.99),
        GroceryItem(name="Broccoli", quantity="300g", macros=dummy_macros, price=2.49),
    ]
    return grocery_items
=======
# def compute_grocery_items(selected_recipes: List[RecipeLink]) -> List[GroceryItem]:
#     """Compute grocery list and macros for selected recipes."""
#     # Placeholder: In reality, you'd scrape ingredients and estimate macros per ingredient
#     dummy_macros = Macros(calories=100, protein=5, carbs=10, fat=2)
#     grocery_items = [
#         GroceryItem(name="Chicken Breast", quantity="500g", macros=dummy_macros, price=5.99),
#         GroceryItem(name="Broccoli", quantity="300g", macros=dummy_macros, price=2.49),
#     ]
#     return grocery_items
>>>>>>> backend


# -----------------------
# STEP 5: Pipeline Orchestration
# -----------------------

<<<<<<< HEAD
def run_pipeline():
    # Example user setup
    user_context = RecipeSelectionContext(
        user_id="u123",
        macros=Macros(calories=2000, protein=150, carbs=200, fat=60),
        goals={"goal": "gain_muscle", "diet": "balanced"}
    )

    # Generate ideas
    ideas = generate_recipe_ideas(user_context)
    print("Generated Ideas:", [i.title for i in ideas])

    # Find web links
    links = find_recipe_links(ideas)
    print("Found Links:", [l.url for l in links])

    # Simulate user liking 3 recipes
    user_context.liked_recipes = links[:3]
    user_context = update_user_preferences(user_context)

    # Compute grocery list
    groceries = compute_grocery_items(user_context.liked_recipes)
    print("Grocery List:", [g.name for g in groceries])

    return groceries


if __name__ == "__main__":
    groceries = run_pipeline()
=======
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
>>>>>>> backend
    print("Pipeline completed.")