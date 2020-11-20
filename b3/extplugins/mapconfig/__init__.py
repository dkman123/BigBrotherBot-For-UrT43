# -*- coding: utf-8 -*-

# ################################################################### #
#                                                                     #
#  BigBrotherBot(B3) (www.bigbrotherbot.net)                          #
#  Copyright (C) 2005 Michael "ThorN" Thornton                        #
#                                                                     #
#  This program is free software; you can redistribute it and/or      #
#  modify it under the terms of the GNU General Public License        #
#  as published by the Free Software Foundation; either version 2     #
#  of the License, or (at your option) any later version.             #
#                                                                     #
#  This program is distributed in the hope that it will be useful,    #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of     #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the       #
#  GNU General Public License for more details.                       #
#                                                                     #
#  You should have received a copy of the GNU General Public License  #
#  along with this program; if not, write to the Free Software        #
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA      #
#  02110-1301, USA.                                                   #
#                                                                     #
# ################################################################### #

# 2019.05.29 try a getCmd for pagear
# 2020.11.20 add timelimit

__version__ = '0.1'
__author__ = 'isopropanol'

# import b3
# from b3.clients import Client
# import b3.events
import b3.plugin
import os
import platform

# from b3 import functions
# from b3.clients import Client
from b3.functions import getCmd
from ConfigParser import NoOptionError

