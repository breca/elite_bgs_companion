from . import log
import webbrowser


# donate menu item function
def listen(config):
    log.info('Opening listen link.')
    webbrowser.open_new(config['Links']['Radio'])

# donate menu item function
def donate(config):
    log.info('Opening donation link.')
    webbrowser.open_new(config['Links']['donate'])

# buy skins menu item function
def skin(config):
    log.info('Opening donation link.')
    webbrowser.open_new(config['Links']['skins'])

# feature request
def feature_request():
    log.info('Opening Github for a feature request.')
    webbrowser.open_new(r"https://github.com/breca/elite_bgs_companion/issues")

# bug report
def bug_report():
    log.info('Opening Github for a bug report.')
    webbrowser.open_new(r"https://github.com/breca/elite_bgs_companion/issues")

# discord
def discord():
    log.info('Opening Discord link.')
    webbrowser.open_new(r"https://discord.gg/0idLQikkQy6csbZx")
