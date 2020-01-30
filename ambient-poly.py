#!/usr/bin/env python3
"""
Polyglot v2 node server for Ambient Weather data.
Copyright (c) 2018 Robert Paauwe
"""
CLOUD = False
try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface
    CLOUD = True
import sys
import time
import requests
import json

LOGGER = polyinterface.LOGGER

class Controller(polyinterface.Controller):
    id = 'Ambient'

    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)

        self.name = 'AmbientWeather'
        self.address = 'ambient'
        self.primary = self.address
        self.api_key = ''
        self.mac_address = ''
        self.indoor = 'disabled'
        self.myParams = {
                'APIKey': '<your value here>',
                'macAddress': '<your value here>',
                'indoor': 'disabled',
                }
        self.url_str = 'http://api.ambientweather.net/v1/devices/'
        self.default = '<your value here>'
        self.configured = False
        self.started = False
        self.first_poll = True

        self.poly.onConfig(self.process_config)
        LOGGER.info('Finished controller init.')

    '''
    This is called whenever there is a configuration change. Somehow
    we need to detect if it is a change in custom parameters and then
    process those changes.
    '''
    def process_config(self, config):
        if self.started == False:
            LOGGER.debug('Ignore config, NS not yet started')
            return

        changed = False

        if 'customParams' in config:
            LOGGER.debug('pc: Incoming config = {}'.format(config['customParams']))
            if 'APIKey' in config['customParams']:
                if self.myParams['APIKey'] != config['customParams']['APIKey']:
                    self.myParams['APIKey'] = config['customParams']['APIKey']
                    self.api_key = config['customParams']['APIKey']
                    changed = True

            if 'macAddress' in config['customParams']:
                if self.myParams['macAddress'] != config['customParams']['macAddress']:
                    self.myParams['macAddress'] = config['customParams']['macAddress']
                    self.mac_address = config['customParams']['macAddress']
                    changed = True
            if 'indoor' in config['customParams']:
                if self.myParams['indoor'] != config['customParams']['indoor']:
                    self.myParams['indoor'] = config['customParams']['indoor']
                    self.indoor = config['customParams']['indoor']
                    changed = True

                
            if changed:
                LOGGER.debug('Configuration change detected.')
                # Update notices.  Make sure we restrict setting notices
                # to only when something was updated. Otherwise we can
                # end up with an infinite loop as setting a notice will
                # trigger a configuration change.
                self.removeNoticesAll()
                notices = {}
                self.configured = True
                if self.mac_address == self.default:
                    notices['mac'] = 'Please set your station macAddress (1)'
                    LOGGER.debug('mac address net set, set configured to false')
                    self.configured = False
                if self.api_key == self.default:
                    notices['key'] = 'Please set APIKey to your Ambient API Key (1)'
                    LOGGER.debug('api key net set, set configured to false')
                    self.configured = False

                self.addNotice(notices)


    def start(self):
        LOGGER.info('Started Ambient Weather Node Server')
        if self.check_params():
            LOGGER.info('AmbientWeatherNS has been configured.')
            self.configured = True
        else:
            LOGGER.info('APIKey and macAddress not set.')
            self.configured = False

        self.discover()
        LOGGER.info('Ambient Weather Node Server initialization complete.')
        self.started = True

    def shortPoll(self):
        pass

    def longPoll(self):
        """
        Here is where we want to query the server and update all
        the drivers.
        https://api.ambientweather.net/v1/devices/macAddress?apiKey=&applicationKey
        States that data is updated every 5 or 30 minutes (so which is it?)
        """

        if self.configured == False:
            if self.first_poll:
                LOGGER.info('Waiting to be configured.')
                LOGGER.info('   key = ' + self.api_key)
                LOGGER.info('   mac = ' + self.mac_address)
                self.first_poll = False
            return

        LOGGER.info('Connecting to Ambient Weather server')

        path_str = self.url_str + self.mac_address
        path_str += '?apiKey=' + self.api_key 
        path_str += '&applicationKey=5644719c27144e3a9b0341238344c7a4bf11a7c5023f4b4cbc1538b834b80037'
        path_str += '&limit=1'
        LOGGER.info(path_str)

        try:
            c = requests.get(path_str)
        except:
            LOGGER.error('Request to Ambient servers failed.')
            return

        awdata = c.json()

        # deserialize data into an object?
        try:
            LOGGER.info(awdata[0])
            d = awdata[0]
        except:
            LOGGER.error('Failed to get data from server: ' + str(awdata))
            return

        # TODO: calculate additional data values
        # pressure trend
        # heat index
        # windchill
        # rain rate

        for node in self.nodes:
            if self.nodes[node].id == 'pressure':
                self.set_driver(node, 'GV0', d, 'baromrelin')
                if 'baromabsin' in d:
                    self.set_driver(node, 'ST', d, 'baromabsin')

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
                self.set_driver(node, 'GV0', d, 'solarradiation')
            elif self.nodes[node].id == 'indoor':
                self.set_driver(node, 'ST', d, 'tempinf')
                self.set_driver(node, 'GV0', d, 'humidityin')

        self.first_poll = False


    def set_driver(self, node, driver, data, index):
        try:
            self.nodes[node].setDriver(driver, data[index],
                    report = True, force = self.first_poll)
        except (ValueError, KeyError, TypeError):
            LOGGER.warning('Missing data: ' + index)

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
        if self.indoor.lower() == 'enabled':
            self.addNode(IndoorNode(self, self.address, 'indoor', 'Indoor Sensor'))

    def delete(self):
        LOGGER.info('Deleting the Ambient Weather node server.')

    def stop(self):
        LOGGER.debug('NodeServer stopped.')

    def check_param(self, name, myParams, default, notices, notice):
        param = default
        st = True
        if name in self.polyConfig['customParams']:
            if self.polyConfig['customParams'][name] != default:
                param = self.polyConfig['customParams']['macAddress']
                myParams[name] = param
            else:
                if notice != '':
                    notices[name] = notice
                st = False
        else:
            LOGGER.error('check_params: %s not defined in customParams' % name)
            if notice != '':
                notices[name] = notice
            st = False

        return st, param

    def check_params(self):
        st = True
        self.removeNoticesAll()
        notices = {}
        default = '<your value here>'
        
        st1, self.mac_address = self.check_param('macAddress', self.myParams, default, notices, 'Missing station MAC address')
        st2, self.api_key = self.check_param('APIKey', self.myParams, default, notices, 'Missing Ambient API key')
        st3, self.indoor = self.check_param('indoor', self.myParams, 'disabled', notices, '')
        
        if 'macAddress' in self.polyConfig['customParams']:
            if self.polyConfig['customParams']['macAddress'] != default:
                self.mac_address = self.polyConfig['customParams']['macAddress']
                self.myParams['macAddress'] = self.mac_address
            else:
                notices['macaddress'] = 'Please set your station macAddress'
                st = False
        else:
            st = False
            self.mac_address = default
            LOGGER.error('check_params: macAddress not defined in customParams, please add it.')
            notices['macaddress'] = 'Please add a customParam with key "macAddress" and value set to your Ambient station MAC address'

        if 'APIKey' in self.polyConfig['customParams']:
            if self.polyConfig['customParams']['APIKey'] != default:
                self.api_key = self.polyConfig['customParams']['APIKey']
                self.myParams['APIKey'] = self.api_key
            else:
                notices['apikey'] = 'Please set APIKey to your Ambient API Key'
                st = False
        else:
            st = False
            self.api_key = default
            LOGGER.error('check_params: APIKey not defined in customParams, please add it.')
            notices['apikey'] = 'Please add a customParam with key "APIKey" and value set to your Ambient API Key'

        if 'indoor' in self.polyConfig['customParams']:
            if self.polyConfig['customParams']['indoor'] != 'disabled':
                self.indoor = self.polyConfig['customParams']['indoor']
                self.myParams['indoor'] = self.indoor
        else:
            self.indoor = 'disabled'

        # Must be called with all parameters and all notices!
        self.addCustomParam(self.myParams)
        self.addNotice(notices)
        return (st1 and st2)

    def remove_notices_all(self,command):
        LOGGER.info('remove_notices_all:')
        # Remove all existing notices
        self.removeNoticesAll()

    def update_profile(self,command):
        LOGGER.info('update_profile:')
        st = self.poly.installprofile()
        return st

    commands = {
        'DISCOVER': discover,
        'UPDATE_PROFILE': update_profile,
        'REMOVE_NOTICES_ALL': remove_notices_all
    }
    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},
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

class IndoorNode(polyinterface.Node):
    id = 'indoor'
    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 17},  # indoor temp
            {'driver': 'GV0', 'value': 0, 'uom': 22},  # indoor humidity
            ]

if __name__ == "__main__":
    try:
        polyglot = polyinterface.Interface('AmbientWeather')
        polyglot.start()
        control = Controller(polyglot)
        control.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
