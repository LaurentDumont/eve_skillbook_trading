# IMPORTS
import time

import requests
from objects.region import Region
from objects.skillbook import Skillbook
from objects.url import url
from objects.sellOrder import SellOrder
from concurrent.futures import ThreadPoolExecutor
from requests_futures.sessions import FuturesSession
from tqdm import *
import json
import openpyxl

__author__ = 'Laurent Dumont'

session = FuturesSession(executor=ThreadPoolExecutor(max_workers=10))
price_list_npc = []
price_list_trade = []
crest_url_list = []
sell_orders_list = []
skillbook_list = []
futures = []
res = []


# Decorator
def RateLimited(maxPerSecond):
    minInterval = 1.0 / float(maxPerSecond)

    def decorate(func):
        lastTimeCalled = [0.0]

        def rateLimitedFunction(*args, **kargs):
            elapsed = time.clock() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait > 0:
                time.sleep(leftToWait)
            ret = func(*args, **kargs)
            lastTimeCalled[0] = time.clock()
            return ret

        return rateLimitedFunction

    return decorate


# Get TYPEID from textfile
def get_typeID_skillbooks():
    with open("eve-skills-typeID.txt") as file:
        typeID = [line.rstrip('\n') for line in file]
    return typeID


def get_sell_order_crest(typeID):
    def make_api_call(crest_url_list):

        @RateLimited(150)
        def get_data(session, url):
            try:
                response = session.get(url.full_url)
                return response

            except requests.ConnectionError:
                print "Connection Aborted - BadStatusLine"

        session = FuturesSession(max_workers=10)

        for url in tqdm(crest_url_list, desc="Downloading", leave=False):
            # futures.append(get_data(session, url))
            futures.append(SellOrder(get_data(session, url), url.region))

        for request in tqdm(futures, desc="Completing Requests", leave=False):
            # res.append(request.result())
            res.append(SellOrder(request.data.result(), request.region))

        for x in res:
            # sell_orders_list.append(json.loads(x.content))
            sell_orders_list.append(SellOrder(json.loads(x.data.content), x.region))

        return sell_orders_list

    # Create the list of all the urls to query with the correct typeID, region typeID and Sell or Buy Order type
    # market_region_id = {Region("10000002", "jita")}
    market_region_id = {Region("10000002", "jita"), Region("10000030", "rens"), Region("10000032", "dodixie"),
                        Region("10000043", "amarr"), Region("10000042", "hek")}
    market_order_type = "sell"

    # Create the list of all the urls to query with the correct typeID, region typeID and Sell or Buy Order type
    for skill_typeID in typeID:
        for region in market_region_id:
            current_typeID = skill_typeID
            crest_url_list.append(url(
                "https://public-crest.eveonline.com/market/" + region.typeID + "/orders/" + market_order_type + "/?type=https://public-crest.eveonline.com/types/" + current_typeID + "/",
                region.name))

    return make_api_call(crest_url_list)


