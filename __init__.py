# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from aqt import gui_hooks
from aqt.qt import QAction

from . import set_card_ease

def setupAction(browser):
    actionSetCardEase = QAction("Set Ease Factor...", browser)
    actionSetCardEase.triggered.connect(lambda: set_card_ease.setCardEase(browser))

    browser.form.menu_Cards.insertAction(browser.form.menu_Cards.actions()[2], actionSetCardEase)

gui_hooks.browser_menus_did_init.append(setupAction)
