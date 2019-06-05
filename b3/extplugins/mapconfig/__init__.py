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

__version__ = '0.1'
__author__ = 'isopropanol'

# import b3
# from b3.clients import Client
# import b3.events
import b3.plugin

# from b3 import functions
# from b3.clients import Client
# from b3.functions import getCmd
from ConfigParser import NoOptionError

class MapconfigPlugin(b3.plugin.Plugin):
	# requiresConfigFile = False

	adminPlugin = None
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
		self.adminPlugin = self.console.getPlugin('admin')
		self.powerAdminUrtPlugin = self.console.getPlugin('powerAdminUrtPlugin')

		# register our commands
		#if 'commands' in self.config.sections():
		#	for cmd in self.config.options('commands'):
		#		level = self.config.get('commands', cmd)
		#		sp = cmd.split('-')
		#		alias = None
		#		if len(sp) == 2:
		#			cmd, alias = sp
		#
		#		func = getCmd(self, cmd)
		#		if func:
		#			self._adminPlugin.registerCommand(self, cmd, level, func, alias)

		self.registerEvent('EVT_GAME_ROUND_START', self.onNewMap)

		# # tried to catch the end of the map to announce the next map, but it's not firing.
		# # it might only catch actual match rounds
		# self.registerEvent('EVT_GAME_ROUND_END', self.onMapEnd)

	def onLoadConfig(self):
		"""
		load plugin configuration
		"""
		# NOTE: if you add fields then add them here
		try:
			self.default_capturelimit = self.config.getint('global_settings', 'default_capturelimit')
		except (NoOptionError, ValueError):
			self.default_capturelimit = 8

		self.debug('default_capturelimit : %s' % self.default_capturelimit)

		try:
			self.default_g_suddendeath = self.config.getint('global_settings', 'default_g_suddendeath')
		except (NoOptionError, ValueError):
			self.default_g_suddendeath = 0

		self.debug('default_g_suddendeath : %s' % self.default_g_suddendeath)

		try:
			self.default_g_gear = self.config.getint('global_settings', 'default_g_gear')
		except (NoOptionError, ValueError):
			self.default_g_gear = "0"

		self.debug('default_g_gear : %s' % self.default_g_gear)

		try:
			self.default_g_gravity = self.config.getint('global_settings', 'default_g_gravity')
		except (NoOptionError, ValueError):
			self.default_g_gravity = 800

		self.debug('default_g_gravity : %s' % self.default_g_gravity)

		try:
			self.default_g_friendlyfire = self.config.getint('global_settings', 'default_g_friendlyfire')
		except (NoOptionError, ValueError):
			self.default_g_friendlyfire = 0

		self.debug('default_g_friendlyfire : %s' % self.default_g_friendlyfire)

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
		self.debug('onNewMap map %s', mapName)
		# need to read b3 table to get values

		# NOTE: if you add fields then add them here
		mapconfig = {"id": 0, \
					 "mapname": mapName, \
					 "capturelimit": self.default_capturelimit, \
					 "g_suddendeath": self.default_g_suddendeath, \
					 "g_gear": self.default_g_gear, \
					 "g_gravity": self.default_g_gravity, \
					 "g_friendlyfire": self.default_g_friendlyfire }

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
		# self.debug('onNewMap updated successfully')

		# I want to have it perform an @gear command if gear limits are on
		# if mapconfig["g_gear"] != "0":
		self.debug("sending gear cmd")
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

		# command = self.adminPlugin._commands['admins']
		# command.executeLoud(data=None, client=None)
		# command = functions.getCmd(self.powerAdminUrtPlugin, "pagear")
		# command.executeLoud(data=None, client=None)

	# def onMapEnd(self, event):
	# 	"""
	#	Handle EVT_GAME_ROUND_END
	#	"""
	#	self.debug('onMapEnd map %s', mapName)
	#	nextmap = self.console.getNextMap()
	#	if nextmap:
	#		ad = "^2Next map: ^3" + nextmap
	#		self.console.say(ad)

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
	
		return mapconfig

	####################################################################################################################
	#                                                                                                                  #
	#    COMMANDS                                                                                                      #
	#                                                                                                                  #
	####################################################################################################################

	# def cmd_dosomething(self, data=None, client=None, cmd=None):
	#	if not data:
	#		client.message('^7invalid data, try !help dosomething')
	#		return
	#
	#	sclient = self._adminPlugin.findClientPrompt(data, client)
	#
	#	if not sclient:
	#		# a player matching the name was not found, a list of closest matches will be displayed
	#		# we can exit here and the user will retry with a more specific player
	#		return
	#
	#	# TODO check immunity level
	#	#if sclient.
	#
	#	# -- IPHub
	#
	#	cmd.sayLoudOrPM(client, 'dosomething %s' % (sclient.cid))


