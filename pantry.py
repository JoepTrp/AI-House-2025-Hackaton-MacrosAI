from grocery_item import GroceryItem

class Pantry:
    def __init__(self):
        self.items = []

    def add_item(self, item: GroceryItem):
        """Add a grocery item to the pantry."""
        self.items.append(item)

    def remove_item(self, item: GroceryItem):
        """Remove a specific item from the pantry."""
        if item in self.items:
            self.items.remove(item)

    def expiring_soon(self, threshold=3):
        """Return items that will expire within `threshold` days."""
        return [item for item in self.items if item.days_to_expire <= threshold]

    def remove_expired(self):
        """Remove all items that have expired (days_to_expire <= 0)."""
        self.items = [item for item in self.items if item.days_to_expire > 0]

    def list_items(self):
        """Return a list of all items in the pantry."""
        return self.items

    def __repr__(self):
        return f"<Pantry ({len(self.items)} items)>"
