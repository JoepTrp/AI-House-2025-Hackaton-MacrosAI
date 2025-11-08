from dataclasses import dataclass

@dataclass
class GroceryItem:
    id: int
    item_name: str
    category: str
    price: float
    macros: str
    days_to_expire: int

    def is_expiring_soon(self, threshold=3):
        """Check if the item will expire within a given number of days."""
        return self.days_to_expire <= threshold

    def __repr__(self):
        return f"<GroceryItem {self.item_name} (${self.price}), {self.days_to_expire}d to expire>"
