# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from aqt import mw
from aqt.utils import tooltip, showWarning, getText
from aqt.operations import CollectionOp
from anki import version as anki_version

import random

from . import config_manager

PROMPT_TEXT = \
"""Enter new card ease factor.
250 = sets ease factors to default starting value
+120 = adds 120 to current ease factor values
-10,25 = adds a random value from the interval [-10, 25] to current ease factor values
*0.9 = multiplies current ease factor values by 0.9
*0.8,1.2 = multiplies current ease factor values by a random value from the interval [0.8, 1.2]"""

def isNumber(str, strict_numeric=False, strict_positive=False):
    if strict_numeric:
        if any(not (x.isnumeric() or x == '.') for x in str):
            return False
    try:
        f = float(str)
    except ValueError:
        return False
    if strict_positive:
        if f <= 0:
            return False
    return True
def getNumber(str):
    return float(str)
def isNumberPair(str, strict_growing=True, strict_positive=False):
    pair = str.split(',')
    if len(pair) != 2:
        return False
    try:
        f1, f2 = float(pair[0]), float(pair[1])
    except ValueError:
        return False
    if strict_growing:
        if not f1 < f2:
            return False
    if strict_positive:
        if f1 <= 0 or f2 <= 0:
            return False
    return True
def getNumberPair(str):
    pair = str.split(',')
    return float(pair[0]), float(pair[1])

def setCardEaseOp(col, id_card, id_factor):
    for cid in id_card:
        id_card[cid].factor = round(id_factor[cid])

    if anki_version == '2.1.45':
        for card in id_card.values():
            col.update_card(card)
        changes = col.update_note(list(id_card.values())[0].note())
        changes.browser_table = True
    else:
        changes = col.update_cards(list(id_card.values()))

    return changes

def setCardEase(card_ids, parent, initiator):
    if not card_ids:
        tooltip("No cards selected!")
        return

    id_card = {card_id : mw.col.get_card(card_id) for card_id in card_ids}
    id_factor = {card_id : id_card[card_id].factor for card_id in card_ids}

    if any(factor == 0 for factor in id_factor.values()):
        showWarning("New cards detected. You cannot change card ease factor during learning phase.")
        return

    prompt = PROMPT_TEXT
    if len(id_card) == 1:
        prompt = f"Current card ease factor value: {int(list(id_factor.values())[0]) // 10}%" + "\n\n" + PROMPT_TEXT

    default_input = config_manager.configRead(config_manager.CONFIG_DEFAULT_INPUT, default='250')
    user_input, succeeded = getText(prompt, parent=parent, default=default_input)
    if not succeeded:
        return

    # If user_input is a strictly clean number (no '+', '-', or other characters), set ease to that value
    is_number = isNumber(user_input, strict_numeric=True)
    # If first character is '*', set either to multiple of current values or multiple in range, depending on remaining input
    is_multiplication_simple = user_input[0] in ['*'] and isNumber(user_input[1:], strict_positive=True)
    is_multiplication_range = user_input[0] in ['*'] and isNumberPair(user_input[1:], strict_positive=True)    
    # If first character is '+', '-', or the string is a pair, set either to add of current values or random add in range, depending on remaining input
    is_addition_simple = user_input[0] in ['+', '-'] and isNumber(user_input)
    is_addition_range = isNumberPair(user_input)

    if is_number:
        val = getNumber(user_input)
        id_factor = {cid : val*10 for cid in card_ids}
    elif is_multiplication_simple:
        val = getNumber(user_input[1:])
        id_factor = {cid : id_factor[cid]*val for cid in card_ids}
    elif is_multiplication_range:
        low, high = getNumberPair(user_input[1:])
        id_factor = {cid : id_factor[cid]*random.uniform(low, high) for cid in card_ids}
    elif is_addition_simple:
        val = getNumber(user_input)
        id_factor = {cid : id_factor[cid] + val*10 for cid in card_ids}
    elif is_addition_range:
        low, high = getNumberPair(user_input)
        id_factor = {cid : id_factor[cid] + random.uniform(low, high)*10 for cid in card_ids}
    else:
        showWarning("Invalid input.")
        return
    
    # Card factors like '2505' or '250.5%' are annoying, round last digit
    id_factor = {cid : int(round(id_factor[cid], -1)) for cid in id_factor}

    success_string = f"Set ease factor of {len(id_factor)} cards."
    if len(id_card) == 1:
        success_string = f"Set ease factor value to {list(id_factor.values())[0] // 10}%."

    CollectionOp(parent, lambda col: setCardEaseOp(col, id_card, id_factor)) \
        .success(lambda _: tooltip(success_string, parent=parent)) \
        .run_in_background(initiator=initiator)

    config_manager.configWrite(config_manager.CONFIG_DEFAULT_INPUT, user_input)
    