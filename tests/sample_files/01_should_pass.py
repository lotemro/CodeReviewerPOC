def calculate_total_price(item_price: float, quantity: int, tax_rate: float) -> float:
    """
    Calculates the total price of an item including tax.
    """
    subtotal = item_price * quantity
    total_tax = subtotal * tax_rate
    return subtotal + total_tax

class ShoppingCart:
    def __init__(self):
        self.items = []

    def add_item(self, item_name: str, price: float):
        """Adds an item with its price to the cart."""
        self.items.append({"name": item_name, "price": price})
