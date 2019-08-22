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

__version__ = '0.1'
__author__  = 'isopropanol'

import b3
import b3.events
import b3.plugin
import datetime

from b3.functions import getCmd
from ConfigParser import NoOptionError
from b3.storage import mapresult

class FlagannouncePlugin(b3.plugin.Plugin):
    # requiresConfigFile = True
    # requiresPlugins = ['admin']
    _adminPlugin = None
    _poweradminPlugin = None
    _immunity_level = None
    _red_score = 0
    _blue_score = 0
    _has_red = ""
    _has_blue = ""
    _shuffle_score_diff = 0
    _shuffle_now_diff = 0
    _shuffle_now_map = ""
    _warmup = False
    _capture_map_results = False
    # variables for mapresults
    _mapname = ""
    _start_time = None
    _low_player = 99
    _high_player = 0

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
        self._poweradminPlugin = self.console.getPlugin('poweradminurt')

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

        self.registerEvent('EVT_CLIENT_ACTION', self.onAction)
        self.registerEvent('EVT_GAME_ROUND_START', self.onNewMap)
        self.registerEvent('EVT_GAME_ROUND_END')
        self.registerEvent('EVT_GAME_EXIT')

    def onLoadConfig(self):
        """
        load plugin configuration
        """
        try:
            self._shuffle_score_diff = self.config.getint('settings', 'shuffle_score_diff')
            self.debug('loaded settings/shuffle_score_diff: %s' % self._shuffle_score_diff)
        except NoOptionError:
            self.warning('could not find settings/shuffle_score_diff in config file, '
                         'using default: %s' % self._shuffle_score_diff)
        except KeyError, e:
            self.error('could not load settings/shuffle_score_diff config value: %s' % e)
            self.debug('using default value (%s) for settings/shuffle_score_diff' % self._shuffle_score_diff)

        try:
            self._shuffle_now_diff = self.config.getint('settings', 'shuffle_now_diff')
            self.debug('loaded settings/shuffle_now_diff: %s' % self._shuffle_now_diff)
        except NoOptionError:
            self.warning('could not find settings/shuffle_now_diff in config file, '
                         'using default: %s' % self._shuffle_now_diff)
        except KeyError, e:
            self.error('could not load settings/shuffle_now_diff config value: %s' % e)
            self.debug('using default value (%s) for settings/shuffle_now_diff' % self._shuffle_now_diff)

        try:
            self._capture_map_results = self.getSetting('settings', 'capture_map_results', b3.BOOL, self._capture_map_results)
            self.debug('loaded settings/capture_map_results: %s' % self._capture_map_results)
        except NoOptionError:
            self.warning('could not find settings/capture_map_results in config file, '
                         'using default: %s' % self._capture_map_results)
        except KeyError, e:
            self.error('could not load settings/capture_map_results config value: %s' % e)
            self.debug('using default value (%s) for settings/capture_map_results' % self._capture_map_results)

    ####################################################################################################################
    #                                                                                                                  #
    #   EVENTS                                                                                                         #
    #                                                                                                                  #
    ####################################################################################################################

    def onAction(self, event):
        """
        Handle EVT_CLIENT_ACTION.
        """
        # edata = event.data
        # cname = event.client.name
        # if not cname:
        #     cname = "none?"
        # self.debug("FlagAnnounce: %s by %s" % (edata, cname))

        # think of it as "flag captured at COLOR:
        if event.data == 'team_CTF_redflag':
            self._has_red = event.client.name
            # self.debug("DK: _has_red %s" % self._has_red)
        elif event.data == 'team_CTF_blueflag':
            self._has_blue = event.client.name
            # self.debug("DK: _has_blue %s" % self._has_blue)
        if event.data in 'flag_captured':
            self._warmup = True
            # self.debug("DK: name: %s; has_blue %s; has_red %s" % (event.client.name, self._has_blue, self._has_red))
            caplimit = self.console.getCvar('capturelimit').getInt()
            if event.client.name == self._has_blue:
                self._red_score += 1
                # self.debug("DK: red scored %s" % self._has_blue)
                if caplimit - self._red_score > 0:
                    self.console.say(self.getMessage('red_flags_to_limit', (caplimit - self._red_score)))
            elif event.client.name == self._has_red:
                self._blue_score += 1
                # self.debug("DK: blue scored %s" % self._has_red)
                if caplimit - self._blue_score > 0:
                    self.console.say(self.getMessage('blue_flags_to_limit', (caplimit - self._blue_score)))

            self.debug("FlagAnnounce Red: %s; Blue: %s" % (self._red_score, self._blue_score))

            self.checkPlayerCount()

            # self.debug("FlagAnnounce %s Red: %s by has_blue %s; Blue: %s by has_red %s"
            #            % (event.data, self._red_score, self._has_blue, self._blue_score, self._has_red))
            if (self._shuffle_now_diff > 0
                    and self._shuffle_now_diff == abs(self._red_score - self._blue_score)):
                mapName = self.console.getMap()
                if (mapName != self._shuffle_now_map):
                    self.debug("Running shuffle now")
                    self._shuffle_now_map = mapName
                    self._poweradminPlugin.cmd_paskuffle()

    def onNewMap(self, event):
        """
        Handle EVT_GAME_ROUND_START
        """
        # self.debug("DK: shuffle diff %s; actual diff %s; (red %s; blue %s)" % (self._shuffle_score_diff, abs(self._red_score - self._blue_score), self._red_score, self._blue_score))

        if self._warmup:
            # this catches the original map load
            self._warmup = False
        else:
            # this runs after warmup ends
            self._mapname = self.console.getMap()

            # shuffle if the score difference is set and the difference is at least that value
            if self._shuffle_score_diff > 0 and abs(self._red_score - self._blue_score) >= self._shuffle_score_diff:
                self.debug("FlagAnnounce: shuffling due to last map cap difference %s >= %s" % (abs(self._red_score - self._blue_score), self._shuffle_score_diff))
                # do i need to start a new thread and wait 30 seconds first?
                self._poweradminPlugin.cmd_paskuffle()

            self._red_score = 0
            self._blue_score = 0
            self._has_red = ""
            self._has_blue = ""
            self._start_time = datetime.datetime.now()
            self._low_player = 99
            self._high_player = 0

    def onEvent(self, event):
        if (event.type == self.console.getEventID('EVT_GAME_EXIT')) or \
                (event.type == self.console.getEventID('EVT_GAME_ROUND_END')):

            # if (event.type == self.console.getEventID('EVT_GAME_EXIT')):
            #     self.debug("EVT_GAME_EXIT")
            # if (event.type == self.console.getEventID('EVT_GAME_ROUND_END')):
            #     self.debug("EVT_GAME_ROUND_END")

            # getmap doesn't work after mapexit, it returns "None"
            # but this event is firing twice as mapexit, so use the second one to actually write
            localmapname = self.console.getMap()

            if not localmapname:
                maptime = "00:00"
                if self._start_time:
                    timediff = datetime.datetime.now() - self._start_time
                    diffminutes, diffseconds = divmod(timediff.seconds, 60)
                    maptime = "%02i:%02i" % (diffminutes, diffseconds)
                self.debug("onEvent %s. Red %s, Blue %s; map time %s; low-high %s-%s; localmapname: %s"
                           % (self._mapname, self._red_score, self._blue_score, maptime, self._low_player, self._high_player, localmapname))

                # NOTE: for some reason this fires before the final cap is counted, so update from poweradmin (doesn't work)
                # self._red_score, self._blue_score = self._poweradminPlugin.getTeamScores()

                mapresult1 = mapresult(self._mapname, self._red_score, self._blue_score, maptime,
                                       self._low_player, self._high_player, None, None)
                # self.debug("DK: made it past")
                self.console.storage.setMapResult(mapresult1)
                # return 0

    ####################################################################################################################
    #                                                                                                                  #
    #    OTHER METHODS                                                                                                 #
    #                                                                                                                  #
    ####################################################################################################################

    def checkPlayerCount(self):
        clients = self.console.clients.getList()
        players = len(clients)
        for rec in clients:
            self.debug(rec.name)
        self.debug("DK: player count: %s" % players)
        if self._low_player > players:
            self._low_player = players
        if self._high_player < players:
            self._high_player = players

    ####################################################################################################################
    #                                                                                                                  #
    #    COMMANDS                                                                                                      #
    #                                                                                                                  #
    ####################################################################################################################

    def cmd_faset(self, data=None, client=None, cmd=None):
        # self.debug("faset entered")

        # auto pull the map name
        self._mapname = self.console.getMap()

        m = self._adminPlugin.parseUserCmd(data)
        if not m:
            client.message('^7Missing data, try !help faset')
            return False

        self.debug("FASet: %s red %s blue %s" % (self._mapname, m[0], m[1]))
        self._red_score = m[0]
        self._blue_score = m[1]
        # NOTE: for some reason this fires before the final cap is counted, so update from poweradmin (doesn't work)
        # self._red_score, self._blue_score = self._poweradminPlugin.getTeamScores()

        if not self._start_time:
            self._start_time = datetime.datetime.now()

        self.checkPlayerCount()

        cmd.sayLoudOrPM(client, '^7FlagAnnounce set %s ^1Red %s^7, ^4Blue %s^7. Low-High %s-%s'
                        % (self._mapname, self._red_score, self._blue_score, self._low_player, self._high_player))


    def cmd_fashow(self, data=None, client=None, cmd=None):
        # self.debug("fashow entered")

        cmd.sayLoudOrPM(client, '^7FlagAnnounce %s ^1Red %s^7, ^4Blue %s^7. Low-High %s-%s'
                        % (self._mapname, self._red_score, self._blue_score, self._low_player, self._high_player))