def sort_sell_order_prices(sell_orders_list):
    # If the JSON string is invalid, remove from the array and break.

    def clean_sell_orders(sell_orders_list):

        for sell_order in sell_orders_list[:]:
            if sell_order.data["totalCount_str"] == "0":
                sell_orders_list.remove(sell_order)
                continue
        return sell_orders_list

    def calculate_profit(sell_order, npc, trade):

        global skillbook_name
        global item_profit
        item_profit = 0
        # print sell_order.region
        try:
            skillbook_name = sell_order.data["items"][0]["type"]["name"]
            # print skillbook_name
        except IndexError:
            sell_orders_list.remove(sell_order)
            # print skillbook_name

        # Iterate through the items to check the location.
        for sellOrder in sell_order.data["items"][:]:
            price_list_npc = []
            price_list_trade = []
            # print sellOrder["location"]["name"]
            # print sellOrder["price"]
            # print trade
            # print npc
            # print sellOrder
            if sellOrder["location"]["name"] == trade:
                print "trade"
                price_list_trade.append(sellOrder["price"])

            if sellOrder["location"]["name"] == npc:
                print "npc"
                price_list_npc.append(sellOrder["price"])

            # print price_list_npc.__len__()
            # print price_list_trade.__len__()
            try:
                item_profit = min(price_list_trade) - min(price_list_npc)
            except:
                pass

            skillbook_list.append(
                Skillbook(item_profit, skillbook_name, min(price_list_trade), min(price_list_npc), sell_order.region))
        print skillbook_list.__len__()
        return skillbook_list

    def process_sell_orders(sell_orders_list):
        amarr_trade = "Amarr VIII (Oris) - Emperor Family Academy"
        amarr_npc = "Sarum Prime III - Moon 2 - Imperial Academy"
        rens_trade = "Rens VI - Moon 8 - Brutor Tribe Treasury"
        rens_npc = "Hulm VIII - Moon 2 - Republic University"
        dodixie_trade = "Dodixie IX - Moon 20 - Federation Navy Assembly Plant"
        dodixie_npc = "Bourynes VII - Moon 2 - University of Caille"
        hek_trade = "Hek VIII - Moon 12 - Boundless Creation Factory"
        hek_npc = "Olbra I - Pator Tech School"
        jita_trade = "Jita IV - Moon 4 - Caldari Navy Assembly Plant"
        jita_npc = "Itamo VI - Moon 6 - Science and Trade Institute School"

        for sell_order in sell_orders_list[:]:
            if sell_order.region == "jita":
                # calculate_profit(sell_order, jita_npc, jita_trade)
                try:
                    skillbook_name = sell_order.data["items"][0]["type"]["name"]
                except IndexError:
                    sell_orders_list.remove(sell_order)
                    continue
                # Iterate through the items to check the location
                price_list_npc = []
                price_list_trade = []
                for sellOrder in sell_order.data["items"][:]:

                    if sellOrder["location"]["name"] == jita_trade:
                        price_list_trade.append(sellOrder["price"])

                    if sellOrder["location"]["name"] == jita_npc:
                        price_list_npc.append(sellOrder["price"])

                # Calculate price for the item
                try:
                    item_profit = min(price_list_trade) - min(price_list_npc)
                except ValueError:
                    continue

                skillbook_list.append(Skillbook(item_profit, skillbook_name, min(price_list_trade), min(price_list_npc),
                                                sell_order.region))

            if sell_order.region == "amarr":
                # calculate_profit(sell_order, amarr_npc, amarr_trade)
                try:
                    skillbook_name = sell_order.data["items"][0]["type"]["name"]
                except IndexError:
                    sell_orders_list.remove(sell_order)
                    continue
                # Iterate through the items to check the location
                price_list_npc = []
                price_list_trade = []
                for sellOrder in sell_order.data["items"][:]:

                    if sellOrder["location"]["name"] == amarr_trade:
                        price_list_trade.append(sellOrder["price"])

                    if sellOrder["location"]["name"] == amarr_npc:
                        price_list_npc.append(sellOrder["price"])

                # Calculate price for the item
                try:
                    item_profit = min(price_list_trade) - min(price_list_npc)
                except ValueError:
                    continue

                skillbook_list.append(Skillbook(item_profit, skillbook_name, min(price_list_trade), min(price_list_npc),
                                                sell_order.region))

            if sell_order.region == "rens":
                # calculate_profit(sell_order, rens_npc, rens_trade)
                try:
                    skillbook_name = sell_order.data["items"][0]["type"]["name"]
                except IndexError:
                    sell_orders_list.remove(sell_order)
                    continue
                # Iterate through the items to check the location
                price_list_npc = []
                price_list_trade = []
                for sellOrder in sell_order.data["items"][:]:

                    if sellOrder["location"]["name"] == rens_trade:
                        price_list_trade.append(sellOrder["price"])

                    if sellOrder["location"]["name"] == rens_npc:
                        price_list_npc.append(sellOrder["price"])

                # Calculate price for the item
                try:
                    item_profit = min(price_list_trade) - min(price_list_npc)
                except ValueError:
                    continue

                skillbook_list.append(Skillbook(item_profit, skillbook_name, min(price_list_trade), min(price_list_npc),
                                                sell_order.region))

            if sell_order.region == "dodixie":
                # calculate_profit(sell_order, dodixie_npc, dodixie_trade)
                try:
                    skillbook_name = sell_order.data["items"][0]["type"]["name"]
                except IndexError:
                    sell_orders_list.remove(sell_order)
                    continue
                # Iterate through the items to check the location
                price_list_npc = []
                price_list_trade = []
                for sellOrder in sell_order.data["items"][:]:

                    if sellOrder["location"]["name"] == dodixie_trade:
                        price_list_trade.append(sellOrder["price"])

                    if sellOrder["location"]["name"] == dodixie_npc:
                        price_list_npc.append(sellOrder["price"])

                # Calculate price for the item
                try:
                    item_profit = min(price_list_trade) - min(price_list_npc)
                except ValueError:
                    continue

                skillbook_list.append(Skillbook(item_profit, skillbook_name, min(price_list_trade), min(price_list_npc),
                                                sell_order.region))

            if sell_order.region == "hek":
                # calculate_profit(sell_order, hek_npc, hek_trade)
                try:
                    skillbook_name = sell_order.data["items"][0]["type"]["name"]
                except IndexError:
                    sell_orders_list.remove(sell_order)
                    continue
                # Iterate through the items to check the location
                price_list_npc = []
                price_list_trade = []
                for sellOrder in sell_order.data["items"][:]:

                    if sellOrder["location"]["name"] == hek_trade:
                        price_list_trade.append(sellOrder["price"])

                    if sellOrder["location"]["name"] == hek_npc:
                        price_list_npc.append(sellOrder["price"])

                # Calculate price for the item
                try:
                    item_profit = min(price_list_trade) - min(price_list_npc)
                except ValueError:
                    continue

                skillbook_list.append(Skillbook(item_profit, skillbook_name, min(price_list_trade), min(price_list_npc),
                                                sell_order.region))

    print ("Cleaning invalid data")
    clean_sell_orders(sell_orders_list)
    print ("Calculating profits")
    process_sell_orders(sell_orders_list)
    return skillbook_list


