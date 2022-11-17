# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from aqt import gui_hooks
from aqt.qt import QAction

from . import set_card_ease

SET_DUE_DATE_TEXT = "Set Due Date..."
SET_CARD_EASE_TEXT = "Set Ease Factor..."

def createAction(action, parent):
    actionSetCardEase = QAction(SET_CARD_EASE_TEXT, parent)
    actionSetCardEase.triggered.connect(action)
    return actionSetCardEase

def getActionIndex(menu, text, default=-1):
    actions_text = [action.text() for action in menu.actions()]
    try:
        return actions_text.index(text)
    except ValueError:
        return default

def setupBrowserAction(browser):
    actionLambda = lambda: set_card_ease.setCardEase(browser.selectedCards(), browser, browser)
    actionSetCardEase = createAction(actionLambda, browser)
    
    set_due_date_index = getActionIndex(browser.form.menu_Cards, SET_DUE_DATE_TEXT, default=2)
    insert_action_at = browser.form.menu_Cards.actions()[set_due_date_index]
    browser.form.menu_Cards.insertAction(insert_action_at, actionSetCardEase)

def setupReviewerAction(reviewer, menu):
    actionLambda = lambda: set_card_ease.setCardEase([reviewer.card.id], reviewer.web, reviewer)
    actionSetCardEase = createAction(actionLambda, reviewer.web)
    
    set_due_date_index = getActionIndex(menu, SET_DUE_DATE_TEXT, default=-1)
    if set_due_date_index == -1:
        set_due_date_index = getActionIndex(menu, SET_DUE_DATE_TEXT[:-3], default=3)
    insert_action_at = menu.actions()[set_due_date_index]
    menu.insertAction(insert_action_at, actionSetCardEase)

gui_hooks.browser_menus_did_init.append(setupBrowserAction)
gui_hooks.reviewer_will_show_context_menu.append(setupReviewerAction)
