# IMPORTS
import requests
import json
from requests_futures.sessions import FuturesSession
import requests_futures
from concurrent.futures import ThreadPoolExecutor
from skillbook_class import create_Skillbook
from url_class import create_url
import time
from tqdm import *

__author__ = 'Laurent Dumont'

session = FuturesSession(executor=ThreadPoolExecutor(max_workers=100))
price_list_jita = []
price_list_itamo = []
crest_url_list = []
sell_orders_list = []
skillbook_list = []

#
def RateLimited(maxPerSecond):
    minInterval = 1.0 / float(maxPerSecond)
    def decorate(func):
        lastTimeCalled = [0.0]
        def rateLimitedFunction(*args,**kargs):
            elapsed = time.clock() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait>0:
                time.sleep(leftToWait)
            ret = func(*args,**kargs)
            lastTimeCalled[0] = time.clock()
            return ret
        return rateLimitedFunction
    return decorate

def get_typeID_skillbooks():

    print "Reading the file for the typeID"
    with open("eve-skills-typeID.txt") as file:
        typeID = [line.rstrip('\n') for line in file]
    print "Finished reading the file - Returning a LIST with all the typeID"
    return typeID

def get_sell_order_crest(typeID):

    def make_api_call(crest_url_list):

        @RateLimited(150)
        def get_data(session,url):
            try:
                response = session.get(url)
                return response
            except requests.ConnectionError:
                print "Connection Aborted - BadStatusLine"


        print "Sending the requests"
        session = FuturesSession(max_workers=10)
        futures = []

        for url in tqdm(crest_url_list, desc="Downloading", leave=True):
            futures.append(get_data(session, url))

    # Static variables
    market_region = "10000002"
    market_order_type = "sell"

    # Create the list of all the urls to query with the correct typeID, region typeID and Sell or Buy Order type
    print "Creating the LIST with the CREST url"
    for skill_typeID in typeID:
        current_typeID = skill_typeID
        crest_url_list.append("https://public-crest.eveonline.com/market/" + market_region + "/orders/" + market_order_type + "/?type=https://public-crest.eveonline.com/types/" + current_typeID + "/")

    make_api_call(crest_url_list)
    return sell_orders_list


def sort_sell_order_prices(sell_orders_list):

    #If the JSON string is invalid, remove from the array and break
    for sell_order in sell_orders_list[:]:
        if sell_order["totalCount_str"] == "0":
            sell_orders_list.remove(sell_order)
            continue
    #Iterate through the Sell Orders list
    for sell_order in sell_orders_list[:]:
        try:
            skillbook_name = sell_order["items"][0]["type"]["name"]
        except IndexError:
            sell_orders_list.remove(sell_order)
            continue
        #Iterate through the items to check the location
        price_list_itamo = []
        price_list_jita = []
        for sellOrder in sell_order["items"][:]:

            if sellOrder["location"]["name"] == "Jita IV - Moon 4 - Caldari Navy Assembly Plant":
                price_list_jita.append(sellOrder["price"])

            if sellOrder["location"]["name"] == "Itamo VI - Moon 6 - Science and Trade Institute School":
                price_list_itamo.append(sellOrder["price"])

        # Calculate price for the item
        try:
            item_profit = min(price_list_jita) - min(price_list_itamo)
        except ValueError:
            continue

        skillbook_list.append(create_Skillbook(item_profit,skillbook_name,min(price_list_jita),min(price_list_itamo)))

    return skillbook_list


def print_result(skillbook_list):

    file = open("skillbook_profit.txt", 'w')
    total = "Total number of valid skillbooks : %i \n" % skillbook_list .__len__()
    separator = "-------------------------------\n"
    file.write(total)
    skillbook_list = sorted(skillbook_list, key=lambda skillbook: skillbook.profit, reverse=True)

    for skillbook in skillbook_list[:]:
        comma_price_itamo = "ISK {:,.2f}".format(skillbook.price_itamo)
        comma_price_jita = "ISK {:,.2f}".format(skillbook.price_jita)
        comma_item_profit = "ISK {:,.2f}".format(skillbook.profit)
        profit_line = "%s - Profit : %s \nItamo Cost : %s \nJita Cost %s \n" %( skillbook.name, comma_item_profit, comma_price_itamo,comma_price_jita )
        file.write(profit_line)
        file.write(separator)

def main():
        print_result(sort_sell_order_prices(get_sell_order_crest(get_typeID_skillbooks())))

if __name__ == "__main__":
    main()