import json
from grocery_item import GroceryItem

class GroceryList:
    def __init__(self, items=None):
        self.items = items or []

    @classmethod
    def from_json(cls, file_path):
        """Create a GroceryList from a JSON file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        items = [GroceryItem(**item) for item in data]
        return cls(items)

    def get_by_id(self, item_id):
        return next((item for item in self.items if item.id == item_id), None)

    def filter_by_category(self, category):
        return [item for item in self.items if item.category.lower() == category.lower()]

    def total_cost(self):
        return sum(item.price for item in self.items)

    def __repr__(self):
        return f"<GroceryList ({len(self.items)} items)>"
