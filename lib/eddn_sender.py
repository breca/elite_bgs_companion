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
        super(EDDN_dispatcher, self).__init__()
        self._stop_event = threading.Event()
        self.bgs_version = config['General']['version']
        self.journal_path = journal_path

    def run(self):
        try:
            while not self.stopped():
                self.shipyard_monitor()
                sleep(1)
        except Exception as e:
            log.exception('EDDN Dispatcher exception during runtime.', e)
            pass

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def receive_response(self, response):
        try:
            print(str(response)) ##DEBUG
            log.info('Recieved response from EDDN: {}'.format(str(response)))
        except Exception as e:
            log.exception('EDDN Dispatcher errored.. somehow.. getting a response.', e)

    def shipyard_monitor(self):
        try:
            filename = max(glob.iglob(path.join(self.journal_path, 'Shipyard.json')), key=path.getctime)
            with open(filename, 'r') as f:
                _list = f.readlines() # Frontier decided to put newlines everywhere so we get a list
                _lines = ''.join(_list)
                #log.debug('LINES: \n{}'.format(str(_lines))) #DEBUG
                _json = json.loads(_lines)
                #print(str(_json)) #DEBUG

            # see how stale this timestamp is
            timestamp_now = datetime.utcnow()
            timestamp_file = datetime.strptime(_json['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
            # subtract now from timestamp in file
            # if there's more than 30 seconds between them, ignore
            timestamp_drift = timestamp_now - timestamp_file

            #print(str(timestamp_drift.total_seconds())) #DEBUG
            log.debug('EDDN Dispatcher calculated data timestamp drift between json and realtime for Shipyard.json: {}'.format(timestamp_drift.total_seconds())) #DEBUG
            if not timestamp_drift.total_seconds() > 5:
            #if timestamp_drift.total_seconds(): ##DEBUG FIXME
                # Check to see if this data matches data previously stored in this class
                if hasattr(self, 'old_shipyard_lines'):
                    #print(str(self.old_shipyard_lines))
                    if self.old_shipyard_lines == _json:
                        log.debug('EDDN Dispatcher has already processed this Shipyard.json. Ignoring.')
                        return
                else:
                    # We'll store the json, just to try and ensure we don't double up or spam data
                    self.old_shipyard_lines = _json
                    # Construct and send the payload
                    self.send_shipyard(_json)
            else:
                log.debug('EDDN Dispatcher found stale Shipyard data.')
        except Exception as e:
            log.exception('EDDN Dispatcher encountered error trying to post Shipyard data.', e)
            pass


    def send_shipyard(self, data):
        session = FuturesSession()
        log.info('EDDN Dispatcher sending Shipyard payload.')
        log.debug('EDDN Dispatcher Raw Shipyard Data: {}'.format(str(data)))

        payload = {
          "$schemaRef": "https://eddn.edcd.io/schemas/shipyard/2/test",
          "header": {
            "uploaderID": "Kalis",
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
        log.debug('EDDN Dispatcher Final Shipyard Payload: {}'.format(str(payload)))
        r = session.post('https://eddn.edcd.io:4430/upload/', data=payload, background_callback=self.receive_response)
        #r = session.post('https://wiki.hiteklolife.net', data=payload, background_callback=self.receive_response)
        r.result()

        # def outfitting(self, data):
        #     try:
        #         session = FuturesSession()
        #         payload = {
        #           "$schemaRef": "https://eddn.edcd.io/schemas/outfitting/2",
        #           "header": {
        #             "uploaderID": "Anon",
        #             "softwareName": "BGS Companion",
        #             "softwareVersion": self.bgs_version
        #           },
        #           "message": {
        #             "systemName": data['StationName'],
        #             "stationName": data['StationName'],
        #             "timestamp": data['timestamp'],
        #             "modules": []
        #           }
        #         }
        #
        #         for module in data['Items']:
        #             payload['message']['modules'].append(data['Name'])
        #
        #         r = session.post('https://eddn.edcd.io:4430/upload/', data=payload, background_callback=self.receive_response)
        #         r.result()
        #     except Exception as e:
        #         log.exception('Exception occured sending outfitting payload to EDDN', e)
        #         pass


    # def outfitting_monitor(self):
    #     outfit = max(glob.iglob(path.join(journal_path, 'Outfitting.json'), key=path.getctime))
    #     with open(outfit, 'r') as f:
    #         outfit_lines = f.readlines()
    #     if not hasattr(self, 'old_outfit_lines'):
    #         log.info('EDDN Dispatcher found new Outfitting file.')
    #         self.old_outfit_lines = outfit_lines
    #     else:
    #         if self.old_outfit_lines != outfit_lines:
    #             self.payload.outfitting(old_outfit_lines)
    #             self.old_outfit_lines = outfit_lines
    #
    #
    # def market_monitor(self):





        # def market(self, data):
        #     try:
        #         payload = {
        #           "$schemaRef": "https://eddn.edcd.io/schemas/commodity/3",
        #           "header": {
        #             "uploaderID": "Anon",
        #             "softwareName": "BGS Companion",
        #             "softwareVersion": config['General']['Version']
        #           },
        #           "message": {
        #             "systemName": data['StationName'],
        #             "stationName": data['StationName'],
        #             "timestamp": data['timestamp'],
        #             "commodities": []
        #           }
        #         }
        #
        #         for commodity in data['Items']:
        #             c_dict = { 'name': commodity['Name'],
        #                        'meanPrice': commodity['MeanPrice'],
        #                        'buyPrice': commodity['BuyPrice'],
        #                        'stock': commodity['Stock'],
        #                        'stockBracket': commodity['StockBracket'],
        #                        'sellPrice': commodity['SellPrice'],
        #                        'demand': commodity['Demand'],
        #                        'demandBracket': commodity['DemandBracket']
        #                        }
        #             payload['commodities'].append(c_dict)
        #     except Exception as e:
        #         log.exception('Exception occured sending market payload to EDDN', e)
        #         pass
        #
