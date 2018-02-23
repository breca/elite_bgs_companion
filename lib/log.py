import logging
#from logging.handlers import RotatingFileHandler
from os import remove

#oh jesus, the tears
import configparser
config = configparser.ConfigParser()
config.read('settings.ini')

# hahaha
if config['General']['LogLevel'] == 'debug':
    logging.basicConfig(filename='companion.log',level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
elif config['General']['LogLevel'] == 'info':
    logging.basicConfig(filename='companion.log',level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    #logging.Formatter(datefmt='%Y-%m-%d, %H:%M:%S - ')
    #my_handler = RotatingFileHandler('companion.log', mode='a', maxBytes=5*1024*1024, backupCount=2, encoding=None, delay=0)
    #my_handler.setFormatter(log_formatter)
    #my_handler.setLevel(logging.INFO)
    #logging.getLogger("").addHandler(my_handler)
# Windows file handlers are shit


def exception(text, e):
    logging.exception(text + '\n' + str(e))
    raise

def error(text):
    logging.error(text)

def warning(text):
    logging.warning(text)

def info(text):
    logging.info(text)

def debug(text):
    logging.debug(text)
