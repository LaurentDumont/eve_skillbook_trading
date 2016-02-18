class Skillbook:
    profit = 0
    name = ""
    price_trade = 0
    price_npc = 0
    region = ""

    def __init__(self, profit, name, price_trade, price_npc, region):
        self.profit = profit
        self.name = name
        self.price_trade = price_trade
        self.price_npc = price_npc
        self.region = region