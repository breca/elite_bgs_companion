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

# feature request
def feature_request():
    log.info('Opening Github for a feature request.')
    webbrowser.open_new(r"https://github.com/breca/elite_bgs_companion/issues")

# feature request
def bug_report():
    log.info('Opening Github for a bug report.')
    webbrowser.open_new(r"https://github.com/breca/elite_bgs_companion/issues")

# feature request
def discord():
    log.info('Opening Discord link.')
    webbrowser.open_new(r"https://discord.gg/0idLQikkQy6csbZx")
