# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from aqt import mw
from aqt.utils import tooltip, showWarning, getText
from aqt.operations import CollectionOp

import random

def isNumber(str):
    try:
        float(str)
        return True
    except ValueError:
        return False
def isNumberPair(str):
    try:
        pair = str.split(',')
        if len(pair) != 2:
            raise ValueError
        float(pair[0])
        float(pair[1])
        return True
    except ValueError:
        return False
def getNumberPair(str):
    pair = str.split(',')
    return float(pair[0]), float(pair[1])

def load_config_val(entry, default=''):
    try:
        return mw.addonManager.getConfig(__name__)[entry]
    except:
        return default
def write_config_val(entry, value):
    try:
        config = mw.addonManager.getConfig(__name__)
        config[entry] = value
        mw.addonManager.writeConfig(__name__, config)
    except:
        pass

def setEaseStatic(col, card_ids, ease):
    cards = [col.get_card(card_id) for card_id in card_ids]

    for card in cards:
        card.factor = int(round(ease * 10, -1))
    
    return col.update_cards(cards)

def setEaseDynamicAdd(col, card_ids, add_low, add_high):
    cards = [col.get_card(card_id) for card_id in card_ids]

    for card in cards:
        card.factor = int(round(card.factor + random.uniform(add_low, add_high) * 10, -1))

    return col.update_cards(cards)

def setEaseDynamicMultiply(col, card_ids, mult_low, mult_high):
    cards = [col.get_card(card_id) for card_id in card_ids]

    for card in cards:
        card.factor = int(round(card.factor * random.uniform(mult_low, mult_high), -1))

    return col.update_cards(cards)

def setCardEase(browser):
    card_ids = browser.selectedCards()
    if not card_ids:
        return

    user_input, succeeded = getText("Enter new card ease factor.\n250 = sets ease factor to the default starting value\n-10,25 = adds a random value from the interval [-10, 25] to the current ease factor\n*0.8,1.2 = multiplies the current ease factor with a random value from the interval [0.8, 1.2]", 
                                    parent=browser, default=load_config_val('default_input', default='250'))
    if not succeeded:
        return

    if isNumber(user_input):
        ease = float(user_input)
        op = CollectionOp(browser, lambda col: setEaseStatic(col, card_ids, ease))
        op.success(lambda _: tooltip(f"Set ease factor of {len(card_ids)} cards.", parent=browser))
        op.run_in_background()
        write_config_val('default_input', user_input)
        return

    if isNumberPair(user_input):
        low, high = getNumberPair(user_input)
        op = CollectionOp(browser, lambda col: setEaseDynamicAdd(col, card_ids, low, high))
        op.success(lambda _: tooltip(f"Set ease factor of {len(card_ids)} cards.", parent=browser))
        op.run_in_background()
        write_config_val('default_input', user_input)
        return

    if '*' == user_input[0] and isNumberPair(user_input[1:]):
        low, high = getNumberPair(user_input[1:])
        op = CollectionOp(browser, lambda col: setEaseDynamicMultiply(col, card_ids, low, high))
        op.success(lambda _: tooltip(f"Set ease factor of {len(card_ids)} cards.", parent=browser))
        op.run_in_background()
        write_config_val('default_input', user_input)
        return

    showWarning("Invalid input.")
