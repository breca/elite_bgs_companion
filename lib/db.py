from . import log
import sqlite3
from collections import defaultdict
from os import remove as careful_delete
from os import path

# connect to db
class DatabaseAgent():
    def __init__(self):
        log.debug('Starting Database agent.')
        try:
            self.conn = sqlite3.connect('etc\companion.db', check_same_thread=False)
            self.conn.row_factory = self.dict_factory
            self.cursor = self.conn.cursor()
            log.debug('Database connection established.')
        except Exception as e:
            log.exception('Exception caught connecting to database.', e)
            exit(1)

        self.check_setup()


    # close db
    def disconnect(self):
        try:
            log.info('Closing database.')
            self.conn.close()
        except Exception as e:
            log.exception('Exception occured closing the database.', e)


    '''###########################################
    #              db checks / setup
    ###########################################'''

    # setup db table
    def check_setup(self):
        try:
            log.info('Checking database setup.')
            sql = 'SELECT sql FROM sqlite_master '
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            log.debug('DB Setup check returned: ' + str(result))
            if len(result) == 0:
                self.setup()
            else:
                # If there are indeed databases, make sure the schema is up to snuff
                schema_file = path.isfile('schema.dat')
                if schema_file:
                    with open('schema.dat', 'r') as f:
                        saved = f.readlines()
                        schema_check = eval(saved[0])
                else:
                    schema_check = 'Missing'

                if result != schema_check:
                    log.info('Recreating database.')
                    log.debug('Old schema was:\n{}\nNew schema:\n{}'.format(result, schema_check))
                    for i in 'voucher', 'mission', 'session':
                        log.debug('Dropping table {}'.format(i))
                        sql = 'drop table {}'.format(i)
                        self.cursor.execute(sql)
                        self.conn.commit()
                    if schema_file != 'Missing':
                        careful_delete('schema.dat')
                    self.setup()
                else:
                    log.info('Database OK.')
        except Exception as e:
            log.exception('Exception occured checking database setup.', e)
            pass


    # setup db table
    def setup(self):
        try:
            log.info('Creating BGS table.')
            sql = '''CREATE TABLE IF NOT EXISTS voucher (system text, station text, faction text, faction_state text default 'N/A', type text, amount integer, commodity_traded text default 'N/A', ts text unique, processed boolean default 'False')'''
            self.cursor.execute(sql)
            self.conn.commit()
            log.info('BGS voucher table created.')
            sql = '''CREATE TABLE IF NOT EXISTS mission (mission_id int unique default(0), mission_type text, mission_influence text, mission_giver_system text, mission_giver_station text, mission_giver_faction text, mission_amount int default 0, mission_state text default 'accepted', processed text default 'False')'''
            self.cursor.execute(sql)
            self.conn.commit()
            log.info('BGS mission table created.')
            sql = '''CREATE TABLE IF NOT EXISTS session (journal_file text, journal_byte_offset int, commander_name text, credits int, ship_name text, ship text, game_mode text, game_mode_group text, star_system text, system_is_target_faction_owned text, system_pop int, near_body text, near_body_type text, docked text, landed text, station_name text, station_faction text, target_faction_state text, old_target_faction_state text, location text, in_srv text)'''
            self.cursor.execute(sql)
            self.conn.commit()
            log.info('Companion session table created.')
            # Backup our current schema for version checks
            sql = 'SELECT sql FROM sqlite_master'
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            with open('schema.dat', 'w') as f:
                f.write(str(result))
            self.check_setup()
        except Exception as e:
            log.exception('Exception occured during table creation.', e)
            exit(2)


    '''###########################################
    #            session data handling
    ###########################################'''

    # squash previous session data (called on exit)
    def save_session_data(self, stats):
        log.info('Updating session data in DB.')
        try:
            log.debug('Dumping old session data')
            sql = '''delete from session'''
            self.cursor.execute(sql)
            self.conn.commit()
            offset = stats['journal_byte_offset'] #+ 2
            # if len(runtime['game_mode_group']) < 0:
            log.debug('Inserting current session stats.')
            sql = '''insert into session values ("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'''.format(
                stats['journal_file'],
                offset, #accomodates for expected newline if this same journal gets updated later
                stats['commander_name'],
                stats['credits'],
                stats['ship_name'],
                stats['ship'],
                stats['game_mode'],
                stats['game_mode_group'],
                stats['star_system'],
                stats['system_is_target_faction_owned'],
                stats['system_pop'],
                stats['near_body'],
                stats['near_body_type'],
                stats['docked'],
                stats['landed'],
                stats['station_name'],
                stats['station_faction'],
                stats['target_faction_state'],
                stats['old_target_faction_state'],
                stats['location'],
                stats['in_srv']
            )
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            log.exception('Error occured updating session stats in database.', e)
            log.debug(sql)
        else:
            log.info('Session stats successfully entered into database.')
            log.debug(sql)
            self.disconnect()


    def lookup_session_data(self):
        log.info('Fetching session data from DB.')
        try:
            sql = '''select * from session'''
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            return results
        except Exception as e:
            log.exception('Could not fetch session data from DB.', e)
        else:
            if len(results) > 0:
                log.info('Session stats successfully entered into database.')
            else:
                log.info('Could not find any old session stats.')


    '''###########################################
    #             mission handling
    ###########################################'''

    # update stored mission status
    def update_mission_status(self, status):
        try:
            log.info('Updating mission ({}) status ({}) in BGS mission table.'.format(status['mission']['mission_id'], status['mission']['status']))
            if status['mission']['status'] == 'completed':
                sql = '''update mission set mission_state = "{}", mission_amount = "{}" where mission_id is "{}"'''.format(status['mission']['status'], status['mission']['amount'], status['mission']['mission_id'])
            else:
                sql = '''update mission set mission_state = "{}" where mission_id is "{}"'''.format(status['status'], status['mission']['mission_id'])
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            log.exception('Failed to update mission {} status in BGS mission table'.format(status['mission']['mission_id']), e)
            exit(5)

    # insert bgs mission data
    def insert_mission(self, update, runtime):
        try:
            if not update['mission']['faction']:
                raise ValueError('Update was:\n' + str(update) + '\nRuntime:\n' + str(runtime))
            log.info('Attempting to insert mission [{}] into BGS mission table.'.format(update['mission']['mission_id']))
            sql = '''insert or ignore into mission values ("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'''.format(
                update['mission']['mission_id'],
                update['mission']['type'],
                update['mission']['influence'],
                runtime['star_system'],
                runtime['station_name'],
                update['mission']['faction'],
                0,
                'accepted',
                'False'
                )
            self.cursor.execute(sql)
            self.conn.commit()
            log.info('BGS mission data for {} in {}, {} ({}) inserted into database.'.format(
                update['mission']['faction'],
                runtime['station_name'],
                runtime['star_system'],
                update['mission']['type'],
                ))
        except ValueError as e:
            log.exception('Faction data not present, refusing to insert!', e)
            pass
        except Exception as e:
            log.exception('Exception occured inserting BGS mission data into table.', e)
            exit(3)

    # return mission facts
    def lookup_mission(self, m_id):
        log.info('Fetching mission [{}] facts from database.'.format(m_id))
        sql = 'select mission_giver_system, mission_giver_station, mission_giver_faction, mission_influence from mission where mission_id is "{}"'.format(m_id)
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        try:
            log.debug('Found result: '+str(res))
            a = res[0]['mission_giver_system']
            b = res[0]['mission_giver_station']
            c = res[0]['mission_giver_faction']
            d = res[0]['mission_influence']
            return a, b, c
        except Exception as e:
            log.warning('Could not find mission ' + str(m_id) +'! May be already processed.')
            log.debug(e)
            # this CAN happen if the mission is already processed
            pass


    '''###########################################
    #             voucher handling
    ###########################################'''

    # insert bgs voucher data
    def insert_voucher(self, update, runtime):
        if 'commodity' not in update['voucher'].keys():
            update['voucher']['commodity'] = 'N/A'
        try:
            log.info('Inserting {} reward into BGS voucher table.'.format(update['voucher']['type']))
            log.debug('Attempting to insert voucher data [{}] into BGS voucher table.'.format(update))
            if update['voucher']['type'] not in ['CombatBond', 'bounty']:
                if not runtime['station_faction']:
                    raise ValueError('Update was:\n' + str(update) + '\nRuntime:\n' + str(runtime))
                sql = '''insert or ignore into voucher values ("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'''.format(
                    runtime['star_system'],
                    runtime['station_name'],
                    runtime['station_faction'],
                    runtime['target_faction_state'],  #FIXME this needs to be udpated with the state of the STATION's faction.. I think.
                    update['voucher']['type'],
                    int(update['voucher']['amount']),
                    update['voucher']['commodity'],
                    update['voucher']['timestamp'],
                    'False'
                    )
                self.cursor.execute(sql)
                self.conn.commit()
                log.info('Voucher inserted.')
                log.debug('BGS voucher data for {} in {}, {} ({}, {}) inserted into database.'.format(
                    runtime['station_faction'],
                    runtime['station_name'],
                    runtime['star_system'],
                    update['voucher']['type'],
                    update['voucher']['amount']
                ))
            else:
                for faction in update['voucher']['factions']:
                    log.info('Inserting {} reward into BGS voucher table.'.format(update['voucher']['type']))
                    log.debug('Attempting to insert voucher data [{}] into BGS voucher table.'.format(update))
                    if not faction[0]:
                        raise ValueError('Update was:\n' + str(update) + '\nRuntime:\n' + str(runtime))
                    sql = '''insert or ignore into voucher values ("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'''.format(
                        runtime['star_system'],
                        runtime['station_name'],
                        faction[0],
                        runtime['target_faction_state'],  #FIXME this needs to be udpated with the state of the STATION's faction
                        update['voucher']['type'],
                        faction[1],
                        update['voucher']['commodity'],
                        update['voucher']['timestamp'],
                        'False'
                        )
                    self.cursor.execute(sql)
                    self.conn.commit()
                    log.info('Voucher inserted.')
                    log.debug('BGS voucher data for {} in {}, {} ({}, {}) inserted into database.'.format(
                        runtime['station_faction'],
                        runtime['station_name'],
                        runtime['star_system'],
                        update['voucher']['type'],
                        faction[1]
                    ))
        except ValueError as e:
            log.exception('Faction data not present, refusing to insert!', e)
            pass
        except Exception as e:
            log.exception('Exception occured inserting BGS voucher data into table.', e)
            exit(3)

    '''###########################################
    #
    #         marking data as 'processed'
    #
    #   instead of just outright deletion,
    #   this will ensure none of this data
    #   pops up under the BGS report, but
    #   retains it so it can be later synced
    #   to a server, etc.
    #   Actual deletion can occur after sync
    #
    #  Note to self: need to make sure that
    #  goes straight to the end of the journal
    #  and that the application checks that Elite
    #  is running or this might be problematic
    #
    ###########################################'''

    # delete bgs data
    def mark_processed(self, ids):
        # super hacky way to delete from different tables, oh my god
        for i in ids:
            try:
                if len(str(i)) <8 and not i ==0:
                    sql = 'update voucher set processed = "True" where processed is "False" and rowid is {}'.format(i)
                elif len(str(i)) >8:
                    sql = 'update mission set processed = "True" where processed is "False" and mission_id is {}'.format(i)

                log.debug('Marking shown BGS data {} as \'processed\' in BGS table.'.format(i))
                self.cursor.execute(sql)
                self.conn.commit()
            except Exception as e:
                log.exception('Exception occured marking data as processed.', e)
                exit(4)
        log.info('All BGS data marked as processed.')

    '''###########################################
    #          BGS report generation
    ###########################################'''

    # get bgs data
    def get_bgs(self, runtime):
        try:
            log.info('Fetching data from tables.')
            log.debug('Fetching voucher data from BGS table.')
            sql = '''select rowid, amount, commodity_traded, type, faction, faction_state, station, system from voucher where processed is "False"'''.format(runtime['target_faction'])
            #sql = 'select * from voucher'
            self.cursor.execute(sql)
            v_results = self.cursor.fetchall()
            log.debug('Collected BGS voucher data from database:\n'+ str(v_results))
            # return results
        except Exception as e:
            log.exception('Exception occured polling database for BGS voucher data.', e)
            exit(4)
        try:
            log.debug('Fetching mission data from BGS table.')
            sql = '''select mission_id as rowid, mission_amount as amount, mission_type as type, mission_giver_faction as faction, mission_giver_station as station, mission_giver_system as system from mission where mission_state is not 'accepted' and processed is "False"'''.format(runtime['target_faction'])
            #sql = 'select * from mission'
            self.cursor.execute(sql)
            m_results = self.cursor.fetchall()
            log.debug('Collected BGS mission data from database:\n'+ str(m_results))
            # return results
        except Exception as e:
            log.exception('Exception occured polling database for BGS mission data.', e)
            exit(4)


        log.debug('BGS report generator constructing data')
        # here we munge it all into a data structure we can easily iterate over
        # report_dict (end state example)
        # report_dict = { '37 Librae': {'Roosa Market': { 'Radio Sidewinder Crew': { 'state': 'N/A'
        #                                                                            'transaction': {
        #                                                                                'bounty': [500, [1,5,23]],  # <total amount, [<table row_ids>]
        #                                                                                'trade': [500, ['foo'], [3,6,7]],  # <profits, [<commodities>], [<table row_ids>]
        #                                                                                'smuggled': [500, ['foo'], [2,8,4]],
        #                                                                                'mission': [500, ['foo'], [2,8,4]],
        #                                                                                'donation': [500, [2,8,4]], # mission_ids instead of rowids
        #                                                                                 },
        #
        #                                                                         }
        #                                             }
        #                            }
        #             }

        report_dict = defaultdict(dict)
        if len(v_results) >0:
            log.debug('BGS report generator processing vouchers')
            for entry in v_results:
                # horribly inelegant dict traversal
                # create system dict if it doesn't exist
                if entry['system'] in report_dict.keys():
                    log.debug('BGS report generator found existing system') ##DEBUG
                else:
                    log.debug('BGS report generator creating new system') ##DEBUG
                    report_dict[entry['system']] = {}
                # create station dict if it doesn't exist
                if entry['station'] in report_dict[entry['system']].keys():
                    log.debug('BGS report generator found existing station') ##DEBUG
                else:
                    log.debug('BGS report generator creating new station')
                    report_dict[entry['system']][entry['station']] = {}
                # create faction dict if it doesn't exist
                if entry['faction'] in report_dict[entry['system']][entry['station']].keys():
                    log.debug('BGS report generator found existing station faction') ##DEBUG
                else:
                    log.debug('BGS report generator creating new station faction')
                    report_dict[entry['system']][entry['station']][entry['faction']] = {'transaction': {}}
                # set faction state if it exists
                if entry['faction_state'] != 'N/A':
                    log.debug('BGS report generator updating system faction state')
                    if entry['faction_state'] in report_dict[entry['system']][entry['station']][entry['faction']].keys():
                        report_dict[entry['system']][entry['station']][entry['faction']][entry['faction_state']] = entry['faction_state']
                # create voucher dict if not present
                if entry['type'] not in report_dict[entry['system']][entry['station']][entry['faction']]['transaction'].keys():
                    log.debug('BGS report generator creating new voucher of type '+ entry['type'])
                    report_dict[entry['system']][entry['station']][entry['faction']]['transaction'][entry['type']] = {}
                # add data to voucher dict
                if entry['type'] not in ['smuggled', 'trade']:
                    if len(report_dict[entry['system']][entry['station']][entry['faction']]['transaction'][entry['type']]) <2:
                        log.debug('BGS report generator determined this is a fresh transaction')
                        report_dict[entry['system']][entry['station']][entry['faction']]['transaction'][entry['type']] = [0, []]
                    log.debug('BGS report generator adding this ' + entry['type'] + ' amount to total for this transaction type')
                    report_dict[entry['system']][entry['station']][entry['faction']]['transaction'][entry['type']][0] += entry['amount']
                    report_dict[entry['system']][entry['station']][entry['faction']]['transaction'][entry['type']][-1].append(entry['rowid'])
                else:
                    # check to see if this is a new entry
                    if len(report_dict[entry['system']][entry['station']][entry['faction']]['transaction'][entry['type']]) <2:
                        log.debug('BGS report generator determined this is a fresh trade transaction')
                        update = [entry['amount'], [entry['commodity_traded']], [entry['rowid']]]
                        report_dict[entry['system']][entry['station']][entry['faction']]['transaction'][entry['type']] = update
                    else:
                        log.debug('BGS report generator adding this ' + entry['type'] + ' amount to total for this transaction type')
                        report_dict[entry['system']][entry['station']][entry['faction']]['transaction'][entry['type']][0] += entry['amount']
                        if entry['commodity_traded'] not in report_dict[entry['system']][entry['station']][entry['faction']]['transaction'][entry['type']][1]:
                            report_dict[entry['system']][entry['station']][entry['faction']]['transaction'][entry['type']][1].append(entry['commodity_traded'])
                        report_dict[entry['system']][entry['station']][entry['faction']]['transaction'][entry['type']][-1].append(entry['rowid'])

        if len(m_results) >0:
            for entry in m_results:
                log.debug('BGS report generator processing mission')
                # horribly inelegant dict traversal
                # create system dict if it doesn't exist
                if entry['system'] in report_dict.keys():
                    log.debug('BGS (mission) report generator found existing system') ##DEBUG
                else:
                    log.debug('BGS report generator creating new system') ##DEBUG
                    report_dict[entry['system']] = {}
                # create station dict if it doesn't exist
                if entry['station'] in report_dict[entry['system']].keys():
                    log.debug('BGS (mission) report generator found existing station') ##DEBUG
                else:
                    log.debug('BGS (mission) report generator creating new station')
                    report_dict[entry['system']][entry['station']] = {}
                # create faction dict if it doesn't exist
                if entry['faction'] in report_dict[entry['system']][entry['station']].keys():
                    log.debug('BGS report (mission) generator found existing station faction') ##DEBUG
                else:
                    log.debug('BGS report (mission) generator creating new station faction')
                    report_dict[entry['system']][entry['station']][entry['faction']] = {'transaction': {}}
                # set faction state if it exists
                if 'faction_state' in entry.keys():
                    if entry['faction_state'] != 'N/A':
                        log.debug('BGS report (mission) generator updating system faction state')
                        if entry['faction_state'] in report_dict[entry['system']][entry['station']][entry['faction']].keys():
                            report_dict[entry['system']][entry['station']][entry['faction']][entry['faction_state']] = entry['faction_state']
                # create voucher dict if not present
                if entry['type'] not in report_dict[entry['system']][entry['station']][entry['faction']]['transaction'].keys():
                    log.debug('BGS report (mission) generator creating new voucher of type '+ entry['type'])
                    report_dict[entry['system']][entry['station']][entry['faction']]['transaction'][entry['type']] = {}
                # add data to voucher dict
                if len(report_dict[entry['system']][entry['station']][entry['faction']]['transaction'][entry['type']]) <2:
                    log.debug('BGS report generator determined this is a fresh mission type')
                    report_dict[entry['system']][entry['station']][entry['faction']]['transaction'][entry['type']] = [0, []]
                log.debug('BGS report generator adding this ' + entry['type'] + ' amount to total for this transaction type')
                report_dict[entry['system']][entry['station']][entry['faction']]['transaction'][entry['type']][0] += entry['amount']
                report_dict[entry['system']][entry['station']][entry['faction']]['transaction'][entry['type']][-1].append(entry['rowid'])

        log.debug('Final BGS report :\n'+ str(report_dict))
        return report_dict



    '''###########################################
    #           other db functions
    ###########################################'''

    # return dict from results, literally lifted from python3 sqlite3 docs
    # https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.row_factory
    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
