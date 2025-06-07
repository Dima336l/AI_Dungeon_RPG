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

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)

    def heal(self, amount):
        self.health = min(100, self.health + amount)

    def get_status(self):
        inv = ', '.join(self.inventory) if self.inventory else 'Nothing'
        return f"Health: {self.health}/100 | Inventory: {inv}"
