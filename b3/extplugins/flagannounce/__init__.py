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

# from b3.functions import getCmd
from ConfigParser import NoOptionError

class FlagannouncePlugin(b3.plugin.Plugin):
    # requiresConfigFile = True
    # requiresPlugins = ['admin']
    _adminPlugin = None
    _immunity_level = None
    _red_score = 0
    _blue_score = 0
    _has_red = ""
    _has_blue = ""

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

        # register our commands
        # if 'commands' in self.config.sections():
        #    for cmd in self.config.options('commands'):
        #        level = self.config.get('commands', cmd)
        #        sp = cmd.split('-')
        #        alias = None
        #        if len(sp) == 2:
        #            cmd, alias = sp
        #
        #        func = getCmd(self, cmd)
        #        if func:
        #            self._adminPlugin.registerCommand(self, cmd, level, func, alias)

        self.registerEvent('EVT_CLIENT_ACTION', self.onAction)
        self.registerEvent('EVT_GAME_ROUND_START', self.onNewMap)

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
        # self.debug("FlagAnnc: %s by %s" % (edata, cname))

        # think of it as "flag captured at COLOR:
        if event.data == 'team_CTF_redflag':
            self._has_red = event.client.name
            # self.debug("DK: _has_red %s" % self._has_red)
        elif event.data == 'team_CTF_blueflag':
            self._has_blue = event.client.name
            # self.debug("DK: _has_blue %s" % self._has_blue)
        if event.data in 'flag_captured':
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

            # self.debug("DK: FlagAnnounce Red: %s; Blue: %s" % (self._red_score, self._blue_score))

        # self.debug("DK: FlagAnnounce %s Red: %s by has_blue %s; Blue: %s by has_red %s" % (event.data, self._red_score, self._has_blue, self._blue_score, self._has_red))

    def onNewMap(self, event):
        """
        Handle EVT_GAME_ROUND_START
        """
        self._red_score = 0
        self._blue_score = 0
        self._has_red = ""
        self._has_blue = ""

    ####################################################################################################################
    #                                                                                                                  #
    #    OTHER METHODS                                                                                                 #
    #                                                                                                                  #
    ####################################################################################################################

    ####################################################################################################################
    #                                                                                                                  #
    #    COMMANDS                                                                                                      #
    #                                                                                                                  #
    ####################################################################################################################
