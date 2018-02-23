from . import log
import webbrowser

# donate menu item function
def listen():
    log.info('Opening listen link.')
    webbrowser.open_new(r"https://www.radiosidewinder.com/listen-now/")

# donate menu item function
def donate():
    log.info('Opening donation link.')
    webbrowser.open_new(r"https://www.radiosidewinder.com/donate/")

# buy skins menu item function
def skin():
    log.info('Opening donation link.')
    webbrowser.open_new(r"https://www.radiosidewinder.com/shipskins/")
