# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from aqt import mw
from aqt.utils import tooltip, showWarning, getText
from aqt.operations import CollectionOp
from anki import version as anki_version

import random

PROMPT_TEXT = \
"""Enter new card ease factor.
250 = sets ease factor to the default starting value
+120 = adds 120 to the current ease factor values
-10,25 = adds a random value from the interval [-10, 25] to the current ease factor
*0.9 = multiplies the current ease factor values by 0.9
*0.8,1.2 = multiplies the current ease factor with a random value from the interval [0.8, 1.2]"""

def isNumber(str, strict=False):
    if strict:
        if any([not (x.isnumeric() or x == '.') for x in str]):
            return False
    try:
        float(str)
    except ValueError:
        return False
    return True
def getNumber(str):
    return float(str)
def isNumberPair(str):
    pair = str.split(',')
    if len(pair) != 2:
        return False
    try:
        float(pair[0])
        float(pair[1])
    except ValueError:
        return False
    return True
def getNumberPair(str):
    pair = str.split(',')
    return float(pair[0]), float(pair[1])

def update_cards(col, cards):
    if anki_version == '2.1.45':
        for card in cards:
            col.update_card(card)
        return col.update_note(cards[0].note())
    else:
        return col.update_cards(cards)

def setEaseStatic(col, card_ids, ease):
    cards = [col.get_card(card_id) for card_id in card_ids]
    for card in cards:
        card.factor = int(round(ease * 10, -1))
    return update_cards(col, cards)

def setEaseDynamicAdd(col, card_ids, add):
    cards = [col.get_card(card_id) for card_id in card_ids]
    for card in cards:
        card.factor = int(round(card.factor + add * 10, -1))
    return update_cards(col, cards)
def setEaseDynamicAddRandom(col, card_ids, add_low, add_high):
    cards = [col.get_card(card_id) for card_id in card_ids]
    for card in cards:
        card.factor = int(round(card.factor + random.uniform(add_low, add_high) * 10, -1))
    return update_cards(col, cards)

def setEaseDynamicMultiply(col, card_ids, mult):
    cards = [col.get_card(card_id) for card_id in card_ids]
    for card in cards:
        card.factor = int(round(card.factor * mult, -1))
    return update_cards(col, cards)
def setEaseDynamicMultiplyRandom(col, card_ids, mult_low, mult_high):
    cards = [col.get_card(card_id) for card_id in card_ids]
    for card in cards:
        card.factor = int(round(card.factor * random.uniform(mult_low, mult_high), -1))
    return update_cards(col, cards)

def configRead(entry, default=''):
    try:
        return mw.addonManager.getConfig(__name__)[entry]
    except:
        return default
def configWrite(entry, value):
    try:
        config = mw.addonManager.getConfig(__name__)
        config[entry] = value
        mw.addonManager.writeConfig(__name__, config)
    except:
        pass

def startCollectionOp(browser, op, card_id_len):
    op = CollectionOp(browser, op)
    op.success(lambda _: tooltip(f"Set ease factor of {card_id_len} cards.", parent=browser))
    op.run_in_background()

def setCardEase(browser):
    card_ids = browser.selectedCards()
    if not card_ids:
        return

    user_input, succeeded = getText(PROMPT_TEXT, parent=browser, default=configRead('default_input', default='250'))
    if not succeeded:
        return

    # If user_input is a strictly clean number (no '+', '-', or other characters), set ease to that value
    if isNumber(user_input, strict=True):
        val = getNumber(user_input)
        startCollectionOp(browser, lambda col: setEaseStatic(col, card_ids, val), len(card_ids))
        configWrite('default_input', user_input)
        return

    # If first character is '*', set either to multiple of current values or multiple in range, depending on remaining input
    if user_input[0] in ['*']:
        if isNumber(user_input[1:]):
            val = getNumber(user_input[1:])
            startCollectionOp(browser, lambda col: setEaseDynamicMultiply(col, card_ids, val), len(card_ids))
            configWrite('default_input', user_input)
            return
        elif isNumberPair(user_input[1:]):
            low, high = getNumberPair(user_input[1:])
            startCollectionOp(browser, lambda col: setEaseDynamicMultiplyRandom(col, card_ids, low, high), len(card_ids))
            configWrite('default_input', user_input)
            return

    # If first character is '+', '-', or the string is a pair, set either to add of current values or random add in range, depending on remaining input
    if user_input[0] in ['+', '-'] or isNumberPair(user_input):
        if isNumber(user_input[1:]):
            val = getNumber(user_input)
            startCollectionOp(browser, lambda col: setEaseDynamicAdd(col, card_ids, val), len(card_ids))
            configWrite('default_input', user_input)
            return
        elif isNumberPair(user_input):
            low, high = getNumberPair(user_input)
            startCollectionOp(browser, lambda col: setEaseDynamicAddRandom(col, card_ids, low, high), len(card_ids))
            configWrite('default_input', user_input)
            return

    showWarning("Invalid input.")
