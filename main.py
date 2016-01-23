__author__ = 'Laurent Dumont'

#IMPORTS
import requests
import grequests
from sys import argv
from time import sleep
from requests_futures.sessions import FuturesSession
from concurrent.futures import ThreadPoolExecutor

price_list_jita = []
price_list_itamo = []
crest_url_list = []
sell_orders_list = []
session = FuturesSession(executor=ThreadPoolExecutor(max_workers=50))

def get_typeID_skillbooks():
    with open("eve-skills-typeID.txt") as file:
        typeID = [line.rstrip('\n') for line in file]
    return typeID

def get_sell_order_crest(typeID):

    # Static variables
    market_region = "10000002"
    market_order_type = "sell"

    # Create the list of all the urls to query with the correct typeID, region typeID and Sell or Buy Order type
    for skill_typeID in typeID:
        current_typeID = skill_typeID
        #print current_typeID
        #json_market_data = requests.get("https://public-crest.eveonline.com/market/"+market_region+"/orders/"+market_order_type+"/?type=https://public-crest.eveonline.com/types/"+current_typeID+"/")
        #sleep(1) # Sleep time in seconds to not get fucked over by CREST API rate limits.
        crest_url_list.append("https://public-crest.eveonline.com/market/" + market_region + "/orders/" + market_order_type + "/?type=https://public-crest.eveonline.com/types/" + current_typeID + "/")

    # For each URL, get the json response
    session = FuturesSession()
    for url in crest_url_list:
        response = session.get(url)
        sleep(0.5)
        unparsed_sell_orders = response.result()
        sell_orders_list.append(unparsed_sell_orders.json())

    # for url in crest_url_list:
    #     json_market_data = grequests.get(url)
    #     json_response_list.append(json_market_data.json())
    # print json_response_list[:]
    #
    # rs = (grequests.get(u) for u in crest_url_list)
    # results = grequests.map(rs)
    # print results


        #for json_data in crest_url_list = json_market_data.json()
        #return parsed_jason_market_data


def sort_sell_order_prices(parsed_jason_market_data):

    skillbook_name = parsed_jason_market_data["items"][0]["type"]["name"]
    for sellOrder in parsed_jason_market_data["items"]:
        if sellOrder["location"]["name"] == "Jita IV - Moon 4 - Caldari Navy Assembly Plant":
                price_list_jita.append(sellOrder["price"])
                price_list_jita.sort()

        else:
           if sellOrder["location"]["name"] == "Itamo VI - Moon 6 - Science and Trade Institute School":
                price_list_itamo.append(sellOrder["price"])
                price_list_itamo.sort()


    print "Here is the price list in Jita : %s" %min(price_list_jita)
    print "Here is the price list in Itamo : %s"  %min(price_list_itamo)

    #Calculate price for the item
    item_profit = min(price_list_jita) - min(price_list_itamo)
    comma_item_profit = "ISK {:,.2f}".format(item_profit)
    print "Here is the profit per skillbook for : %s - %s" %(skillbook_name,comma_item_profit)
    #print ("Total cost is: ISK {:,.2f}".format(item_profit))

def main():
    #sort_sell_order_prices( get_sell_order_crest())
    get_sell_order_crest(get_typeID_skillbooks())

if __name__ == "__main__":
    main()