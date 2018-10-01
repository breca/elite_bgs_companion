from sqlitedict import SqliteDict
import logging
logger = logging.getLogger(__name__)


"""
- Stores data
- Fetches data
- That's it
"""


class Debaser:

    def __init__(self):
        logging.info('Database handler ready.')
        self.db = SqliteDict('companion.db', 'companion', autocommit=True)
        # Session data storage
        if 'session' not in self.db.keys():
            logger.info('Creating new session data.')
            self.db['session'] = {
                'journal_file': '',
                'journal_offset': 0,
                'commander_name': 0,
                'credits': 0,
                'ship_name': '',
                'ship': '',
                'game_mode': '',
                'game_mode_group': '',
                'system': '',
                'system_facts': '',
                'near_body': '',
                'near_body_type': '',
                'docked': '',
                'landed': '',
                'station_name': '',
                'station_faction': '',
                'location': '',
                'in_srv': ''
            }
            self.db.commit()
        else:
            logger.info('Found session data.')

        if 'transactions' not in self.db.keys():
            logger.info('Creating new transaction data.')
            self.db['transactions'] = {}
            self.db.commit()
        else:
            logger.info('Found transaction data.')

    def get(self, key):
        try:
            logging.debug('Attempting to fetch key "{}" from database'.format(key))
            data = self.db[key]
            logging.debug('Fetched: {}'.format(str(data)))
            return data
        except KeyError:
            logging.warning('Tried to fetch key {}, but could not find it in the db.'.format(key))
            pass
        except Exception as e:
            logging.exception('Caught unhandled exception: ' + str(e))
            raise

    def put(self, data):
        try:
            if isinstance(data, dict):
                # self.db = { **self.db, **data}  # Merge method
                self.db.update(data)
                self.db.commit()
            else:
                logging.warning('Tried to put a non-dictionary entry into the database!')
        except Exception as e:
            logging.exception('Caught unhandled exception: ' + str(e))
            raise


''' Sample data structure for BGS transaction database
# Note that in all cases, the data MUST pass validation before it gets this far.
bgs = {
    'transactions': {
            '37 Librae': {                              # Star System
                'Roosa Market': {                       # Station / Settlement
                    'Radio Sidewinder Crew': {          # Faction
                        'state': 'N/A',                 # Faction State (Boom, etc)
                        'transactions': {
                            'combat': {
                                'count': 2,          # Total combat bond transactions
                                'kills': 23,         # Total warzone kills
                                'amount': 5000,      # Total combat bond credits rewarded
                                'commanders': 2,     # Number of commander bounties collected
                                'cmdr_names': { 'name': 4 }     # Commander names and times killed
                                },
                            'bounty': {
                                'count': 2,          # Total bounty transactions
                                'kills': 23,         # Total bounty kills
                                'amount': 5000,      # Total bounty credits rewarded
                                'commanders': 2,     # Number of commander bounties collected
                                'cmdr_names': { 'name': 4 }     # Commander names and times killed
                                },
                            'trade': {
                                'count': {            # Number of trades made
                                   'high': 12,        # Trade transaction with high profit (>700 credits)
                                   'high_commtypes': [], # List of commodity types traded at this level
                                   'normal': 2,          # Trade transaction with normal profit (<700 credits)
                                   'normal_commtypes': [], # List of commodity types traded at this level
                                   'loss': 231        # Trade transaction at a loss (<0 credits)
                                   'loss_commtypes': [] # List of commodity types traded at this level

                                   }
                                'amount': 12313,      # Credits made/lost trading
                                },
                            'smuggled': {
                                'count': {            # Number of trades made
                                   'high': 12,        # Trade transaction with high profit (>700 credits)
                                   'high_commtypes': [], # List of commodity types traded at this level
                                   'normal': 2,          # Trade transaction with normal profit (<700 credits)
                                   'normal_commtypes': [], # List of commodity types traded at this level
                                   'loss': 231        # Trade transaction at a loss (<0 credits)
                                   'loss_commtypes': [] # List of commodity types traded at this level
                                   }
                                'amount': 12321
                                },
                            'mission': {                # FDev still haven't given us proper identifiers for this...
                                'completed': { 
                                   'high': 2,           # and as such 99% missions will be 'medium'.
                                   'medium': 2,         # ...makes you wonder...
                                   'low': 2
                                   }
                                'abandoned': 4,      # Missions abandoned
                                'amount': 12342,    # Amount raised waiting for a decent mission system
                                'id': ['123123123', '54353445324'] # Used to ensure no doubling of mission data
                                },
                            'exploration: { 
                                'count': 123,   # Individual exploration transactions
                                'amount': 10    # Amount raised from selling exploration data
                            }
                        }
                    },
                },
                'murder': {                            # Murders committed against NPCs in this system
                    'Law Party of Whatever': 5
                },
                'assault': {                           # Assaults committed in this system
                    'Law Party of Whatever': 5
                },
                'fine': 238746,                        # Fines accrued in this system
                'commanders_killed': {
                    'CMDR Kalis': 324235                # Commanders dispatched in this system
                }
            }
        }
    }
'''





