# IMPORTS
import requests
from requests_futures.sessions import FuturesSession
from concurrent.futures import ThreadPoolExecutor
from progressbar import ProgressBar
import json
from skillbook_class import create_Skillbook
import os

__author__ = 'Laurent Dumont'

session = FuturesSession(executor=ThreadPoolExecutor(max_workers=10))
price_list_jita = []
price_list_itamo = []
crest_url_list = []
sell_orders_list = []
pbar = ProgressBar()
skillbook_list = []

def get_typeID_skillbooks():

    print "Reading the file for the typeID"
    with open("eve-skills-typeID.txt") as file:
        typeID = [line.rstrip('\n') for line in file]
    print "Finished reading the file - Returning a LIST with all the typeID"
    return typeID

def get_sell_order_crest(typeID):

    def make_api_call(crest_url_list):
        print "Sending the requests"
        session = FuturesSession()
        session.mount("http://", requests.adapters.HTTPAdapter(max_retries=3))
        session.mount("https://", requests.adapters.HTTPAdapter(max_retries=3))
        for url in crest_url_list:
            try:
                print "Sending query..."
                json_market_data = session.get(url)
                temp = json_market_data.result()
                sell_orders_list.append(json.loads(temp.content))
            except requests.ConnectionError:
                print "Connection Aborted - BadStatusLine"

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
    total = "Total number of valid skillbooks : %i \n" % skillbook_list.__len__()
    separator = "-------------------------------\n"
    file.write(total)
    skillbook_list = sorted(skillbook_list, key=lambda skillbook: skillbook.profit, reverse=True)
    for skillbook in skillbook_list[:]:
        comma_price_itamo = "ISK {:,.2f}".format(skillbook.price_itamo)
        comma_price_jita = "ISK {:,.2f}".format(skillbook.price_jita)
        comma_item_profit = "ISK {:,.2f}".format(skillbook.profit)
        profit_line = "%s - Profit : %s Itamo Cost : %s | Jita Cost %s \n" %( skillbook.name, comma_item_profit, comma_price_itamo,comma_price_jita )
        file.write(profit_line)
        file.write(separator)

def main():
        print_result(sort_sell_order_prices(get_sell_order_crest(get_typeID_skillbooks())))

if __name__ == "__main__":
    main()