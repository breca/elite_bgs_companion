import threading
import glob
import json
from time import sleep
from collections import defaultdict
from os import path, environ
import logging
logger = logging.getLogger(__name__)

"""
- Scans the journal file
- Captures events
- Checks for validity
- Supplies data to the main window
- Shoves stuff into the database
"""


class JournalMonitor(threading.Thread):
    def __init__(self, parent):
        super(JournalMonitor, self).__init__()
        self._stop_event = threading.Event()

        self.parent = parent
        self.db = parent.db

        # Retrieve old session data from DB
        self.filename = self.db.get_session('journal_filename')
        self.offset = self.db.get_session('journal_offset')

        self.path = path.join(environ.get("USERPROFILE") +
                                      '\\Saved Games\\Frontier Developments\\Elite Dangerous')

        with open('etc\\commodities.json', 'r') as f:
            self.commodity = json.loads(f.read())

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        update = {'journal_offset': self.offset,
                  'journal_filename': str(self.filename)}
        self.db.update_session(update)
        return self._stop_event.is_set()

    def run(self):
        while not self.stopped():
            self.new_file = False
            session = {}

            try:
                new = max(glob.iglob(path.join(self.path, '*.log')), key=path.getctime)

                if self.filename != new:
                    self.filename = new
                    self.parent.set_status('New journal detected. Opening file.')
                    sanitised_name = new.split('\\')[-1]
                    logging.info('Found new file: ' + sanitised_name)
                    self.file = open(new, 'r')
                    logging.debug('Resetting offset value.')
                    self.offset = 0
                    session['journal_offset'] = 0
                    self.db.update_session(session)
                    self.new_file = True
                    session['journal_filename'] = str(self.file)
                    self.db.update_session(session)
                elif not self.new_file:
                    if not hasattr(self, 'file'):
                        logging.info('Opening old journal.')
                        self.file = open(new, 'r')
                        logging.debug('Moving to previous offset.')
                        self.offset = self.db.get_session('journal_offset')
                        logging.debug('Using offset ' + str(self.offset))
                        self.file.seek(self.offset)
            except:
                logging.exception('Hit exception checking for file.')

            try:
                file_data = self.file.readline()
                self.offset = self.file.tell()
                session['journal_offset'] = self.offset
                self.db.update_session(session)
                self.parse(file_data)
                sleep(0.05)
            except json.JSONDecodeError:
                pass
            except:
                logging.exception('Exception occurred parsing JSON.')
                logging.exception('Data was: ' + file_data)
                pass

    def parse(self, file_data):
        data = json.loads(file_data)
        logging.debug('Parsing JSON')

        event = data['event']
        update = makehash()
        transaction = makehash()

        # --- Generic events
        if event == 'LoadGame':
            logging.debug('Found ' + event + '.')
            update['commander_name'] = data['Commander']
            update['ship_name'] = data['ShipName']
            update['ship'] = data['Ship']
            update['game_mode'] = data['GameMode']

            self.parent.update_commander(data['Commander'])
            self.parent.update_shipname(data['ShipName'], data['Ship'])

            # Set credits directly for loadgame events
            self.parent.credits_int = data['Credits']
            nice_credits = str('${:,}'.format(self.parent.credits_int))
            self.parent.credits.set(nice_credits)
            self.parent.credits_delta_int = 0
            nice_delta_credits = str('$0')
            self.parent.credits_delta.set(nice_delta_credits)

            update['credits_int'] = data['Credits']
            update['credits'] = nice_credits

            if 'Group' in data.keys():
                update['game_mode_group'] = data['Group']
                self.parent.update_game_mode(data['GameMode'], data['Group'])
            else:
                self.parent.update_game_mode(data['GameMode'])

            if 'StartLanded' in data.keys():
                update['landed'] = True


        elif event == 'Loadout':
            logging.debug('Found ' + event + '.')
            update['ship_name'] = data['ShipName']
            update['ship'] = data['Ship']
            self.parent.update_shipname(data['ShipName'], data['Ship'])

        # --- Location events
        elif event == 'Location':
            logging.debug('Found ' + event + '.')

            update['system'] = data['StarSystem']
            update['near_body'] = data['Body']
            update['near_body_type'] = data['BodyType']

            if data['Docked'] == 'True':
                update['docked'] = True
                update['station_name'] = data['StationName']
            else:
                update['docked'] = False
                update['station_name'] = ''

            location_string = self.location_generator(data)
            update['location'] = location_string
            self.parent.update_location(location_string)

        # REVIEW I'm not convinced the below really adds much
        elif event == 'StartJump':
            logging.debug('Found ' + event + '.')
            if data['JumpType'] == 'Hyperspace':
                location_string = 'Jumping to the {} system.'.format(data['StarSystem'])
                update['location'] = location_string
                self.parent.update_location(location_string)

        elif event == 'SupercruiseExit':
            logging.debug('Found ' + event + '.')
            update = {'session': {'system': data['StarSystem']}}
            if 'BodyType' in data.keys():
                location_string = self.location_generator(data)
            else:
                location_string = 'In the {} system'.format(data['StarSystem'])
            update['location'] = location_string
            self.parent.update_location(location_string)

        elif event == 'FSDJump':
            logging.debug('Found ' + event + '.')
            update['system'] = data['StarSystem']
            if 'Factions' in data.keys():
                update = self.faction_scraper(data, update)
            location_string = self.location_generator(data)
            update['location'] = location_string
            self.parent.update_location(location_string)

        elif event == 'Docked':
            logging.debug('Found ' + event + '.')
            update['station_name'] = data['StationName']
            update['station_faction'] = data['StationFaction']
            update['docked'] = True
            location_string = 'Docked at ' + data['StationName'] + ' in the ' + data['StarSystem'] + ' system.'
            update['location'] = location_string
            self.parent.update_location(location_string)

        elif event == 'Undocked':
            logging.debug('Found ' + event + '.')
            update['docked'] = False
            update['station_faction'] = ''
            logging.debug('Cleared station_faction.')
            update['docked'] = False
            location_string = 'Undocked from ' + data['StationName'] + \
                              ' in the ' + self.db.get_session('system') + ' system.'
            update['location'] = location_string
            self.parent.update_location(location_string)

        elif event == 'ApproachBody':
            logging.debug('Found ' + event + '.')
            location_string = 'In the {} system, in close proximity to {}.'.format(data['StarSystem'], data['Body'])
            update['location'] = location_string
            self.parent.update_location(location_string)

        elif event == 'LeaveBody':
            logging.debug('Found ' + event + '.')
            location_string = 'In the {} system, near {}.'.format(data['StarSystem'], data['Body'])
            update['location'] = location_string
            self.parent.update_location(location_string)

        elif event == 'LaunchSRV':
            logging.debug('Found ' + event + '.')
            location_string = 'Exploring {}.'.format(self.db.get_session('near_body'))
            update['location'] = location_string
            self.parent.update_location(location_string)

        elif event == 'DockSRV':
            logging.debug('Found ' + event + '.')
            location_string = 'Landed on {}.'.format(self.db.get_session('near_body'))
            update['location'] = location_string
            self.parent.update_location(location_string)

        elif event == 'SRVDestroyed':
            logging.debug('Found ' + event + '.')
            if self.db.get_session('landed'):
                location_string = 'Landed on {}.'.format(self.db.get_session('near_body'))
            else:
                location_string = 'In the {} system, in close proximity to {}.'.format(
                    self.db.get_session('system'),
                    self.db.get_session('near_body')
                )
            update['location'] = location_string
            self.parent.update_location(location_string)

        elif event == 'Touchdown':
            logging.debug('Found ' + event + '.')
            location_string = 'Landed on {}.'.format(self.db.get_session('near_body'))
            update['location'] = location_string
            update['landed'] = True
            self.parent.update_location(location_string)

        elif event == 'Liftoff':
            logging.debug('Found ' + event + '.')
            location_string = 'In the {} system, in close proximity to {}.'.format(
                self.db.get_session('system'),
                self.db.get_session('near_body')
            )
            update['location'] = location_string
            update['landed'] = False
            self.parent.update_location(location_string)

        # --- BGS events
        # Bounties / Combat Bonds
        elif event == 'RedeemVoucher':
            logging.debug('Found ' + event + '.')

            valid = self.validate(data)
            if valid != 'invalid':
                update_string = ''
                station = self.db.get_session('station_faction')
                faction = self.db.get_session('station_faction')
                state = self.db.get_session('system_factions')[faction]
                system = self.db.get_session('system')
                total = 0
                voucher = ''

                if data['Type'] == 'bounty':
                    voucher = 'bounty'
                    update_string += 'You redeemed bounties worth '
                    for faction in data['Factions']:
                        total += faction['Amount']

                elif data['Type'] == 'CombatBond':
                    voucher = 'combat'
                    update_string += 'You redeemed combat bonds worth '
                    total = data['Amount']

                elif data['Type'] in ['scannable', 'settlement']:
                    voucher = 'exploration'
                    update_string += 'You redeemed data worth '
                    total = data['Amount']

                elif data['Type'] == 'exploration':
                    voucher = 'exploration'
                    update_string += 'You redeemed exploration data worth '
                    total = data['Amount']

                amount = str('${:,}'.format(total))
                update_string += '{} credits for {} at {} in {}'.format(amount, faction, station, system)
                self.parent.update_credits(total)

                if valid == 'increase':
                    update_string += ' prolonging the state of {}.'.format(state)
                elif valid == 'decrease':
                    update_string += ' expediting the end of the {}.'.format(state)
                else:
                    update_string += '.'

                transaction[system][station][faction]['state'] = state
                transaction[system][station][faction][voucher] = {'count': 1, 'amount': total}
                self.db.file_transaction(transaction)

        else:
            logging.debug('Event ignored ({}).'.format(data['event']))
            return

        logging.debug('Storing new session details from {} event'.format(data['event']))
        logging.debug('Update: ' + str(update))
        self.db.update_session(update)

    def validate(self, data):
        logging.info('Determining validity.')
        will_effect_influence = ''
        will_decrease_duration = ''
        will_increase_duration = ''

        # Get state of faction
        faction = self.db.get_session('station_faction')
        state = self.db.get_session(['system_factions'][faction])

        logging.debug('Found {} in state {}'.format(faction, state))

        if data['event'] == 'bounty' or data['event'] == 'CombatBond':
            if state in ['Elections', 'Famine', 'Outbreak']:
                reason = 'Invalid: Redeemed {} for faction in {} state.'.format(data['event'], state)
                will_effect_influence = False
            elif state in ['Lockdown', 'CivilUnrest']:
                reason = 'Valid: Will decrease duration of current {} state.'.format(state)
                will_decrease_duration = True
            else:
                reason = 'Valid: Current state has no affect on this transaction.'
                will_effect_influence = True

        if data['event'] == 'mission' or data['event'] == 'donation':  # FIXME combat missions count here
            if state in ['War', 'Civil War', 'Famine', 'Outbreak', 'Lockdown']:
                reason = 'Invalid: Mission completed for faction in {} state.'.format(state)
                will_effect_influence = False
            else:
                reason = 'Valid: Current state has no affect on this transaction.'
                will_effect_influence = True

        if data['event'] == 'exploration' or data['event'] == 'scannable':
            if state in ['Boom', 'Expansion', 'Investment']:
                reason = 'Valid: Will increase duration of current {} state.'.format(state)
                will_increase_duration = True
            elif state in ['Bust', 'Famine', 'Outbreak']:
                reason = 'Valid: Will decrease duration of current {} state.'.format(state)
                will_decrease_duration = True
            elif state in ['War', 'CivilWar']:
                reason = 'Invalid: Redeemed exploration data for faction in state: {}'.format(state)
                will_effect_influence = False
            else:
                reason = 'Valid: Current state has no affect on this transaction.'
                will_effect_influence = True

        if data['event'] == 'trade':
            # profit_made = self.determine_profit(data)
            # if profit_made:
                if state in ['Boom']:
                    reason = 'Valid: Will increase duration of current {} state.'.format(state)
                    will_increase_duration = True
                elif state in ['Bust']:
                    reason = 'Valid: Will decrease duration of current {} state.'.format(state)
                    will_decrease_duration = True
                elif state in ['CivilUnrest']:
                    if data['Type'] in self.commodity['weapons']:
                        reason = 'Valid: Supplying weapons will increase duration of current {} state.'.format(state)
                        will_increase_duration = True
                elif state in ['Famine']:
                    if data['Type'] in self.commodity['foods']:
                        reason = 'Valid: Supplying food will decrease duration of current {} state.'.format(state)
                        will_decrease_duration = True
                elif state in ['Outbreak']:
                    if data['Type'] in self.commodity['medicines']:
                        reason = 'Valid: Supplying medicines will decrease duration of current {} state.'.format(state)
                        will_decrease_duration = True
                elif state in ['War', 'CivilWar', 'Lockdown']:
                    reason = 'Invalid: Conducted normal trade for faction in {} state.'.format(state)
                    will_effect_influence = False
                else:
                    reason = 'Valid: Current state has no affect on this transaction.'
                    will_effect_influence = True
            # else:
            #     reason = 'Valid: Current state has no affect on this transaction.'
            #     will_effect_influence = True

        if data['event'] == 'smuggled':
            # profit_made = self.determine_profit(data)
            # if profit_made == True:
                if state in ['CivilUnrest']:
                    if data['Type'] in self.commodity['weapons']:
                        reason = 'Valid: Supplying weapons will increase duration of current {} state.'.format(state)
                        will_increase_duration = True
                elif state in ['Famine']:
                    if data['Type'] in self.commodity['foods']:
                        reason = 'Valid: Supplying food will decrease duration of current {} state.'.format(state)
                        will_decrease_duration = True
                elif state in ['Outbreak']:
                    if data['Type'] in self.commodity['medicines']:
                        reason = 'Valid: Supplying medicines will decrease duration of current {} state.'.format(state)
                        will_decrease_duration = True
                elif state in ['Lockdown', 'CivilUnrest']:
                    reason = 'Valid: Smuggling will increase duration of current {} state.'.format(state)
                    will_increase_duration = True
                else:
                    reason = 'Valid: Current state has no affect on this transaction.'
                    will_effect_influence = True

        if will_increase_duration:
            logging.info(reason)
            return 'increase'
        elif will_decrease_duration:
            logging.info(reason)
            return 'decrease'
        elif not will_effect_influence:
            logging.info(reason)
            return 'invalid'
        else:
            logging.info(reason)
            return 'valid'

    # def determine_profit(self, data):
    #     buy_price = data['AvgPricePaid'] * data['Count']
    #     delta = data['TotalSale'] - buy_price
    #     if delta > 0:
    #         return True
    #     else:
    #         return False

    def location_generator(self, data):
        try:
            if 'BodyType' in data.keys():
                if data['BodyType'] == 'Null':
                    location_string = 'In the {} system'.format(data['StarSystem'])
                elif data['BodyType'] == 'Station':
                    if 'Docked' in data:
                        if data['Docked']:
                            location_string = 'Docked at ' + data['StationName'] + ' in the ' + \
                                              data['StarSystem'] + ' system.'
                    else:
                        location_string = 'Near {} station in the {} system'.format(data['Body'], data['StarSystem'])
                elif data['BodyType'] == 'Star':
                    location_string = 'Near a star in the {} system.'.format(data['StarSystem'])
                elif data['BodyType'] == 'Planet' and 'Latitude' not in data.keys():
                    location_string = 'In the {} system, near {}.'.format(data['StarSystem'], data['Body'])
                elif data['BodyType'] == 'Planet' and 'Latitude' in data.keys():
                    location_string = 'In the {} system, landed on {}.'.format(data['StarSystem'], data['Body'])
                elif data['BodyType'] == 'PlanetaryRing':
                    location_string = 'In the {} system, near the rings of {}.'.format(data['StarSystem'], data['Body'])
            elif data['event'] == 'FSDJump':
                location_string = 'In the {} system.'.format(data['StarSystem'])
        except Exception as e:
            logging.warning("Couldn't properly determine location.\n{}\nReceived data was:\n{}".format(e.message, data))
            location_string = 'Lost in space.'
            pass
        return location_string

    def faction_scraper(self, data, update):
        # Store factions present, their states, and determine if we care about any of them
        for faction in data['Factions']:
            update['system_factions'][faction['Name']] = faction['FactionState']
        logging.debug('Found factions: ' + str(update['system_factions']))

        # Search for faction presence
        if self.parent.conf['bgs']['my_faction'] in update['system_factions'].keys():
            logging.debug('Found own faction "' + self.parent.conf['bgs']['my_faction'] + '" in system.')
            update['faction_present'] = True
        else:
            update['faction_present'] = False

        # Search for ally presence
        for faction in self.parent.conf['bgs']['allied_factions']:
            if faction in update['system_factions'].keys():
                logging.debug('Found ally "' + self.parent.conf['bgs']['my_faction'] + '" in system.')
                update['faction_ally_present'] = True
            else:
                update['faction_ally_present'] = False

        # Search for enemy presence
        if self.parent.conf['bgs']['my_faction'] in update['system_factions'].keys():
            logging.debug('Found enemy "' + self.parent.conf['bgs']['my_faction'] + '" in system.')
            update['faction_present'] = True
        else:
            update['faction_present'] = False

        return update


def makehash():
    return defaultdict(makehash)
