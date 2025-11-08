"""
recipe_agent_pipeline.py
Boilerplate for an AI Recipe Generation Pipeline using OpenAI models and web search
"""
import numpy as np
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import json
import openai
import requests
from dataclasses import dataclass

from models import Macros


# -----------------------
# STEP 0: Define Models
# -----------------------

client = OpenAI(
    api_key = "sk-FAyzaUaK8JlUzvrmIU2XlA",
    base_url = "https://fj7qg3jbr3.execute-api.eu-west-1.amazonaws.com/v1/chat/completions"
)

def get_embedding(text: str) -> np.ndarray:
    """Compute embedding for a given text using OpenAI embeddings."""
    resp = client.embeddings.create(
        model="text-embedding-3-large",
        input=text
    )
    return np.array(resp.data[0].embedding)

# -----------------------
# STEP 1: Recipe Idea Generation
# -----------------------

def generate_recipe_ideas(context: RecipeSelectionContext, n_ideas: int = 5) -> List[RecipeIdea] | None:
    """Use OpenAI model to generate structured recipe ideas given user macros and goals"""
    prompt = f"""
    Think of {n_ideas} creative, healthy recipe ideas for someone who wants to {context.goals.get('goal')}
    with these daily macros:
    Calories: {context.macros.calories}, Protein: {context.macros.protein}g,
    Carbs: {context.macros.carbs}g, Fat: {context.macros.fat}g.
    Fill the tags field with relevant descriptors on cuisine type, flavor profile, key condiments, ... (at most 6-7)
    """
    response = client.responses.parse(
        model="gpt-5",
        input=[
            {"role": "system", "content": "Your name is Sarah Brown. You are an expert nutritionist and recipe planning assistant."},
            {
                "role": "user",
                "content": prompt,
            },
        ],
        text_format=List[RecipeIdea],
    )

    return response.output_parsed

# -----------------------
# STEP 2: Find Recipe Links (Web Search)
# -----------------------

def find_recipe_links(ideas: List[RecipeIdea]) -> List[List[RecipeLink]]:
    """
    Uses OpenAI web_search tool to find recipes biased toward highly rated and widely reviewed recipes.
    """
    results: List[List[RecipeLink]] = []

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
            text_format=List[RecipeLink],
        )

        results.append(links_associated_with_this_idea.output_parsed)

    return results


# -----------------------
# STEP 3: Update User Preferences (Learning/Adaptation)
# -----------------------

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


# -----------------------
# STEP 4: Compute Grocery List
# -----------------------

def compute_grocery_items(selected_recipes: List[RecipeLink]) -> List[GroceryItem]:
    """Compute grocery list and macros for selected recipes."""
    # Placeholder: In reality, you'd scrape ingredients and estimate macros per ingredient
    dummy_macros = Macros(calories=100, protein=5, carbs=10, fat=2)
    grocery_items = [
        GroceryItem(name="Chicken Breast", quantity="500g", macros=dummy_macros, price=5.99),
        GroceryItem(name="Broccoli", quantity="300g", macros=dummy_macros, price=2.49),
    ]
    return grocery_items


# -----------------------
# STEP 5: Pipeline Orchestration
# -----------------------

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
    print("Pipeline completed.")