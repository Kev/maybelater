#!/usr/bin/python2.5
"""
    xmppbot.py - Copyright 2008 Kevin Smith
    This file is part of MaybeLater.

    This is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This software is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this software; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""

import logging
import sleekxmpp.sleekxmpp
from optparse import OptionParser
from xml.etree import ElementTree as ET
import os
import time
from django.db.models import Q
from maybelater.models import Task, Project, Context, UserJid, PRIORITIES, EFFORTS
import django

class MaybeLaterXmppBot(sleekxmpp.sleekxmpp.xmppclient):
    def __init__(self, jid, password, ssl=True, plugin_config = {}):
        sleekxmpp.sleekxmpp.xmppclient.__init__(self, jid, password, ssl, plugin_config)
        self.add_event_handler("message", self.handle_message)
        self.add_event_handler("session_start", self.start, threaded=True)
    
    def start(self, event):
        #TODO: make this configurable
        logging.debug("xmppbot.py: start()")
        self.requestRoster()
        self.sendPresence(ppriority=10)
       
    def handle_message(self, event):
        try:
            userJid = UserJid.objects.get(jid=event['jid'])
        except UserJid.DoesNotExist:
            logging.info("Message from unrecognised jid %s/%s '%s'" % (event['jid'], event['resource'], event['message']))
            return
        logging.debug("Creating new task '%s' for user %s from jid %s/%s" %(event['message'], userJid.user.username, event['jid'], event['resource']))
        newTask = Task(name=event['message'], user=userJid.user)
        newTask.save()

        
if __name__ == '__main__':
    optp = OptionParser()
    optp.add_option('-q','--quiet', help='set logging to ERROR', action='store_const', dest='loglevel', const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d','--debug', help='set logging to DEBUG', action='store_const', dest='loglevel', const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v','--verbose', help='set logging to COMM', action='store_const', dest='loglevel', const=5, default=logging.INFO)
    optp.add_option("-c","--config", dest="configfile", default="config.xml", help="set config file to use")
    opts,args = optp.parse_args()
    
    logging.basicConfig(level=opts.loglevel, format='%(levelname)-8s %(message)s')

    #load xml config
    logging.info("xmppbot.py: Loading config file: %s" % opts.configfile)
    config = ET.parse(os.path.expanduser(opts.configfile)).find('auth')
    
    #init
    logging.info("xmppbot.py: Logging in as %s" % config.attrib['jid'])
    
    
    plugin_config = {}
    plugin_config['xep_0092'] = {'name': 'MaybeLater Bot', 'version': 'devel'}
    plugin_config['xep_0199'] = {'keepalive': True, 'timeout': 30, 'frequency': 300}
    
    con = MaybeLaterXmppBot(config.attrib['jid'], config.attrib['pass'], plugin_config=plugin_config)
    if not config.get('server', None):
        # we don't know the server, but the lib can probably figure it out
        con.connect() 
    else:
        con.connect((config.attrib['server'], 5222))
    con.process()
    while con.connected:
        time.sleep(1)