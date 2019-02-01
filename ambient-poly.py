#!/usr/bin/env python3
"""
Polyglot v2 node server for Ambient Weather data.
Copyright (c) 2018 Robert Paauwe
"""
import polyinterface
import sys
import time
import requests
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
        # #LOGGER.info(self.api_key)
        # #LOGGER.info(self.mac_address)

        # TODO: Make the path as part of the config procesing so that
        # we only do it once.
        # how to limit this to one entry?
        # TODO: May want to make the app key user provided?
        awAPI = 'https://api.ambientweather.net/'
        awAPI += 'v1/devices/' + self.mac_address + '?apiKey=' + self.api_key
        awAPI += '&applicationKey=5644719c27144e3a9b0341238344c7a4bf11a7c5023f4b4cbc1538b834b80037'
        awAPI += '&limit=1'
        #LOGGER.info(awAPI)

        r = requests.get(awAPI)
        #LOGGER.info(r.json())
        awdata = r.json()
        d = awdata[0]

        '''
        Added check for add-on sensors.
        If they exist in Ambient Weather then
        add nodes for them to be updated on next poll
        '''
        for k,v in d.items():
            if k == 'temp1f':
                if 'sensor01' not in self.nodes:
                    self.addNode(Sensor01Node(self, self.address, 'sensor01', 'Sensor 01'))
            elif k == 'temp2f':
                if 'sensor02' not in self.nodes:
                    self.addNode(Sensor02Node(self, self.address, 'sensor02', 'Sensor 02'))
            elif k == 'temp3f':
                if 'sensor03' not in self.nodes:
                    self.addNode(Sensor03Node(self, self.address, 'sensor03', 'Sensor 03'))
            elif k == 'temp4f':
                if 'sensor04' not in self.nodes:
                    self.addNode(Sensor04Node(self, self.address, 'sensor04', 'Sensor 04'))
            elif k == 'temp5f':
                if 'sensor05' not in self.nodes:
                    self.addNode(Sensor05Node(self, self.address, 'sensor05', 'Sensor 05'))
            elif k == 'temp6f':
                if 'sensor06' not in self.nodes:
                    self.addNode(Sensor06Node(self, self.address, 'sensor06', 'Sensor 06'))
            elif k == 'temp7f':
                if 'sensor07' not in self.nodes:
                    self.addNode(Sensor07Node(self, self.address, 'sensor07', 'Sensor 07'))
            elif k == 'temp8f':
                if 'sensor08' not in self.nodes:
                    self.addNode(Sensor08Node(self, self.address, 'sensor08', 'Sensor 08'))

        '''
        TODO: calculate additional data values
        pressure trend
        heat index
        windchill
        rain rate
        '''
        for node in self.nodes:
            if self.nodes[node].id == 'pressure':
                self.set_driver(node, 'ST', d, 'baromabsin')
                self.set_driver(node, 'GV0', d, 'baromrelin')
                trend = self.nodes[node].updateTrend(d['baromabsin'])
                self.nodes[node].setDriver('GV1', trend, report = True, force = True)
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

            # Adding updates for add-on sensors            
            elif self.nodes[node].id == 'sensor01':
                self.set_driver(node, 'ST', d, 'temp1f')
                self.set_driver(node, 'GV0', d, 'humidity1')
            elif self.nodes[node].id == 'sensor02':
                self.set_driver(node, 'ST', d, 'temp2f')
                self.set_driver(node, 'GV0', d, 'humidity2')
            elif self.nodes[node].id == 'sensor03':
                self.set_driver(node, 'ST', d, 'temp3f')
                self.set_driver(node, 'GV0', d, 'humidity3')
            elif self.nodes[node].id == 'sensor04':
                self.set_driver(node, 'ST', d, 'temp4f')
                self.set_driver(node, 'GV0', d, 'humidity4')
            elif self.nodes[node].id == 'sensor05':
                self.set_driver(node, 'ST', d, 'temp5f')
                self.set_driver(node, 'GV0', d, 'humidity5')
            elif self.nodes[node].id == 'sensor06':
                self.set_driver(node, 'ST', d, 'temp6f')
                self.set_driver(node, 'GV0', d, 'humidity6')
            elif self.nodes[node].id == 'sensor07':
                self.set_driver(node, 'ST', d, 'temp7f')
                self.set_driver(node, 'GV0', d, 'humidity7')
            elif self.nodes[node].id == 'sensor08':
                self.set_driver(node, 'ST', d, 'temp8f')
                self.set_driver(node, 'GV0', d, 'humidity8')
            
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
        '''
        TODO: Maybe Make these discovered and not created by default
        to support non PWS Ambient Weather consoles?
        '''
        self.addNode(TemperatureNode(self, self.address, 'temperature', 'Temperatures'))
        self.addNode(HumidityNode(self, self.address, 'humidity', 'Humidity'))
        self.addNode(PressureNode(self, self.address, 'pressure', 'Barometric Pressure'))
        self.addNode(WindNode(self, self.address, 'wind', 'Wind'))
        self.addNode(PrecipitationNode(self, self.address, 'rain', 'Precipitation'))
        self.addNode(LightNode(self, self.address, 'light', 'Illumination'))    

    def delete(self):
        LOGGER.info('Deleting the Ambient Weather node server.')

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
    mytrend = []

    def updateTrend(self, current):
        t = 0
        past = 0

        if (len(self.mytrend) == 180):
            past = self.mytrend.pop()
        if self.mytrend != []:
            past = self.mytrend[0]

        # calculate trend
        if (past - current) > 0.01:
            t = -1
        elif (past - current) < 0.01:
            t = 1

        self.mytrend.insert(0, current)
        return t

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

class Sensor01Node(polyinterface.Node):
    id = 'sensor01'
    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 17},
        {'driver': 'GV0', 'value': 0, 'uom': 22}]

class Sensor02Node(polyinterface.Node):
    id = 'sensor02'
    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 17},
        {'driver': 'GV0', 'value': 0, 'uom': 22}]

class Sensor03Node(polyinterface.Node):
    id = 'sensor03'
    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 17},
        {'driver': 'GV0', 'value': 0, 'uom': 22}]

class Sensor04Node(polyinterface.Node):
    id = 'sensor04'
    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 17},
        {'driver': 'GV0', 'value': 0, 'uom': 22}]

class Sensor05Node(polyinterface.Node):
    id = 'sensor05'
    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 17},
        {'driver': 'GV0', 'value': 0, 'uom': 22}]

class Sensor06Node(polyinterface.Node):
    id = 'sensor06'
    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 17},
        {'driver': 'GV0', 'value': 0, 'uom': 22}]

class Sensor07Node(polyinterface.Node):
    id = 'sensor07'
    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 17},
        {'driver': 'GV0', 'value': 0, 'uom': 22}]

class Sensor08Node(polyinterface.Node):
    id = 'sensor08'
    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 17},
        {'driver': 'GV0', 'value': 0, 'uom': 22}]

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
