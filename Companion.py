import logging.config
import yaml
import queue
from windows.main import MainWindow
from lib.debased import Debaser
from tkinter import *
from tkinter import ttk


'''
Copyright (C) 2018, CMDR Kalis for Radio Sidewinder.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


def load_configurations():
    """ Load distribution specific settings from YAML configuration files """

    logging.info('Loading distribution-specific config files.')

    with open('etc\\menus.yml')as f:
        menus = yaml.load(f)

    with open('etc\\strings.yml')as f:
        strings = yaml.load(f)

    with open('etc\\theme.yml')as f:
        theme = yaml.load(f)

    with open('etc\\urls.yml')as f:
        urls = yaml.load(f)

    with open('etc\\bgs.yml')as f:
        bgs = yaml.load(f)

    logging.info('Loading user settings.')

    with open('settings.yml')as f:
        settings = yaml.load(f)

    config = {'menu': menus,
              'string': strings,
              'theme': theme,
              'urls': urls,
              'bgs': bgs,
              'settings': settings
              }

    return config


if __name__ == '__main__':

    with open('logging.yml') as y:
        logging.config.dictConfig(yaml.load(y))
    logging.info('Starting Companion.')

    config = load_configurations()
    logging.info('Configuration loaded.')

    # logging.debug('Creating queues.')
    # q_main = queue.Queue()    # Main window queue
    # q_data = queue.Queue()    # Data handler queue
    # q_db = queue.Queue()      # Database query queue

    # Main window initialisation
    root = MainWindow(config)#, q_main, q_db)


    # # Data broker initialisation
    # data_broker = DataHandler(q_main, q_db)
    #
    # # Database initialisation
    # database = Debased(q.db)

    # Start monitoring queues
    #logging.debug('Monitoring queue.')
    #app.monitor_queue()

    #queue_main.put({'type': 'name', 'value': 'ftoopmsh'})

    # Enter main loop
    root.mainloop()

