# IMPORTS
import time

import requests
from objects.region_class import Region
from objects.skillbook_class import Skillbook
from objects.url import url
from objects.sellOrder import SellOrder
from concurrent.futures import ThreadPoolExecutor
from requests_futures.sessions import FuturesSession
from tqdm import *

__author__ = 'Laurent Dumont'

session = FuturesSession(executor=ThreadPoolExecutor(max_workers=100))
price_list_jita = []
price_list_itamo = []
crest_url_list = []
sell_orders_list = []
skillbook_list = []

#Decorator
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

#Get TYPEID from textfile
def get_typeID_skillbooks():

    with open("eve-skills-typeID.txt") as file:
        typeID = [line.rstrip('\n') for line in file]
    return typeID

def get_sell_order_crest(typeID):

    def make_api_call(crest_url_list):

        @RateLimited(150)
        def get_data(session,url):
            try:
                response = session.get(url.full_url)
                return response

            except requests.ConnectionError:
                print "Connection Aborted - BadStatusLine"

        session = FuturesSession(max_workers=10)
        futures = []
        res = []

        for url in tqdm(crest_url_list, desc="Downloading", leave=True):
            futures.append(get_data(session, url))

        for request in tqdm(futures,desc="Completing Requests"):
            res.append(request.result())
        print res.__len__()
        for x in res:
            print x.content

    # Create the list of all the urls to query with the correct typeID, region typeID and Sell or Buy Order type
    market_region_id = {Region("10000002","jita"),Region("10000030","rens"),Region("10000032","dodixie"),Region("10000043","amarr"),Region("10000042","hek")}
    #market_region_id = {Region("10000002","jita")}
    market_order_type = "sell"

    # Create the list of all the urls to query with the correct typeID, region typeID and Sell or Buy Order type
    for skill_typeID in typeID:
        for region in market_region_id:
            current_typeID = skill_typeID
            crest_url_list.append(url(
                "https://public-crest.eveonline.com/market/" + region.typeID + "/orders/" + market_order_type + "/?type=https://public-crest.eveonline.com/types/" + current_typeID + "/",
                region.name))

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

        skillbook_list.append(Skillbook(item_profit,skillbook_name,min(price_list_jita),min(price_list_itamo)))

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