#!/usr/bin/env python3
"""
Polyglot v2 node server for Ambient Weather data.
Copyright (c) 2018 Robert Paauwe
"""
import polyinterface
import sys
import time
#import httplib
import urllib3
import json

LOGGER = polyinterface.LOGGER

class Controller(polyinterface.Controller):
    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)

        self.name = 'Ambient Weather'
        self.address = 'ambient'
        self.primary = self.address

    def start(self):
        LOGGER.info('Started Ambient Weather Node Server')
        self.check_params()
        self.discover()

    def shortPoll(self):
        pass

    def longPoll(self):
        """
        TODO: Here is where we want to query the server and update all
        the drivers.
        https://api.ambientweather.net/v1/devices/macAddress?apiKey=&applicationKey
        States that data is updated every 5 or 30 minutes (so which is it?)
        """
        LOGGER.info('Connecting to Ambient Weather server')
        LOGGER.info(self.api_key)
        LOGGER.info(self.mac_address)

        http = urllib3.PoolManager()
        #c = httplib.HTTPSConnection("api.ambientweather.net")

        # TODO: Make the path as part of the config procesing so that
        # we only do it once.
        # how to limit this to one entry?
        path_str = 'http://api.ambientweather.net/'
        path_str += 'v1/devices/' + self.mac_address + '?apiKey='
        path_str += self.api_key 

        path_str += '&applicationKey=5644719c27144e3a9b0341238344c7a4bf11a7c5023f4b4cbc1538b834b80037'
        path_str += '&limit=1'
        LOGGER.info(path_str)

        c = http.request('GET', path_str)
        #c.request("GET", path_str)

        #response = c.getresponse()
        #response = c.data
        #print response.status, response.reason
        print (c.status, c.reason)
        #data = response.read()
        #c.close()
        awdata = json.loads(c.data.decode('utf-8'))

        # deserialize data into an object?
        LOGGER.info(awdata[0])
        d = awdata[0]

        # TODO: calculate additional data values
        # pressure trend
        # heat index
        # windchill
        # rain rate

        for node in self.nodes:
            if self.nodes[node].id == 'pressure':
                self.set_driver(node, 'ST', d, 'baromabsin')
                self.set_driver(node, 'GV0', d, 'baromrelin')
                #self.set_driver(node, 'GV1', d, 'trend')
            elif self.nodes[node].id == 'temperature':
                self.set_driver(node, 'ST', d, 'tempf')
                self.set_driver(node, 'GV0', d, 'feelsLike')
                self.set_driver(node, 'GV1', d, 'dewPoint')
                #self.set_driver(node, 'GV2', d, 'heatIndex')
                #self.set_driver(node, 'GV3', d, 'windchill')
            elif self.nodes[node].id == 'humidity':
                self.set_driver(node, 'ST', d, 'humidity')
            elif self.nodes[node].id == 'wind':
                self.set_driver(node, 'ST', d, 'windspeedmph')
                self.set_driver(node, 'GV0', d, 'winddir')
                self.set_driver(node, 'GV1', d, 'windgustmph')
                #self.set_driver(node, 'GV2', d, 'windgustdir')
            elif self.nodes[node].id == 'precipitation':
                #self.set_driver(node, 'ST', d, 'rainrate')
                self.set_driver(node, 'GV0', d, 'hourlyrainin')
                self.set_driver(node, 'GV1', d, 'dailyrainin')
                self.set_driver(node, 'GV2', d, 'weeklyrainin')
                self.set_driver(node, 'GV3', d, 'monthlyrainin')
                self.set_driver(node, 'GV4', d, 'yearlyrainin')
            elif self.nodes[node].id == 'light':
                self.set_driver(node, 'ST', d, 'uv')
                #self.set_driver(node, 'GV0', d, 'solarradiation')

        c.close


    def set_driver(self, node, driver, data, index):
        try:
            self.nodes[node].setDriver(driver, data[index],
                    report = True, force = True)
        except (ValueError, KeyError, TypeError):
            LOGGER.error('Missing data: ' + index)

    def query(self):
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    def discover(self, *args, **kwargs):
        self.addNode(TemperatureNode(self, self.address, 'temperature', 'Temperatures'))
        self.addNode(HumidityNode(self, self.address, 'humidity', 'Humidity'))
        self.addNode(PressureNode(self, self.address, 'pressure', 'Barometric Pressure'))
        self.addNode(WindNode(self, self.address, 'wind', 'Wind'))
        self.addNode(PrecipitationNode(self, self.address, 'rain', 'Precipitation'))
        self.addNode(LightNode(self, self.address, 'light', 'Illumination'))

    def delete(self):
        LOGGER.info('Oh God I\'m being deleted. Nooooooooooooooooooooooooooooooooooooooooo.')

    def stop(self):
        LOGGER.debug('NodeServer stopped.')

    def check_params(self):
        if 'macAddress' in self.polyConfig['customParams']:
            self.mac_address = self.polyConfig['customParams']['macAddress']
        else:
            self.mac_address = ""
            LOGGER.error('check_params: mac address not defined in customParams, please add it.  Using {}'.format(self.mac_address))
            st = False

        if 'APIKey' in self.polyConfig['customParams']:
            self.api_key = self.polyConfig['customParams']['APIKey']
        else:
            self.api_key = ""
            LOGGER.error('check_params: API Key not defined in customParams, please add it.  Using {}'.format(self.api_key))
            st = False

        # Make sure they are in the params
        self.addCustomParam({'APIKey': self.api_key, 'macAddress': self.mac_address})

        # Remove all existing notices
        self.removeNoticesAll()
        # Add a notice if they need to change the user/password from the default.
        if self.mac_address == "" or self.api_key == "":
            self.addNotice("Please set proper mac address and API key in configuration page, and restart this nodeserver")

    def remove_notices_all(self,command):
        LOGGER.info('remove_notices_all:')
        # Remove all existing notices
        self.removeNoticesAll()

    def update_profile(self,command):
        LOGGER.info('update_profile:')
        st = self.poly.installprofile()
        return st

    id = 'Ambient'
    commands = {
        'DISCOVER': discover,
        'UPDATE_PROFILE': update_profile,
        'REMOVE_NOTICES_ALL': remove_notices_all
    }
    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 2},
            {'driver': 'BATLVL', 'value': 0, 'uom': 72}  # battery level
            ]


