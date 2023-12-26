import random


class Components:
    def __init__(self, quantity, price):
        self.isin = "XS123" + str(random.randint(1, 100))
        self.quantity = quantity
        self.price = price

