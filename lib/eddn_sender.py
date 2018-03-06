from . import log
from requests_futures.sessions import FuturesSession
import threading, queue
import configparser
import json
from os import path
import glob
from datetime import datetime
from time import sleep

#https://eddn.edcd.io:4430/upload/ POST

class EDDN_dispatcher(threading.Thread):
    def __init__(self, journal_path, config):
        log.info('Initialsing EDDN dispatcher.')
        super(EDDN_dispatcher, self).__init__()
        self._stop_event = threading.Event()
        self.bgs_version = config['General']['version']
        self.journal_path = journal_path

    def run(self):
        try:
            while not self.stopped():
                self.shipyard_monitor()
                self.outfitting_monitor()
                self.market_monitor()
                sleep(1)
        except Exception as e:
            log.exception('EDDN Dispatcher exception during runtime.', e)
            pass

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def receive_response(self, _, response):
        try:
            if response.ok:
                log.info('EDDN Dispatcher successfully posted data.')
            else:
                log.warning('EDDN Dispatcher recieved a bad response from posted data.')
                log.warning(str(response.reason))
                log.warning(str(response))

        except Exception as e:
            log.exception('EDDN Dispatcher errored.. somehow.. getting a response.', e)

    '''-------------------------------------------------------------------------

    File pollers - Here we check freshness of data in stored .json files and
    send payloads to EDDN as required, with care to *try* and not send dupes.

    -------------------------------------------------------------------------'''

    def shipyard_monitor(self):
        try:
            filename = max(glob.iglob(path.join(self.journal_path, 'Shipyard.json')), key=path.getctime)
            with open(filename, 'r') as f:
                _list = f.readlines() # Frontier decided to put newlines everywhere so we get a list
                _lines = ''.join(_list)
                _json = json.loads(_lines)

            # see how stale this timestamp is
            timestamp_now = datetime.utcnow()
            timestamp_file = datetime.strptime(_json['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
            # subtract now from timestamp in file
            # if there's more than 30 seconds between them, ignore
            timestamp_drift = timestamp_now - timestamp_file

            #log.debug('EDDN Dispatcher calculated data timestamp drift between json and realtime for Shipyard.json: {}'.format(timestamp_drift.total_seconds())) #DEBUG
            if not timestamp_drift.total_seconds() > 5:
                # Check to see if this data matches data previously stored in this class
                if hasattr(self, 'old_shipyard_lines'):
                    if self.old_shipyard_lines == _json:
                        #log.debug('EDDN Dispatcher has already processed this Shipyard.json. Ignoring.')
                        return
                else:
                    # We'll store the json, just to try and ensure we don't double up or spam data
                    self.old_shipyard_lines = _json
                    # Construct and send the payload
                    self.send_shipyard(_json)
            #else:
                #log.debug('EDDN Dispatcher found stale Shipyard data.')
        except Exception as e:
            log.exception('EDDN Dispatcher encountered error trying to post Shipyard data.', e)
            pass


    # DID YOU JUST ACCUSE ME OF COPYING AND PASTING BECAUSE I WAS TOO LAZY TO WRITE A SMALL FUNCTION?!
    def outfitting_monitor(self):
        try:
            filename = max(glob.iglob(path.join(self.journal_path, 'Outfitting.json')), key=path.getctime)
            with open(filename, 'r') as f:
                _list = f.readlines() # Frontier decided to put newlines everywhere so we get a list
                _lines = ''.join(_list)
                _json = json.loads(_lines)

            # see how stale this timestamp is
            timestamp_now = datetime.utcnow()
            timestamp_file = datetime.strptime(_json['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
            # subtract now from timestamp in file
            # if there's more than 30 seconds between them, ignore
            timestamp_drift = timestamp_now - timestamp_file

            #log.debug('EDDN Dispatcher calculated data timestamp drift between json and realtime for Outfitting.json: {}'.format(timestamp_drift.total_seconds())) #DEBUG
            if not timestamp_drift.total_seconds() > 5:
                # Check to see if this data matches data previously stored in this class
                if hasattr(self, 'old_outfitting_lines'):
                    if self.old_outfitting_lines == _json:
                        #log.debug('EDDN Dispatcher has already processed this Outfitting.json. Ignoring.')
                        return
                else:
                    # We'll store the json, just to try and ensure we don't double up or spam data
                    self.old_outfitting_lines = _json
                    # Construct and send the payload
                    self.send_outfitting(_json)
            # else:
            #     log.debug('EDDN Dispatcher found stale Outfitting data.')
        except Exception as e:
            log.exception('EDDN Dispatcher encountered error trying to post Outfitting data.', e)
            pass


    # DID YOU JUST ACCUSE ME OF COPYING AND PASTING BECAUSE I WAS TOO LAZY TO WRITE A SMALL FUNCTION?! AGAIN?!
    def market_monitor(self):
        try:
            filename = max(glob.iglob(path.join(self.journal_path, 'Market.json')), key=path.getctime)
            with open(filename, 'r') as f:
                _list = f.readlines() # Frontier decided to put newlines everywhere so we get a list
                _lines = ''.join(_list)
                _json = json.loads(_lines)

            # see how stale this timestamp is
            timestamp_now = datetime.utcnow()
            timestamp_file = datetime.strptime(_json['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
            # subtract now from timestamp in file
            # if there's more than 30 seconds between them, ignore
            timestamp_drift = timestamp_now - timestamp_file

            #log.debug('EDDN Dispatcher calculated data timestamp drift between json and realtime for Market.json: {}'.format(timestamp_drift.total_seconds())) #DEBUG
            if not timestamp_drift.total_seconds() > 5:
                # Check to see if this data matches data previously stored in this class
                if hasattr(self, 'old_market_lines'):
                    if self.old_market_lines == _json:
                        #log.debug('EDDN Dispatcher has already processed this Market.json. Ignoring.')
                        return
                else:
                    # We'll store the json, just to try and ensure we don't double up or spam data
                    self.old_market_lines = _json
                    # Construct and send the payload
                    self.send_market(_json)
            #else:
                #log.debug('EDDN Dispatcher found stale Market data.')
        except Exception as e:
            log.exception('EDDN Dispatcher encountered error trying to post Market data.', e)
            pass


    '''-------------------------------------------------------------------------

    POST functions  .... for posting. To EDDN.

    -------------------------------------------------------------------------'''

    def send_shipyard(self, data):
        session = FuturesSession()
        log.info('EDDN Dispatcher sending Shipyard payload.')
        log.debug('EDDN Dispatcher Raw Shipyard Data: {}'.format(str(data)))

        payload = {
          "$schemaRef": "https://eddn.edcd.io/schemas/shipyard/2/test",
          "header": {
            "uploaderID": "Anon",
            "softwareName": "BGS Companion",
            "softwareVersion": self.bgs_version
          },
          "message": {
            "systemName": data['StarSystem'],
            "stationName": data['StationName'],
            "timestamp": data['timestamp'],
            "ships": []
          }
        }

        for ship in data['PriceList']:
            payload['message']['ships'].append(ship['ShipType'])

        payload = json.dumps(payload)
        log.debug('EDDN Dispatcher Shipyard Data Payload: {}'.format(str(payload)))
        r = session.post('https://eddn.edcd.io:4430/upload/', data=payload, background_callback=self.receive_response)
        r.result()


    def send_outfitting(self, data):
        session = FuturesSession()
        log.info('EDDN Dispatcher sending Outfitting payload.')
        log.debug('EDDN Dispatcher Raw Outfitting Data: {}'.format(str(data)))

        payload = {
          "$schemaRef": "https://eddn.edcd.io/schemas/outfitting/2/test",
          "header": {
            "uploaderID": "Anon",
            "softwareName": "BGS Companion",
            "softwareVersion": self.bgs_version
          },
          "message": {
            "systemName": data['StarSystem'],
            "stationName": data['StationName'],
            "timestamp": data['timestamp'],
            "modules": []
          }
        }

        for module in data['Items']:
            if 'PlanetApproachSuite' not in module['Name'] and 'sku' not in module['Name']:
                if module['Name'].lower().startswith('hpt_') or module['Name'].lower().startswith('int_') or '_armour_' in module['Name'].lower():
                    payload['message']['modules'].append(module['Name'].title()) #Have to add title() due to EDDN regex filter

        payload = json.dumps(payload)
        log.debug('EDDN Dispatcher Outfitting Data Payload: {}'.format(str(payload)))
        r = session.post('https://eddn.edcd.io:4430/upload/', data=payload, background_callback=self.receive_response)
        r.result()


    def send_market(self, data):
        session = FuturesSession()
        log.info('EDDN Dispatcher sending Market payload.')
        log.debug('EDDN Dispatcher Raw Market Data: {}'.format(str(data)))

        payload = {
          "$schemaRef": "https://eddn.edcd.io/schemas/commodity/3/test",
          "header": {
            "uploaderID": "Anon",
            "softwareName": "BGS Companion",
            "softwareVersion": self.bgs_version
          },
          "message": {
            "systemName": data['StarSystem'],
            "stationName": data['StationName'],
            "timestamp": data['timestamp'],
            "commodities": []
          }
        }

        for commodity in data['Items']:
            c_dict = { 'name': commodity['Name'],
                       'meanPrice': commodity['MeanPrice'],
                       'buyPrice': commodity['BuyPrice'],
                       'stock': commodity['Stock'],
                       'stockBracket': commodity['StockBracket'],
                       'sellPrice': commodity['SellPrice'],
                       'demand': commodity['Demand'],
                       'demandBracket': commodity['DemandBracket']
                       }

        for commodity in data['Items']:
            if 'legality' not in commodity.keys(): ##REVIEW
                    payload['message']['commodities'].append(c_dict)

        payload = json.dumps(payload)
        log.debug('EDDN Dispatcher Market Data Payload: {}'.format(str(payload)))
        r = session.post('https://eddn.edcd.io:4430/upload/', data=payload, background_callback=self.receive_response)
        r.result()
