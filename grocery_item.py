from dataclasses import dataclass

@dataclass
class GroceryItem:
    id: int
    item_name: str
    category: str
    price: float
    macros: str
