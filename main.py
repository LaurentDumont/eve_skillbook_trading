__author__ = 'DTKT'

#IMPORTS
import requests

pricelistJita = []
pricelistItamo = []

def get_sell_order_crest():
    json_market_data = requests.get("https://public-crest.eveonline.com/market/10000002/orders/sell/?type=https://public-crest.eveonline.com/types/3307/")
    parsed_jason_market_data = json_market_data.json()
    return parsed_jason_market_data


def sort_sell_order_prices(parsed_jason_market_data):

    skillbook_name = parsed_jason_market_data["items"][0]["type"]["name"]
    for sellOrder in parsed_jason_market_data["items"]:
        if sellOrder["location"]["name"] == "Jita IV - Moon 4 - Caldari Navy Assembly Plant":
                pricelistJita.append(sellOrder["price"])
                pricelistJita.sort()

        else:
           if sellOrder["location"]["name"] == "Itamo VI - Moon 6 - Science and Trade Institute School":
                pricelistItamo.append(sellOrder["price"])
                pricelistItamo.sort()


    print "Here is the price list in Jita"
    print min(pricelistJita)
    print "Here is the price list in Itamo"
    print max(pricelistItamo)

    #Calculate price for the item
    item_profit = min(pricelistJita) - min(pricelistItamo)
    comma_item_profit = "ISK {:,.2f}".format(item_profit)
    print "Here is the profit per skillbook for : %s - %s" %(skillbook_name,comma_item_profit)
    #print ("Total cost is: ISK {:,.2f}".format(item_profit))

def main():
    sort_sell_order_prices( get_sell_order_crest())

if __name__ == "__main__":
    main()