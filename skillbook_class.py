class Skillbook:
    profit = 0
    name = ""
    price_jita = 0
    price_itamo = 0

    def __init__(self, profit, name, price_jita, price_itamo):
        self.profit = profit
        self.name = name
        self.price_jita = price_jita
        self.price_itamo = price_itamo

def create_Skillbook(profit, name, price_jita, price_itamo):

    skillbook = Skillbook(profit, name, price_jita, price_itamo)
    return skillbook