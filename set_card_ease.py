# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from aqt.utils import tooltip, showWarning, getText
from aqt.operations import CollectionOp

import random

def isInteger(str):
    try:
        int(str)
        return True
    except ValueError:
        return False
def isIntegerPair(str):
    try:
        pair = str.split(',')
        if len(pair) != 2:
            raise ValueError
        int(pair[0])
        int(pair[1])
        return True
    except ValueError:
        return False
def getIntegerPair(str):
    pair = str.split(',')
    return int(pair[0]), int(pair[1])

def setEaseStatic(col, card_ids, ease):
    cards = [col.get_card(card_id) for card_id in card_ids]

    for card in cards:
        card.factor = int(ease) * 10
    
    return col.update_cards(cards)

def setEaseDynamic(col, card_ids, add_low, add_high):
    cards = [col.get_card(card_id) for card_id in card_ids]

    for card in cards:
        card.factor = int(card.factor) + int(random.randint(add_low, add_high)) * 10

    return col.update_cards(cards)

def setCardEase(browser):
    card_ids = browser.selectedCards()
    if not card_ids:
        return

    user_input, succeeded = getText("Enter new card ease factor.\n250 = default starting value\n-10,25 = adds the random value from the interval [-10, 25] to the current ease factor", 
                                    parent=browser, default="250")
    if not succeeded:
        return

    if isInteger(user_input):
        op = CollectionOp(browser, lambda col: setEaseStatic(col, card_ids, int(user_input)))
        op.success(lambda _: tooltip(f"Set ease factor of {len(card_ids)} cards.", parent=browser))
        op.run_in_background()
        return

    if isIntegerPair(user_input):
        low, high = getIntegerPair(user_input)
        op = CollectionOp(browser, lambda col: setEaseDynamic(col, card_ids, low, high))
        op.success(lambda _: tooltip(f"Set ease factor of {len(card_ids)} cards.", parent=browser))
        op.run_in_background()
        return

    showWarning("Invalid input.")
