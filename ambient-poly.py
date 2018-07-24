#!/usr/bin/env python3
"""
Polyglot v2 node server for Ambient Weather data.
Copyright (c) 2018 Robert Paauwe
"""
import polyinterface
import sys
import time
import httplib
import json

LOGGER = polyinterface.LOGGER
"""
polyinterface has a LOGGER that is created by default and logs to:
logs/debug.log
You can use LOGGER.info, LOGGER.warning, LOGGER.debug, LOGGER.error levels as needed.
"""

class Controller(polyinterface.Controller):
	"""
	The Controller Class is the primary node from an ISY perspective.
	It is a Superclass of polyinterface.Node so all methods from
	polyinterface.Node are available to this class as well.

	Class Variables:
	self.nodes:   Dictionary of nodes. Includes the Controller node.
				  Keys are the node addresses
	self.name:	String name of the node
	self.address: String Address of Node, must be less than 14 characters
				  (ISY limitation)
	self.polyConfig: Full JSON config dictionary received from Polyglot for
					 the controller Node
	self.added:   Boolean Confirmed added to ISY as primary node
	self.config:  Dictionary, this node's Config

	Class Methods (not including the Node methods):
	start():
		Once the NodeServer config is received from Polyglot this method
		is automatically called.
	addNode(polyinterface.Node, update = False):
		Adds Node to self.nodes and polyglot/ISY. This is called
		for you on the controller itself. Update = True overwrites the
		existing Node data.
	updateNode(polyinterface.Node):
		Overwrites the existing node data here and on Polyglot.
	delNode(address):
		Deletes a Node from the self.nodes/polyglot and ISY. Address is the
		Node's Address
	longPoll():
		Runs every longPoll seconds (set initially in the server.json or
		default 10 seconds)
	shortPoll():
		Runs every shortPoll seconds (set initially in the server.json or
		default 30 seconds)
	query():
		Queries and reports ALL drivers for ALL nodes to the ISY.
	getDriver('ST'):
		gets the current value from Polyglot for driver 'ST' returns a
		STRING, cast as needed
	runForever():
		Easy way to run forever without maxing your CPU or doing some silly
		'time.sleep' nonsense. this joins the underlying queue query thread
		and just waits for it to terminate which never happens.
	"""
	def __init__(self, polyglot):
		"""
		Optional.
		Super runs all the parent class necessities. You do NOT have
		to override the __init__ method, but if you do, you MUST call super.
		"""
		super(Controller, self).__init__(polyglot)

	def start(self):
		"""
		Optional.
		Polyglot v2 Interface startup done. Here is where you start your
		integration.  This will run, once the NodeServer connects to
		Polyglot and gets it's config.
		In this example I am calling a discovery method. While this is optional,
		this is where you should start. No need to Super this method, the parent
		version does nothing.
		"""
		LOGGER.info('Started Ambient Weather Node Server')
		self.check_params()
		self.discover()

	def shortPoll(self):
		"""
		Optional.
		This runs every 10 seconds. You would probably update your nodes
		either here or longPoll. No need to Super this method the parent
		version does nothing.
		The timer can be overriden in the server.json.
		"""
		pass

	def longPoll(self):
		"""
		Optional.
		This runs every 30 seconds. You would probably update your nodes
		either here or shortPoll. No need to Super this method the parent
		version does nothing.
		The timer can be overriden in the server.json.

		TODO: Here is where we want to query the server and update all
		the drivers.
		https://api.ambientweather.net/v1/devices/macAddress?apiKey=&applicationKey
		States that data is updated every 5 or 30 minutes (so which is it?)
		"""
		LOGGER.info('Connecting to Ambient Weather server')
		LOGGER.info(self.api_key)
		LOGGER.info(self.mac_address)
		c = httplib.HTTPSConnection("api.ambientweather.net")

		# TODO: Make the path as part of the config procesing so that
		# we only do it wonce.
		# how to limit this to one entry?
		path_str = "/v1/devices/" + self.mac_address + "?apiKey="
		path_str += self.api_key 

		path_str += "&applicationKey=5644719c27144e3a9b0341238344c7a4bf11a7c5023f4b4cbc1538b834b80037"
		path_str += "&limit=1"
		LOGGER.info(path_str)

		c.request("GET", path_str)

		response = c.getresponse()
		print response.status, response.reason
		data = response.read()
		c.close()

		# deserialize data into an object?
		try:
			#LOGGER.info(data)
			awdata = json.loads(data)
			LOGGER.info(awdata[0])
			d = awdata[0]
			LOGGER.info(d['tempf'])
			LOGGER.info(d['baromrelin'])
			LOGGER.info(d['baromabsin'])
			LOGGER.info(d['winddir'])

			for node in self.nodes:
				if self.nodes[node].id == 'pressure':
					self.nodes[node].setDriver('ST', d['baromabsin'],
							report = True, force = True)
					self.nodes[node].setDriver('GV0', d['baromrelin'],
							report = True, force = True)
				else if self.nodes[node].id == 'temperature':
					self.nodes[node].setDriver('ST', d['tempf'],
							report = True, force = True)
					self.nodes[node].setDriver('GV0', d['dewpoint'],
							report = True, force = True)
				else if self.nodes[node].id == 'humidity':
				else if self.nodes[node].id == 'wind':
				else if self.nodes[node].id == 'precipitation':
				else if self.nodes[node].id == 'light':

		except (ValueError, KeyError, TypeError):
			LOGGER.error('Failed to decode data from ambientweather.net')


	def query(self):
		"""
		Optional.
		By default a query to the control node reports the FULL driver set
		for ALL nodes back to ISY. If you override this method you will need
		to Super or issue a reportDrivers() to each node manually.
		"""
		for node in self.nodes:
			self.nodes[node].reportDrivers()

	def discover(self, *args, **kwargs):
		"""
		Example
		Do discovery here. Does not have to be called discovery. Called
		from example controller start method and from DISCOVER command
		recieved from ISY as an exmaple.

		TODO: Is this suppose to add all the actual devices nodes? It kind
			  of looks like that.  Rough outline:

			  Query AmbientWeather.net with mac address and api key to get
			  station information (name?)
			  Add basic weather sensor nodes
				  - Temperature (temp, dewpoint, heat index, wind chill, feels)
				  - Humidity
				  - Pressure (abs, sealevel, trend)
				  - Wind (speed, gust, direction, gust direction, etc.)
				  - Precipitation (rate, hourly, daily, weekly, monthly, yearly)
				  - Light (UV, solar radiation, lux)
		"""
		self.addNode(TemperatureNode(self, self.address, 'temperature', 'Temperatures'))
		self.addNode(HumidityNode(self, self.address, 'humidity', 'Humidity'))
		self.addNode(PressureNode(self, self.address, 'pressure', 'Barometric Pressure'))
		self.addNode(WindNode(self, self.address, 'wind', 'Wind'))
		self.addNode(PrecipitationNode(self, self.address, 'rain', 'Precipitation'))
		self.addNode(LightNode(self, self.address, 'light', 'Illumination'))

	def delete(self):
		"""
		Example
		This is sent by Polyglot upon deletion of the NodeServer. If the
		process is co-resident and controlled by Polyglot, it will be
		terminiated within 5 seconds of receiving this message.
		"""
		LOGGER.info('Oh God I\'m being deleted. Nooooooooooooooooooooooooooooooooooooooooo.')

	def stop(self):
		LOGGER.debug('NodeServer stopped.')

	def check_params(self):
		"""
		This is an example if using custom Params for user and password and an
		example with a Dictionary

		TODO: Station mac address and API key
		"""
		default_user = "YourUserName"
		default_password = "YourPassword"
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

	"""
	Optional.
	Since the controller is the parent node in ISY, it will actual show up
	as a node.  So it needs to know the drivers and what id it will use.
	The drivers are the defaults in the parent Class, so you don't need
	them unless you want to add to them. The ST and GV1 variables are for
	reporting status through Polyglot to ISY, DO NOT remove them. UOM 2
	is boolean.
	"""
	id = 'controller'
	commands = {
		'DISCOVER': discover,
		'UPDATE_PROFILE': update_profile,
		'REMOVE_NOTICES_ALL': remove_notices_all
	}
	drivers = [{'driver': 'ST', 'value': 0, 'uom': 2}]


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

