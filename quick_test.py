from urllib.parse import urlparse

from openai import OpenAI

from models import RecipeLink

client = OpenAI(
    api_key = "sk-FAyzaUaK8JlUzvrmIU2XlA",
    base_url = "https://fj7qg3jbr3.execute-api.eu-west-1.amazonaws.com/v1"
)

recipe_link_1 = RecipeLink(title="One Pot Cajun Chicken and Rice",
                         url="www.lecremedelacrumb.com",
                         source="Creme de la Crumb")



selected_recipes = [recipe_link_1]

allowed_domains = [
        urlparse(recipe.url).netloc for recipe in selected_recipes
    ]


response = client.responses.create(
        model="gpt-5-nano",
        tools=[
            {
                "type": "web_search",
                "filters": {
                    "allowed_domains": ["www.lecremedelacrumb.com"]
                },
            }
        ],
        tool_choice="auto",
        include=["web_search_call.action.sources"],
        input="Search for a One Pot Cajun Chicken and Rice recipe on this site and summarize the ingredients."
    )

print(response.output_text)