# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from aqt import mw
from aqt.utils import getText

import random

def setEaseStatic(card_ids, ease):
    mw.col.modSchema(check=True)

    for card_id in card_ids:
        new_ease = int(ease) * 10
        mw.col.db.execute("UPDATE cards SET factor=? WHERE id=?", new_ease, card_id)
        
    mw.reset()

def setEaseDynamic(card_ids, add_low, add_high):
    mw.col.modSchema(check=True)

    for card_id in card_ids:
        current_ease = mw.col.db.scalar("SELECT factor FROM cards WHERE id=?", card_id)
        new_ease = int(current_ease) + int(random.randint(add_low, add_high)) * 10
        mw.col.db.execute("UPDATE cards SET factor=? WHERE id=?", new_ease, card_id)
    
    mw.reset()

def setCardEase(browser):
    if not browser.selectedCards():
        return

    card_ids = browser.selectedCards()

    user_input, succeeded = getText("Enter new card ease factor. Examples of acceptable values are '250' (default starting value), '-10,+25' (adds the random value from the interval [-10, 25] to the current ease factor).", 
                                    parent=browser, default="250")
    if not succeeded:
        return

    try:
        ease = int(user_input)
        setEaseStatic(card_ids, ease)
    except ValueError:
        pass

    try:
        interval = user_input.split(',')
        if len(interval) != 2:
            raise ValueError
        setEaseDynamic(card_ids, int(interval[0]), int(interval[1]))
    except ValueError:
        pass
