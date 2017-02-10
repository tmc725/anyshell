#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
__version__ = 0.1
__author__ = 'T Chen'
__copyright__ = 'Copyright (c) 2016'
__doc__ = '''Collections of utility functions to run a telnet command to a gswitch'''

import select
import re
import sys
import logging
import socket
import pdb
import time
import telnetlib

logger = logging.getLogger(__name__)

class SwitchCmd(object):

    '''   
        Telnetlib wrapper to run a switch command
    '''   

    def __init__(self, target='localhost', user=None, passwd=None, timeout=30):
        self.tn = None
        self.target = target
        self._username = user
        self._password = passwd
        self._timeout = timeout
        self._prompt = '#'
        logging.getLogger("telnetlib").setLevel(logging.WARNING)


    def login(self, timeout=None):
        try:
            self.tn = telnetlib.Telnet(self.target)
            r = self.tn.read_until(': ', timeout=1)
            print r
            #if r.lower().endswith("login: ") or r.lower().endswith("username: "):
            if "login:" in r.lower() or "username:" in r.lower():
                self.tn.write(self._username + '\n')
                r = self.tn.read_until('password: ', timeout=self._timeout)
            #if r.lower().endswith("password: "):
            if "password:" in r.lower():
                self.tn.write(self._password + '\n')
            else:
                raise Exception('unexpected login string')
            self.tn.read_until('>')
            self.tn.write('en\n')
            self.tn.read_until(self._prompt)
            self.tn.write('terminal-length 0\n')
            self.tn.read_until(self._prompt)
            self.tn.write('terminal dont-ask\n')
            self.tn.read_until(self._prompt)
        except Exception as e:
            msg = "ERROR: failed to log in to %s due to %s" % (self.target, e)
            raise LoginFailure(msg)

    def execute(self, command, expect):
        resp = None
        try:
            self.tn.write(command + '\n')
            if expect:
                resp = self.tn.read_until(expect, timeout=self._timeout)
            else:
                resp = self.tn.read_until(self._prompt, timeout=self._timeout)
        except Exception as e:
            msg = "ERROR: failed to execute %s due to %s" % (command, e)
            raise ProtocolException(msg)
        return resp

    def exit(self):
        resp = None
        try:
            self.tn.write('exit\n')
            resp = self.tn.read_until(self._prompt, timeout=self._timeout)
        except Exception as e:
            msg = "ERROR: failed to execute %s due to %s" % ('exit', e)
            resp = msg
            
        return resp

    def close(self):
        self.__del__()

    def __del__(self):
        try:
            pass
        except Exception as e:
            msg = "ERROR: failed to close the connection due to %s" % e
            raise ProtocolException(msg)
        finally:
            if self.tn: self.tn.close()
            self.tn = None

#Custom Exception For Unsupported Operations
class LoginFailure(Exception):
    def __init__(self, *args):
        self.args = args
        if len(args)>0:
            self.msg = args[0]
        else:
            self.msg = ""

#Custom Exception For Unsupported Operations
class ProtocolException(Exception):
    def __init__(self, *args):
        self.args = args
        if len(args)>0:
            self.msg = args[0]
        else:
            self.msg = ""

