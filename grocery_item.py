class GroceryItem:
    def __init__(self, id, item_name, category, price, macros):
        self.id = id
        self.item_name = item_name
        self.category = category
        self.price = price
        self.macros = macros

    def __repr__(self):
        return f"<GroceryItem {self.item_name} (${self.price})>"