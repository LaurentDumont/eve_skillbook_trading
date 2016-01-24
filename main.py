# IMPORTS
import requests
from time import sleep
from requests_futures.sessions import FuturesSession
from concurrent.futures import ThreadPoolExecutor
from progressbar import ProgressBar
from requests import Session
import json

__author__ = 'Laurent Dumont'

price_list_jita = []
price_list_itamo = []
crest_url_list = []
sell_orders_list = []
pbar = ProgressBar()
skillbook = []

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

def get_typeID_skillbooks():
    print "Reading the file for the typeID"
    with open("eve-skills-typeID.txt") as file:
        typeID = [line.rstrip('\n') for line in file]
    print "Finished reading the file - Returning a LIST with all the typeID"
    return typeID

def get_sell_order_crest(typeID):

    # Static variables
    market_region = "10000002"
    market_order_type = "sell"

    # Create the list of all the urls to query with the correct typeID, region typeID and Sell or Buy Order type
    print "Creating the LIST with the CREST url"
    for skill_typeID in typeID:
        current_typeID = skill_typeID
        crest_url_list.append("https://public-crest.eveonline.com/market/" + market_region + "/orders/" + market_order_type + "/?type=https://public-crest.eveonline.com/types/" + current_typeID + "/")
    #print '\n'.join(str(p) for p in crest_url_list)

    print "Sending the requests"
    session = FuturesSession()
    for url in crest_url_list:
        try:
            json_market_data = session.get(url)
            print "Sending query..."
            temp = json_market_data.result()
            sell_orders_list.append(json.loads(temp.content))
        except requests.ConnectionError:
            print "Failed to connect to the EVE Crest"
    return sell_orders_list

    # For each URL, get the json response
    # session = FuturesSession()
    # print "Sending the URL to CREST"
    # for url in (crest_url_list):
    #     response = session.get(url)
    #     sleep(0.5)
    #     unparsed_sell_orders = response.result()
    #     sell_orders_list.append(unparsed_sell_orders.json())
    # for sell_order in enumerate(sell_orders_list):
    #     print sell_order
    # return sell_orders_list

    #print unparsed_sell_orders.status_code
    #print response.result
    #for json_data in crest_url_list = json_market_data.json()
    #return parsed_jason_market_data


def sort_sell_order_prices(sell_orders_list):
    #print '\n'.join(str(p) for p in sell_orders_list)
    #If the JSON string is invalid, remove from the array and break
    for sell_order in sell_orders_list[:]:
        if sell_order["totalCount_str"] == "0":
            #print "Removing empty response"
            #print sell_order
            sell_orders_list.remove(sell_order)
            continue
    #Iterate through the Sell Orders list
    #print '\n'.join(str(p) for p in sell_orders_list)
    for sell_order in sell_orders_list[:]:
        try:
            skillbook_name = sell_order["items"][0]["type"]["name"]
        except IndexError:
            #print "Cannot find the name - Probably an empty response"
            #print sell_order
            sell_orders_list.remove(sell_order)
            continue
        #Iterate through the items to check the location
        for sellOrder in sell_order["items"][:]:

            if sellOrder["location"]["name"] == "Jita IV - Moon 4 - Caldari Navy Assembly Plant":
                price_list_jita.append(sellOrder["price"])
                #price_jita = sellOrder["price"]
            # else:
            #     price_jita = 0

            if sellOrder["location"]["name"] == "Itamo VI - Moon 6 - Science and Trade Institute School":
                price_list_itamo.append(sellOrder["price"])
                #price_itamo = sellOrder["price"]
            # else:
            #     price_itamo = 0

        # print "Here is the price list in Jita : %s" %min(price_list_jita)
        # print "Here is the price list in Itamo : %s"  %min(price_list_itamo)
        # print "----------------------------"
        # print "Here is the price list in Jita : %s" %price_jita
        # print "Here is the price list in Itamo : %s"  %price_itamo

        # Calculate price for the item
        try:
            item_profit = min(price_list_jita) - min(price_list_itamo)
        except ValueError:
            continue
        comma_item_profit = "ISK {:,.2f}".format(item_profit)
        #skillbook.append(create_Skillbook(item_profit,skillbook_name,price_jita,price_itamo))
        print "Profit per skillbook for : %s - %s - Price in Itamo %s" %(skillbook_name,comma_item_profit,min(price_list_itamo))
        price_list_itamo[:] = []
        price_list_jita[:] = []

def print_result(skillbook_list):
    for skillbook in skillbook_list:
        print skillbook.profit


def main():
    sort_sell_order_prices(get_sell_order_crest(get_typeID_skillbooks()))

if __name__ == "__main__":
    main()