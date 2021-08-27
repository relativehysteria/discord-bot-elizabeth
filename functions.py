#!/usr/bin/env python3.8
import json
from urllib.request import urlopen

from items import itemList

APIURL = "https://www.albion-online-data.com/api/v2/stats/prices"
CITIES = ",".join([
    "Bridgewatch",
    "Caerleon",
    "FortSterling",
    "Lymhurst",
    "Thetford",
    "Martlock"
])

# UTILS ########################################################################

def get_price(item) -> dict:
    with urlopen(f"{APIURL}/{item}?locations={CITIES}") as url:
        data = json.loads(url.read().decode())
    return data

# PRICE ########################################################################

async def price(*args) -> str:
    if len(args) < 1:
        return "Nedostatek argumentů."

    # Musime mit alespon jeden argument.
    item = args[0].upper()
    if item not in itemList:
        return "Item není v databázi"

    # Stahneme json s daty o itemu
    data = get_price(item)

    # Nyni vytvorime zpravu, kterou pote zasleme.
    # `lineCounter` pocita radky v tabulce.
    lineCounter = 0
    msg = "```\n"
    msg += f"         city |  min sell  |  max buy  \n"
    msg += f"══════════════╪════════════╪═══════════\n"
    for dic in data:
        city           = dic["city"]
        sell_price_min = dic["sell_price_min"]
        buy_price_max  = dic["buy_price_max"]

        if sell_price_min == 0 and buy_price_max == 0:
            continue

        lineCounter += 1
        msg += "{:>14}|{:^12}|{:^12}\n".format(city, sell_price_min, buy_price_max)
    msg += "```"

    return msg

# ENCHANT ######################################################################

# Pocet run, kolik je potreba na enchantovani.
# Index je typ, tzn:
#   0 => nic
#   1 => obourucni
#   2 => jednorucni
#   3 => brneni
#   4 => vsechno ostatni
ENCH_TYPES = [0, 192, 144, 96, 48]
ENCH_LEVEL = ["RUNE", "SOUL", "RELIC"]
MARKET_TAX = 7.15


def profit(cost: int, new_price: int) -> int:
    return int((new_price / 100) * (100 - MARKET_TAX)) - cost


async def enchant(*args) -> str:
    typHelp  = "eli enchant <typ> <tier> <enchant level> <cena> <nová cena>\n```"
    typHelp += f"1 - ({ENCH_TYPES[1]}) obourucni remdih\n"
    typHelp += f"2 - ({ENCH_TYPES[2]}) jednorucni\n"
    typHelp += f"3 -  ({ENCH_TYPES[3]}) brneni a batohy\n"
    typHelp += f"4 -  ({ENCH_TYPES[4]}) cokoliv jineho\n"
    typHelp += "```"

    if len(args) < 1:
        return typHelp
    if len(args) < 5:
        return "Nedostatek argumentů."

    # Vsechny argumenty musi byt numericke
    for arg in args:
        if not arg.isnumeric():
            return "Všechny argumenty musí být numerické"

    # Argumenty preneseme na cisla
    (typ, tier, level, price, priceNew) = [int(i) for i in args]

    # A zkontrolujeme, jestli jsou vsechny validni
    if typ < 1 or typ > 4:
        return typHelp
    if tier < 4 or tier > 8:
        return "Takový tier nelze enchantovat."
    if level < 0 or level > 2:
        return "Enchant level musí být číslo v rozmezí 0-2."
    if price <= 0:
        return "Cena musí být kladné číslo."

    # Vezmeme data z databaze
    data = get_price("T{}_{}".format(tier, ENCH_LEVEL[level]))

    # Data prepiseme do slovniku { "city": int(sell_price_min) }
    cityPrice = dict()
    for dic in data:
        cityPrice.setdefault(
            dic["city"],
            int(dic["sell_price_min"] * ENCH_TYPES[typ])
        )

    # Ted postavime tabulku a odesleme ji
    msg = "```\n"
    msg += f"         city |  total cost  |  profit  \n"
    msg += f"══════════════╪══════════════╪══════════\n"
    for (city, costRunes) in cityPrice.items():
        if costRunes == 0:
            continue

        cost = costRunes + price
        msg += "{:>14}|{:^14}|{:^10}\n".format(
            city,
            cost,
            profit(cost, priceNew)
        )
    msg += "```"

    return msg
