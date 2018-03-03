from . import log
from requests_futures.sessions import FuturesSession
import threading, queue
import configparser
import json

https://eddn.edcd.io:4430/upload/ POST

class EDDN_dispatcher(threading.Thread):
    def __init__(self, journal_path):
        super(EDDN_dispatcher, self).__init__()
        self._stop_event = threading.Event()

    def run(self):



    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


    def shipyard_monitor(self):
        try:
            filename = max(glob.iglob(path.join(journal_path, 'Shipyard.json'), key=path.getctime))
            with open(filename, 'r') as f:
                # get the first line - always the timestamp
                _line = f.readline()
                _json = json.loads(_line)

            # see how stale this timestamp is
            timestamp_now = datetime.strftime(datetime.utcnow())
            ###stale_time = timestamp_now.update(second=timestamp_now.second() + 30)
            timestamp_file = datetime.strptime(_line{'timestamp'], '%Y-%m-%dT%H:%M:%SZ')
            # subtract now from timestamp in file
            # if there's more than 30 seconds between them, ignore
            timestamp_drift = timestamp_now - timestamp_file

            if not timestamp_drift.total_seconds() > 30:
                if self.old_shipyard_lines != shipyard_lines:
                    self.payload.shipyard(shipyard_lines)
                    self.old_shipyard_lines = shipyard_lines


    def outfitting_monitor(self):
        outfit = max(glob.iglob(path.join(journal_path, 'Outfitting.json'), key=path.getctime))
        with open(outfit, 'r') as f:
            outfit_lines = f.readlines()
        if not hasattr(self, 'old_outfit_lines'):
            log.info('EDDN Dispatcher found new Outfitting file.')
            self.old_outfit_lines = outfit_lines
        else:
            if self.old_outfit_lines != outfit_lines:
                self.payload.outfitting(old_outfit_lines)
                self.old_outfit_lines = outfit_lines


    def market_monitor(self):




    def payload(self, data):
        def post(self, payload):




        def outfitting(self, data):
            try:
                session = FuturesSession()
                payload = {
                  "$schemaRef": "https://eddn.edcd.io/schemas/commodity/3",
                  "header": {
                    "uploaderID": "Anon",
                    "softwareName": "BGS Companion",
                    "softwareVersion": "0.9b"
                  },
                  "message": {
                    "systemName": data['StationName'],
                    "stationName": data['StationName'],
                    "timestamp": data['timestamp'],
                    "modules": []
                  }
                }

                for module in data['Items']:
                    payload['message']['modules'].append(data['Name'])

                r = session.post('https://eddn.edcd.io:4430/upload/', data=payload, background_callback=receive_response)
            except Exception as e:
                log.exception('Exception occured sending outfitting payload to EDDN', e)
                pass


        def market(self, data):
            payload = {
              "$schemaRef": "https://eddn.edcd.io/schemas/commodity/3",
              "header": {
                "uploaderID": "Anon",
                "softwareName": "BGS Companion",
                "softwareVersion": "0.9b"
              },
              "message": {
                "systemName": data['StationName'],
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
                payload['commodities'].append(c_dict)


        def shipyard(self, data):
            payload = {
              "$schemaRef": "https://eddn.edcd.io/schemas/shipyard/2",
              "header": {
                "uploaderID": "Anon",
                "softwareName": "BGS Companion",
                "softwareVersion": "0.9b"
              },
              "message": {
                "systemName": data['StationName'],
                "stationName": data['StationName'],
                "timestamp": data['timestamp'],
                "ships": []
              }
            }

            for ship in data['PriceList']:
                payload['message']['ships'].append(ship['ShipType'])

        def market(self, data):
            payload