class MyNode(polyinterface.Node):
	"""
	This is the class that all the Nodes will be represented by. You will add
	this to Polyglot/ISY with the controller.addNode method.
	
	CHECKME: Does this cover all sensors or is it a parent class to each
	specific sensor class?

	Class Variables:
	self.primary: String address of the Controller node.
	self.parent: Easy access to the Controller Class from the node itself.
	self.address: String address of this Node 14 character limit. (ISY limitation)
	self.added: Boolean Confirmed added to ISY

	Class Methods:
	start(): This method is called once polyglot confirms the node is added to ISY.
	setDriver('ST', 1, report = True, force = False):
		This sets the driver 'ST' to 1. If report is False we do not report it to
		Polyglot/ISY. If force is True, we send a report even if the value hasn't changed.
	reportDrivers(): Forces a full update of all drivers to Polyglot/ISY.
	query(): Called when ISY sends a query request to Polyglot for this specific node
	"""
	def __init__(self, controller, primary, address, name):
		"""
		Optional.
		Super runs all the parent class necessities. You do NOT have
		to override the __init__ method, but if you do, you MUST call super.

		:param controller: Reference to the Controller class
		:param primary: Controller address
		:param address: This nodes address
		:param name: This nodes name
		"""
		super(MyNode, self).__init__(controller, primary, address, name)

	def start(self):
		"""
		Optional.
		This method is run once the Node is successfully added to the ISY
		and we get a return result from Polyglot. Only happens once.

		TODO: Do we need to do anything here? Maybe get the initial data
			  and populate the drivers?
		"""
		self.setDriver('ST', 1)
		pass

	def setOn(self, command):
		"""
		Example command received from ISY.
		Set DON on MyNode.
		Sets the ST (status) driver to 1 or 'True'

		TODO: Is this method needed or can it be deleted?
		"""
		self.setDriver('ST', 1)

	def setOff(self, command):
		"""
		Example command received from ISY.
		Set DOF on MyNode
		Sets the ST (status) driver to 0 or 'False'

		TODO: Is this method needed or can it be deleted?
		"""
		self.setDriver('ST', 0)

	def query(self):
		"""
		Called by ISY to report all drivers for this node. This is done in
		the parent class, so you don't need to override this method unless
		there is a need.
		"""
		self.reportDrivers()


	"""
	This looks like an array of drivers so that implies that it will be
	different for different node types.  Which implies that we need
	multiple node classes.
	"""
	
	drivers = [{'driver': 'ST', 'value': 0, 'uom': 2}]
	"""
	Optional.
	This is an array of dictionary items containing the variable names(drivers)
	values and uoms(units of measure) from ISY. This is how ISY knows what kind
	of variable to display. Check the UOM's in the WSDK for a complete list.
	UOM 2 is boolean so the ISY will display 'True/False'
	"""
	id = 'mynodetype'
	"""
	id of the node from the nodedefs.xml that is in the profile.zip. This tells
	the ISY what fields and commands this node has.
	"""
	commands = {
					'DON': setOn, 'DOF': setOff
				}
	"""
	This is a dictionary of commands. If ISY sends a command to the NodeServer,
	this tells it which method to call. DON calls setOn, etc.
	"""

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
