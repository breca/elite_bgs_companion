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
        self.transacton_db = SqliteDict('companion.db', 'transaction', autocommit=True)
        self.session_db = SqliteDict('companion.db', 'session', autocommit=True)
        # Session data storage
        if 'commander_name' not in self.session_db.keys():
            logger.info('Creating new session table.')
            self.session_db['journal_filename'] = ''
            self.session_db['journal_offset'] = 0
            self.session_db['commander_name'] = ''
            self.session_db['credits'] = ''
            self.session_db['credits_int'] = 0
            self.session_db['ship_name'] = ''
            self.session_db['ship'] = ''
            self.session_db['game_mode'] = ''
            self.session_db['game_mode_group'] = ''
            self.session_db['system'] = ''
            self.session_db['system_factions'] = {}
            self.session_db['near_body'] = ''
            self.session_db['near_body_type'] = ''
            self.session_db['docked'] = ''
            self.session_db['landed'] = ''
            self.session_db['station_name'] = ''
            self.session_db['station_faction'] = ''
            self.session_db['location'] = ''
            self.session_db.commit()
            logger.info('Created session table.')

    def get_session(self, key=None):
        try:
            if key:
                logging.debug('Attempting to fetch "{}" from database'.format(key))
                data = self.session_db[key]
                logging.debug('Fetched: {}'.format(str(data)))
                return data
            else:
                data = {}
                for k in self.session_db.keys():
                    data[k] = self.session_db[k]
                return data
        except KeyError:
            logging.warning('Tried to fetch key {}, but could not find it in the db.'.format(key))
            pass
        except:
            logging.exception('Caught unhandled exception:')
            raise

    def update_session(self, data):
        try:
            if not isinstance(data, dict):
                logging.warning('Attempting to update using a non-dict variable:\n' + str(data))
            #self.db = { **self.db, **data}  # Merge method
            self.session_db.update(data)
            self.session_db.commit()
        except:
            logging.exception('Caught unhandled exception:')
            logging.exception('Supplied data was: ' + str(data))
            raise

    def file_transaction(self, transaction):
        for system in transaction.keys():
            if system not in self.transacton_db['transactions'].keys():
                self.transacton_db['transactions'][system] = transaction[system]
                return
            for station in system.keys():
                if station not in self.transacton_db['transactions'][system].keys():
                    self.transacton_db['transactions'][system][station] = transaction[station]
                    return
                for faction in station.keys():
                    if faction not in self.transacton_db['transactions'][system][station].keys():
                        self.transacton_db['transactions'][system][station][faction] = transaction[faction]
                        return
                    for voucher in faction.keys():
                        if voucher not in self.transacton_db['transactions'][system][station][faction].keys():
                            self.transacton_db['transactions'][system][station][faction][voucher] = transaction[voucher]
                            return
                        else:
                            self.transacton_db['transactions'][system][station][faction][voucher]['count'] += 1
                            self.transacton_db['transactions'][system][station][faction][voucher]['amount'] += \
                                transaction[voucher]['amount']


    def close(self):
        self.session_db.commit()
        self.transacton_db.commit()

''' Sample data structure for BGS transaction database
# Note that in all cases, the data MUST pass validation before it gets this far.
bgs = {
    'transactions': {
            '37 Librae': {                              # Star System
                'Roosa Market': {                       # Station / Settlement
                    'Radio Sidewinder Crew': {          # Faction
                        'state': 'N/A',                 # Faction State (Boom, etc)
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





