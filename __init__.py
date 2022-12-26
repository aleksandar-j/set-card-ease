# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from aqt import mw, gui_hooks
from aqt.qt import QAction, QKeySequence

from . import set_card_ease
from . import config_manager

SET_DUE_DATE_TEXT = "Set Due Date..."
SET_CARD_EASE_TEXT = "Set Ease Factor..."

def createAction(action, parent):
    actionSetCardEase = QAction(SET_CARD_EASE_TEXT, parent)
    actionSetCardEase.triggered.connect(action)
    if shortcut := config_manager.configRead(config_manager.CONFIG_KEYBOARD_SHORTCUT):
        actionSetCardEase.setShortcut(QKeySequence(shortcut))
    return actionSetCardEase

def getActionIndex(menu, text, default=-1):
    actions_text = (action.text() for action in menu.actions())
    actions_equal = (i for i, action_text in enumerate(actions_text) if action_text == text)
    return next(actions_equal, default)

def setupBrowserAction(browser):
    actionLambda = lambda: set_card_ease.setCardEase(browser.selectedCards(), browser, browser)
    actionSetCardEase = createAction(actionLambda, browser)
    
    set_due_date_index = getActionIndex(browser.form.menu_Cards, SET_DUE_DATE_TEXT, default=2)
    insert_action_at = browser.form.menu_Cards.actions()[set_due_date_index]
    browser.form.menu_Cards.insertAction(insert_action_at, actionSetCardEase)

    def setupBrowserActionActivity(browser):
        set_ease_index = getActionIndex(browser.form.menu_Cards, SET_CARD_EASE_TEXT)
        if set_ease_index == -1:
            return
        browser.form.menu_Cards.actions()[set_ease_index].setEnabled(bool(browser.table.len_selection()))
    gui_hooks.browser_did_change_row.append(setupBrowserActionActivity)

gui_hooks.browser_menus_did_init.append(setupBrowserAction)

def setupReviewerAction(reviewer, menu):
    actionLambda = lambda: set_card_ease.setCardEase([reviewer.card.id], reviewer.mw, reviewer)
    actionSetCardEase = createAction(actionLambda, menu)
    
    set_due_date_index = getActionIndex(menu, SET_DUE_DATE_TEXT, default=-1)
    if set_due_date_index == -1:
        set_due_date_index = getActionIndex(menu, SET_DUE_DATE_TEXT[:-3], default=3)
    insert_action_at = menu.actions()[set_due_date_index]
    menu.insertAction(insert_action_at, actionSetCardEase)

def setupReviewerActionShortcut(state, shortcuts):
    if state == 'review':
        if shortcut := config_manager.configRead(config_manager.CONFIG_KEYBOARD_SHORTCUT):
            x = (shortcut, lambda: set_card_ease.setCardEase([mw.reviewer.card.id], mw, mw.reviewer))
            shortcuts.append(x)

gui_hooks.reviewer_will_show_context_menu.append(setupReviewerAction)
gui_hooks.state_shortcuts_will_change.append(setupReviewerActionShortcut)
