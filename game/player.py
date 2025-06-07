class Player:
    def __init__(self):
        self.health = 100
        self.inventory = []

    def add_item(self, item):
        self.inventory.append(item)

    def remove_item(self, item):
        if item in self.inventory:
            self.inventory.remove(item)

    def has_item(self, item):
        return item in self.inventory

    def __str__(self):
        inv = ', '.join(self.inventory) if self.inventory else 'Nothing'
        return f"Health: {self.health}/100 | Inventory: {inv}"
