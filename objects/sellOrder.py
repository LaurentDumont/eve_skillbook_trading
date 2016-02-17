class SellOrder:
    data = ""
    region = ""

    def __init__(self, data, region):
        self.data = data
        self.region = region


def create_SellOrder(data, region):

    sellorder = SellOrder(data, region)
    return sellorder