class MapconfigPlugin(b3.plugin.Plugin):
	# requiresConfigFile = False

	_adminPlugin = None
	powerAdminUrtPlugin = None

	requiresParsers = ['iourt42', 'iourt43']
	# loadAfter is a higher level of requires. Doing both causes a "cyclic dependency" error
	# requiresPlugins = ['admin', 'poweradminurt']
	loadAfterPlugins = ['poweradminurt']

	# NOTE: if you add fields then add them here
	default_capturelimit = 8
	default_g_suddendeath = 0
	default_g_gear = 0
	default_g_gravity = 800
	default_g_friendlyfire = 2
	default_startmessage = ""
	default_timelimit = 20

	mapcycle_fileName = ""
	# last modified timestamp
	mapcycle_timestamp = 0
	# the mapcycle as a string
	mapcycle = ""

	# variables held to reduce processing overhead
	_up_mapname = ""
	_up_nextmap = ""
	_up_next3 = ""
	_startmessage = ""

	####################################################################################################################
	#                                                                                                                  #
	#    STARTUP                                                                                                       #
	#                                                                                                                  #
	####################################################################################################################

	def onStartup(self):
		"""
		startup the plugin
		"""
		# get the admin plugin so we can register commands
		self._adminPlugin = self.console.getPlugin('admin')
		self.powerAdminUrtPlugin = self.console.getPlugin('powerAdminUrtPlugin')

		# register our commands
		if 'commands' in self.config.sections():
			for cmd in self.config.options('commands'):
				level = self.config.get('commands', cmd)
				sp = cmd.split('-')
				alias = None
				if len(sp) == 2:
					cmd, alias = sp

				func = getCmd(self, cmd)
				if func:
					self._adminPlugin.registerCommand(self, cmd, level, func, alias)

		self.registerEvent('EVT_GAME_ROUND_START', self.onNewMap)
		self.registerEvent('EVT_GAME_EXIT')
		self.registerEvent('EVT_GAME_ROUND_END')

		# # tried to catch the end of the map to announce the next map, but it's not firing.
		# # it might only catch actual match rounds
		# self.registerEvent('EVT_GAME_ROUND_END', self.onMapEnd)

	def onLoadConfig(self):
		"""
		load plugin configuration
		"""
		# NOTE: if you add fields then add them here
		try:
			self.default_capturelimit = self.config.getint('settings', 'default_capturelimit')
		except (NoOptionError, ValueError):
			self.default_capturelimit = 8

		self.debug('default_capturelimit : %s' % self.default_capturelimit)

		try:
			self.default_g_suddendeath = self.config.getint('settings', 'default_g_suddendeath')
		except (NoOptionError, ValueError):
			self.default_g_suddendeath = 0

		self.debug('default_g_suddendeath : %s' % self.default_g_suddendeath)

		try:
			self.default_g_gear = self.config.getint('settings', 'default_g_gear')
		except (NoOptionError, ValueError):
			self.default_g_gear = "0"

		self.debug('default_g_gear : %s' % self.default_g_gear)

		try:
			self.default_g_gravity = self.config.getint('settings', 'default_g_gravity')
		except (NoOptionError, ValueError):
			self.default_g_gravity = 800

		self.debug('default_g_gravity : %s' % self.default_g_gravity)

		try:
			self.default_g_friendlyfire = self.config.getint('settings', 'default_g_friendlyfire')
		except (NoOptionError, ValueError):
			self.default_g_friendlyfire = 0

		self.debug('default_g_friendlyfire : %s' % self.default_g_friendlyfire)

		try:
			self.default_startmessage = self.config.get('settings', 'default_startmessage')
		except (NoOptionError, ValueError):
			self.default_startmessage = ""

		self.debug('default_startmessage : %s' % self.default_startmessage)

		try:
			self.mapcycle_fileName = self.config.get('settings', 'mapcycle_fileName')
		except (NoOptionError, ValueError):
			self.mapcycle_fileName = ""

		self.debug('mapcycle_fileName : %s' % self.mapcycle_fileName)

		try:
			self.default_timelimit = self.config.getint('settings', 'default_timelimit')
		except (NoOptionError, ValueError):
			self.default_timelimit = 0

		self.debug('default_timelimit : %s' % self.default_timelimit)

		self.mapcycle = ""

	####################################################################################################################
	#                                                                                                                  #
	#   EVENTS                                                                                                         #
	#                                                                                                                  #
	####################################################################################################################

	def onNewMap(self, event):
		"""
	    Handle EVT_GAME_ROUND_START
	    """
		# self.debug('onNewMap handle %s:"%s"', event.type, event.data)
		# event.data is a b3.game.Game object
		mapName = event.data._get_mapName()
		self.setMapSettings(mapName)

	def onEvent(self, event):
		if (event.type == self.console.getEventID('EVT_GAME_EXIT')) or \
				(event.type == self.console.getEventID('EVT_GAME_ROUND_END')):
			# self.debug('onEvent')
			if self.mapcycle_fileName:
				self.cmd_upcoming(self)
			else:
				nextmap = self.console.getNextMap()
				if nextmap:
					ad = "^2Next map: ^3" + nextmap
					self.console.say(ad)

	####################################################################################################################
	#                                                                                                                  #
	#    OTHER METHODS                                                                                                 #
	#                                                                                                                  #
	####################################################################################################################

	def getMapconfig(self, mapconfig):
		"""
		Return an mapconfig object fetching data from the storage.
		:param mapconfig: The mapconfig object to fill with fetch data.
		:return: The mapconfig object given in input with all the fields set.
		"""
		# self.console.debug('Storage: getMapconfig %s' % mapconfig)
		if hasattr(mapconfig, 'mapname') and mapconfig["mapname"]:
			# query = QueryBuilder(self.db).SelectQuery('*', 'mapconfig', {'mapname': mapconfig.mapname}, None, 1)
			self.debug("has attribute mapname")
			# pass
		# else:
		# 	raise KeyError('no mapname was set %s' % mapconfig)

		# cursor = self.query(query)
		cursor = self.console.storage.query("SELECT * FROM mapconfig WHERE mapname = '%s'" % (mapconfig["mapname"]))
		if cursor.EOF:
			cursor.close()
			self.debug('no mapconfig found matching %s' % (mapconfig["mapname"]))
			mapconfig["id"] = 0
			return mapconfig
			# raise KeyError('no mapconfig found matching %s' % mapconfig.mapname)

		row = cursor.getOneRow()
		mapconfig["id"] = int(row['id'])
		mapconfig["mapname"] = row['mapname']
		# NOTE: if you add fields then add them here
		mapconfig["capturelimit"] = int(row['capturelimit'])
		mapconfig["g_suddendeath"] = int(row['g_suddendeath'])
		mapconfig["g_gear"] = row['g_gear']
		mapconfig["g_gravity"] = int(row['g_gravity'])
		mapconfig["g_friendlyfire"] = int(row['g_friendlyfire'])
		mapconfig["startmessage"] = row['startmessage']
		mapconfig["timelimit"] = row['timelimit']
	
		return mapconfig

	def setMapSettings(self, mapName):
		"""
		Sends the rcon commands to set the settings
		:param mapName: the map name (without extension)
		:return:
		"""
		self.debug('onNewMap map %s' % mapName)
		# need to read b3 table to get values

		# NOTE: if you add fields then add them here
		mapconfig = {"id": 0, \
					 "mapname": mapName, \
					 "capturelimit": self.default_capturelimit, \
					 "g_suddendeath": self.default_g_suddendeath, \
					 "g_gear": self.default_g_gear, \
					 "g_gravity": self.default_g_gravity, \
					 "g_friendlyfire": self.default_g_friendlyfire, \
					 "startmessage": self.default_startmessage, \
					 "timelimit": self.default_timelimit }

		mapconfig = self.getMapconfig(mapconfig)
		# if mapconfig["id"] > 0:
		# then rcon to set game values
		# self.debug('setting capturelimit %s, g_gear %s' % (mapconfig["capturelimit"], mapconfig["g_gear"]))

		# NOTE: if you add fields then add them here
		self.console.write('capturelimit %s ' % (mapconfig["capturelimit"]))
		self.console.write('g_suddendeath %s ' % (mapconfig["g_suddendeath"]))
		self.console.write('g_gear "%s" ' % (mapconfig["g_gear"]))
		self.console.write('g_gravity %s ' % (mapconfig["g_gravity"]))
		self.console.write('g_friendlyfire %s ' % (mapconfig["g_friendlyfire"]))
		if mapconfig["startmessage"] and mapconfig["startmessage"] != "":
			self.console.say('Map Start Message: ^8%s' % (mapconfig["startmessage"]))
			self._startmessage = mapconfig["startmessage"]
		else:
			self._startmessage = self.default_startmessage
		self.console.write('timelimit %s ' % (mapconfig["timelimit"]))

		# self.debug('onNewMap updated successfully')

		# I want to have it perform an @gear command if gear limits are on
		# if mapconfig["g_gear"] != "0":
		# self.debug("sending gear cmd")
		# these say it but don't "process" it
		# self.console.say("@pagear")
		# self.console.write('@pagear')

		# these don't work
		# self.console.sayLoudOrPM(None, "@pagear")
		# self.console.cmd_pagear(data=None)
			# client2 = Client()
			# client2.id = 1
			# client2 = self.console.storage.getClient(client2)
			# self.powerAdminUrtPlugin.cmd_pagear(data=None, client=client2, cmd="Command<pagear>")

		# command = self._adminPlugin._commands['admins']
		# command.executeLoud(data=None, client=None)
		# command = functions.getCmd(self.powerAdminUrtPlugin, "pagear")
		# command.executeLoud(data=None, client=None)

	####################################################################################################################
	#                                                                                                                  #
	#    COMMANDS                                                                                                      #
	#                                                                                                                  #
	####################################################################################################################

	def cmd_mapconfig(self, data=None, client=None, cmd=None):
		"""
		Set the game settings for this map from the mapconfig table.
		"""
		# cmd.sayLoudOrPM(client, 'dosomething %s' % (sclient.cid))
		mapName = self.console.getMap()
		# mapName = b3.game.getMap()
		self.debug("map name is %s" % mapName)
		self.setMapSettings(mapName)

	def cmd_maplist(self, data=None, client=None, cmd=None):
		"""
		Get the mapcycle.txt map list.
		"""
		self.debug("maplist entered")

		if not self.mapcycle_fileName or self.mapcycle_fileName == "":
			cmd.sayLoudOrPM(client, '^7MapCycle path not set in ini file.')
			return

		# sclient = self._adminPlugin.findClientPrompt(data, client)
		#
		# if not data:
		# 	client.message('^7invalid data, try !help maplist')
		# 	return
		#
		# if not sclient:
		# 	# a player matching the name was not found, a list of closest matches will be displayed
		# 	# we can exit here and the user will retry with a more specific player
		# 	return

		#if platform.system()
		file_timestamp = os.path.getmtime(self.mapcycle_fileName)
		self.debug("maplist: timestamp is %s" % file_timestamp)

		if self.mapcycle_timestamp != file_timestamp:
			# we need to read the file, because we haven't yet or they've changed
			self.debug("maplist: reading mapcycle")
			self.mapcycle = [line.rstrip('\n') for line in open(self.mapcycle_fileName)]
			self.mapcycle_timestamp = file_timestamp

		if self.mapcycle:
			# get the current map and colorize it if it's in the cycle
			mapname = self.console.getMap()
			if mapname in self.mapcycle:
				idx = self.mapcycle.index(mapname)
				self.mapcycle[idx] = "^8" + self.mapcycle[idx] + "^7"
				cmd.sayLoudOrPM(client, '^7MapList: ^2%s' % '^7, ^2'.join(self.mapcycle))
				self.mapcycle[idx] = mapname
			else:
				cmd.sayLoudOrPM(client, '^7MapList: ^2%s' % '^7, ^2'.join(self.mapcycle))
		else:
			cmd.sayLoudOrPM(client, '^7MapList not found')

	def getNextMaps(self, g_nextmap):
		nummaps = len(self.mapcycle)
		try:
			idx = self.mapcycle.index(g_nextmap)
		except ValueError:
			idx = -1
		idx += 2
		self.debug("nextmap: %s; idx: %s; nummaps: %s" % (g_nextmap, idx, nummaps))
		self.debug("cycle is %s" % self.mapcycle)
		if idx <= nummaps:
			g_nextmap2 = self.mapcycle[idx - 1]
		else:
			idx = 1
			g_nextmap2 = self.mapcycle[idx - 1]

		idx += 1
		if idx <= nummaps:
			g_nextmap3 = self.mapcycle[idx - 1]
		else:
			idx = 1
			g_nextmap3 = self.mapcycle[idx - 1]
		return g_nextmap2, g_nextmap3

	def cmd_upcoming(self, data=None, client=None, cmd=None):
		"""
		Show the next 3 upcoming maps.
		"""
		# self.debug("upcoming entered")

		if not self.mapcycle_fileName or self.mapcycle_fileName == "":
			cmd.sayLoudOrPM(client, '^7MapCycle path not set in ini file.')
			return

		# sclient = self._adminPlugin.findClientPrompt(data, client)
		#
		# if not data:
		# 	client.message('^7invalid data, try !help maplist')
		# 	return
		#
		# if not sclient:
		# 	# a player matching the name was not found, a list of closest matches will be displayed
		# 	# we can exit here and the user will retry with a more specific player
		# 	return

		mapname = self.console.getMap()
		# try to catch when it wants to pop right at the beginning of a map.
		# it would mistakenly list the first 3 in the cycle because it didn't catch the current map correctly
		if not mapname or mapname == "":
			return
		g_nextmap = self.console.getNextMap()

		# if nothing changed, just cough up the last string
		if (mapname == self._up_mapname and g_nextmap == self._up_nextmap):
			self.console.say(self._up_next3)
			self.debug("nothing changed")
			return

		file_timestamp = os.path.getmtime(self.mapcycle_fileName)
		self.debug("upcoming: timestamp is %s" % file_timestamp)

		if self.mapcycle_timestamp != file_timestamp:
			# we need to read the file, because we haven't yet or they've changed
			self.debug("upcoming: reading mapcycle")
			self.mapcycle = [line.rstrip('\n').rstrip('\r') for line in open(self.mapcycle_fileName)]
			self.mapcycle_timestamp = file_timestamp

		nummaps = len(self.mapcycle)

		# i believe that g_nextmap will always have a value here because b3 looks at server var g_nextmap and g_nextcyclemap
		if g_nextmap:
			g_nextmap1 = g_nextmap
			self.debug("g_nextmap is set: %s" % g_nextmap)
			pass
		elif mapname in self.mapcycle:
			self.debug("mapname in cycle")
			idx = self.mapcycle.index(mapname)
			idx += 1
			if idx < nummaps:
				g_nextmap1 = self.mapcycle[idx]
			else:
				g_nextmap1 = self.mapcycle[0]
		else:
			self.debug("flowed to else, using start of mapcycle")
			g_nextmap1 = self.mapcycle[0]

		g_nextmap2, g_nextmap3 = self.getNextMaps(g_nextmap1)

		if self.mapcycle:
			# hold the string so we don't need to reprocess unless something changed
			self._up_mapname = mapname
			self._up_nextmap = g_nextmap1
			self._up_next3 = '^7Upcoming: ^2%s^7, ^2%s^7, ^2%s' % (g_nextmap1, g_nextmap2, g_nextmap3)
			self.console.say(self._up_next3)
		else:
			cmd.sayLoudOrPM(client, '^7Upcoming not found')

	def cmd_startmessage(self, data=None, client=None, cmd=None):
		"""
		Repeat the start message from the mapconfig table.
		"""
		self.console.say('Map Start Message: ^8%s' % self._startmessage)
