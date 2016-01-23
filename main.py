__author__ = 'DTKT'

#IMPORTS
import requests
from sys import argv
from time import sleep

pricelistJita = []
pricelistItamo = []


def get_typeID_skillbooks():
    with open("eve-skills-typeID.txt") as file:
        typeID = [line.rstrip('\n') for line in file]
    return typeID

def get_sell_order_crest(typeID):

    market_region = 10000002
    market_order_type = sell
    for skill_typeID in typeID:
        current_typeID = skill_typeID
        print current_typeID
        json_market_data = requests.get("https://public-crest.eveonline.com/market/"+market_region+"/orders/"+market_order_type+"/?type=https://public-crest.eveonline.com/types/"+current_typeID+"/")
        sleep(1) # Sleep time in seconds to not get fucked over by CREST API rate limits.
        parsed_jason_market_data = json_market_data.json()
        # return parsed_jason_market_data


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


    print "Here is the price list in Jita : %s" %min(pricelistJita)
    print "Here is the price list in Itamo : %s"  %min(pricelistItamo)

    #Calculate price for the item
    item_profit = min(pricelistJita) - min(pricelistItamo)
    comma_item_profit = "ISK {:,.2f}".format(item_profit)
    print "Here is the profit per skillbook for : %s - %s" %(skillbook_name,comma_item_profit)
    #print ("Total cost is: ISK {:,.2f}".format(item_profit))

def main():
    #sort_sell_order_prices( get_sell_order_crest())
    get_sell_order_crest(get_typeID_skillbooks())

if __name__ == "__main__":
    main()