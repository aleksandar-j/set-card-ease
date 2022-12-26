# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from aqt import mw

CONFIG_DEFAULT_INPUT = 'default_input'
CONFIG_KEYBOARD_SHORTCUT = 'keyboard_shortcut'

def configRead(entry, default=''):
    return mw.addonManager.getConfig(__name__).get(entry, default)

def configWrite(entry, value):
    try:
        config = mw.addonManager.getConfig(__name__)
        config[entry] = value
        mw.addonManager.writeConfig(__name__, config)
    except:
        pass