def print_result(skillbook_list):
    skillbook_list = sorted(skillbook_list, key=lambda skillbook: skillbook.profit, reverse=True)
    total = "Total number of valid skillbooks : %i \n" % skillbook_list.__len__()
    separator = "-------------------------------\n"

    # THIS COULD GO INTO A REALLY NICE OOP FUNCTION YOU KNOW :D
    for skillbook in skillbook_list[:]:
        if skillbook.region == "jita":
            file_jita = open("skillbook_profit_jita.txt", "a")
            comma_price_npc = "ISK {:,.2f}".format(skillbook.price_npc)
            comma_price_trade = "ISK {:,.2f}".format(skillbook.price_trade)
            comma_item_profit = "ISK {:,.2f}".format(skillbook.profit)
            profit_line = "%s - Profit : %s \nNPC Cost : %s \nTrade Cost %s \n" % (
                skillbook.name, comma_item_profit, comma_price_npc, comma_price_trade)
            file_jita.write(profit_line)
            file_jita.write(separator)

        if skillbook.region == "rens":
            file_rens = open("skillbook_profit_rens.txt", "a")
            comma_price_npc = "ISK {:,.2f}".format(skillbook.price_npc)
            comma_price_trade = "ISK {:,.2f}".format(skillbook.price_trade)
            comma_item_profit = "ISK {:,.2f}".format(skillbook.profit)
            profit_line = "%s - Profit : %s \nNPC Cost : %s \nTrade Cost %s \n" % (
                skillbook.name, comma_item_profit, comma_price_npc, comma_price_trade)
            file_rens.write(profit_line)
            file_rens.write(separator)

        if skillbook.region == "dodixie":
            file_dodixie = open("skillbook_profit_dodixie.txt", "a")
            comma_price_npc = "ISK {:,.2f}".format(skillbook.price_npc)
            comma_price_trade = "ISK {:,.2f}".format(skillbook.price_trade)
            comma_item_profit = "ISK {:,.2f}".format(skillbook.profit)
            profit_line = "%s - Profit : %s \nNPC Cost : %s \nTrade Cost %s \n" % (
                skillbook.name, comma_item_profit, comma_price_npc, comma_price_trade)
            file_dodixie.write(profit_line)
            file_dodixie.write(separator)

        if skillbook.region == "hek":
            file_hek = open("skillbook_profit_hek.txt", "a")
            comma_price_npc = "ISK {:,.2f}".format(skillbook.price_npc)
            comma_price_trade = "ISK {:,.2f}".format(skillbook.price_trade)
            comma_item_profit = "ISK {:,.2f}".format(skillbook.profit)
            profit_line = "%s - Profit : %s \nNPC Cost : %s \nTrade Cost %s \n" % (
                skillbook.name, comma_item_profit, comma_price_npc, comma_price_trade)
            file_hek.write(profit_line)
            file_hek.write(separator)

        if skillbook.region == "amarr":
            file_amarr = open("skillbook_profit_amarr.txt", "a")
            comma_price_npc = "ISK {:,.2f}".format(skillbook.price_npc)
            comma_price_trade = "ISK {:,.2f}".format(skillbook.price_trade)
            comma_item_profit = "ISK {:,.2f}".format(skillbook.profit)
            profit_line = "%s - Profit : %s \nNPC Cost : %s \nTrade Cost %s \n" % (
                skillbook.name, comma_item_profit, comma_price_npc, comma_price_trade)
            file_amarr.write(profit_line)
            file_amarr.write(separator)


def main():
    print_result(sort_sell_order_prices(get_sell_order_crest(get_typeID_skillbooks())))


if __name__ == "__main__":
    main()
