# AI-House-2025-Hackaton-MacrosAI


## Future Improvements

This is a list of ideas we envisioned for our product, which would complete the functionality of the agent.

## More customizability

The user should be able to provide a multitude of goals and diets, perhaps even detailed body composition.

## Connecting APIs

We still need to connect to real-world supermarkets to make requests for food. This could be used to inform the agent on typical stocks and prices instead of relying on estimations to provide data. We'd also need to include a form of location retrieval to inform the agent where to search for supermarkets / restaurants (future extension).

### Fine-tuning the Recommender System

The recommender system, which improves the subsequent recipes that the agent suggests, is currently implemented on a conceptual level.
To actually measure its effects, fine-tune the parameters that influence the learning procedures (alphas for recipe titles and tags), and potentially explore additional feature vectors for this recommendation, we'd need to run further experiments.

### Extending to Restaurant Deliveries

The user should be able to communicate to the agent that they want a food delivery instead of cooking. The complete agent should provide all food services, ensuring a self-contained experiment. We've written a boilerplate backend implementation, though we have not connected this to a front-end. 

- The look and feel of the delivery interaction would be the same as with the recipes: the agent prompts users with delivery ideas, and the user selects one. The agent then automatically makes the order, or allows the user to add specifications (wanting something additional from the store, etc.) => API integration would be useful here to automate menu retrieval.
- The feature vectors containing extracted data from the interactions with the recipe generator could be reused here to let the agent read the user's preferences
- We would build a parallel recommender system for the deliveries themselves

### Agent inferring user patterns

The agent should be equipped with more tools to infer user preferences
- Periodically, the agent should check the stored context vectors for the user and notify based on threshold values.
- These could be temporal (the user typically orders takeout on Fridays => prompt the user with a notification on Friday) or simply based on common behavior at different points in the app (if the user adds certain items to the grocery list frequently, automatically suggest them)
- If usage activity dips, provide incentives via notifications (include a scan for sales by different food provi
