class Player:
    def __init__(self):
        self.health = 100
        self.max_health = 100
        self.inventory = []

    def get_status(self):
        inv = ', '.join(self.inventory) if self.inventory else 'Nothing'
        return f"Health: {self.health}/{self.max_health} | Inventory: {inv}"

    def add_item(self, item):
        if item not in self.inventory:
            self.inventory.append(item)

    def remove_item(self, item):
        if item in self.inventory:
            self.inventory.remove(item)

    def has_item(self, item):
        return item in self.inventory

    def change_health(self, amount):
        self.health = max(0, min(self.max_health, self.health + amount))