class TemperatureNode(polyinterface.Node):
    id = 'temperature'
    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 17},
            {'driver': 'GV0', 'value': 0, 'uom': 17}, # feels like
            {'driver': 'GV1', 'value': 0, 'uom': 17}, # dewpoint
            {'driver': 'GV2', 'value': 0, 'uom': 17}, # heat index
            {'driver': 'GV3', 'value': 0, 'uom': 17}  # windchill
            ]

class HumidityNode(polyinterface.Node):
    id = 'humidity'
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 22}]

class PressureNode(polyinterface.Node):
    id = 'pressure'
    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 23},  # abs press
            {'driver': 'GV0', 'value': 0, 'uom': 23}, # rel press
            {'driver': 'GV1', 'value': 0, 'uom': 25}  # trend
            ]

class WindNode(polyinterface.Node):
    id = 'wind'
    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 48},  # speed
            {'driver': 'GV0', 'value': 0, 'uom': 76}, # direction
            {'driver': 'GV1', 'value': 0, 'uom': 48}, # gust
            {'driver': 'GV2', 'value': 0, 'uom': 76}  # gust direction
            ]

class PrecipitationNode(polyinterface.Node):
    id = 'precipitation'
    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 24},  # rate
            {'driver': 'GV0', 'value': 0, 'uom': 105}, # hourly
            {'driver': 'GV1', 'value': 0, 'uom': 105}, # daily
            {'driver': 'GV2', 'value': 0, 'uom': 105}, # weekly
            {'driver': 'GV2', 'value': 0, 'uom': 105}, # monthly
            {'driver': 'GV2', 'value': 0, 'uom': 105}  # yearly
            ]

class LightNode(polyinterface.Node):
    id = 'light'
    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 71},  # UV
            {'driver': 'GV0', 'value': 0, 'uom': 74},  # solar radiation
            {'driver': 'GV1', 'value': 0, 'uom': 36},  # Lux
            ]

if __name__ == "__main__":
    try:
        polyglot = polyinterface.Interface('AmbientWeather')
        """
        Instantiates the Interface to Polyglot.
        """
        polyglot.start()
        """
        Starts MQTT and connects to Polyglot.
        """
        control = Controller(polyglot)
        """
        Creates the Controller Node and passes in the Interface
        """
        control.runForever()
        """
        Sits around and does nothing forever, keeping your program running.
        """
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        """
        Catch SIGTERM or Control-C and exit cleanly.
        """
