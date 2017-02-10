#! /bin/sh
""":"
exec python $0 ${1+"$@"}
"""
#
# -*- coding: utf-8 -*-
#
__version__ = 0.1
__author__ = 'T Chen'
__copyright__ = 'Copyright (c) 2017'
__doc__ = '''ThinkAgile CX specific primitives''' 

import sys
import os
import json
import pdb
from time import sleep
import getopt
import logging
logger = logging.getLogger(__name__)
import re
import socket
import paramiko.client as sc
sys.path.append(os.environ["SHELLBASE"])

def usage():
    print('Usage: resetpasswd.py [OPTIONS]\n'
          'A utility program to reset IMM password via SSH.\n'
          'Options:\n'
          '       -h --help \t\t\tprint this usage\n' 
          '       -u --user=<user_id>\t\tuser for the IMM\n'
          '       -p --passwd=<passwd>\tpassword for the IMM\n'
          '       -a --addr=<address>\t\tAddress for the IMM\n' 
          '       -f --func=<function>\t\tRun a function for the IMM\n'
          '       -c --cmd=<command>\t\tRun a command  for the IMM\n'
          '       -l --list\t\tList all possible functions\n' 
          '       -v --verbose\t\tVerbose mode\n' 
         )

class CXBase(object):

    def __init__(self, *args, **kwargs):
        self.user = kwargs['user'] if 'user' in kwargs else 'root'
        self.passwd = kwargs['passwd'] if 'passwd' in kwargs else 'Th1nkAg!le'

    def __str__(self):
        return self.print_dict(self.__dict__)

    def print_dict(self, dict):

        text = "All current attributes:\n"
        text += "%s\n" % ("*" * 30)

        dict_keys = dict.keys()
        dict_keys.sort()
        for key in dict_keys:
            if key.startswith("_"): continue

            text += "%s : %s\n" % (key.ljust(30), dict[key])

        return text

    def __repr__(self):

        text = self.__class__.__name__

        for attribute in ["alias", "name", "href"]:
            try:
                text += " '%s'" % getattr(self, attribute)
                break
            except AttributeError:
                pass

        if hasattr(self, "ipv6"):
            text += " at %s in %s" % (self.ipv6, self.dc)

        return text

class IMM(CXBase):

    def __init__(self, *args, **kwargs):
        super(IMM, self).__init__(*args, **kwargs)

class Host(CXBase):

    def __init__(self, *args, **kwargs):
        super(Host, self).__init__(*args, **kwargs)

class Switch(CXBase):

    def __init__(self, *args, **kwargs):
        super(Switch, self).__init__(*args, **kwargs)

class Nimble(CXBase):

    def __init__(self, *args, **kwargs):
        super(Nimble, self).__init__(*args, **kwargs)

class CMM(CXBase):

    def __init__(self, *args, **kwargs):
        super(CMM, self).__init__(*args, **kwargs)

class Vcenter(CXBase):

    def __init__(self, *args, **kwargs):
        super(Vcenter, self).__init__(*args, **kwargs)

class LXCA(CXBase):

    def __init__(self, *args, **kwargs):
        super(LXCA, self).__init__(*args, **kwargs)

class CX(object):

    def __init__(self, *args, **kwargs):
        self.name = self.__class__.__name__

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.print_dict(self.__dict__)

    def print_dict(self, dict):

        text = "All current attributes:\n"
        text += "%s\n" % ("*" * 30)

        dict_keys = dict.keys()
        dict_keys.sort()
        for key in dict_keys:
            if key.startswith("_"): continue

            text += "%s : %s\n" % (key.ljust(30), dict[key])

        return text 

    def initialize(self, fname='/etc/hosts'):

        ip=get_ipython()
        dc = ip.user_ns['cx']
        ip.user_ns['imms'] = dc.imms = imms = []
        ip.user_ns['hosts'] = dc.hosts = hosts = []
        ip.user_ns['switches'] = dc.switches = switches = []
        ip.user_ns['storage'] = dc.storage = storage = []
        ip.user_ns['cmms'] = dc.cmms = cmms = []
        namesuffix = prefix = None
        vcenter = None
        lxca = None
        try:
            with open(fname, "r") as f:
                for line in f:
                    if ":" in line:
                        line_tokens = line.split()
                        tokens = line_tokens[0].split(":")
                        if not prefix: 
                            prefix = ':'.join(tokens[0:3])
                            namesuffix = ''.join([tokens[0][2:], tokens[1], tokens[2]])

                        #pdb.set_trace()
                        if tokens[-2] == '1':
                            if 'vcenter' in line_tokens[-1]:
                                ip.user_ns['vcenter'] = vcenter = Vcenter(user='Administrator@lci.lenovo.local')
                                vcenter.ipv6 = line_tokens[0]
                                vcenter.name = line_tokens[-1]
                                vcenter.dc = ip.user_ns['cx']
                            elif 'lxca' in line_tokens[-1]:
                                ip.user_ns['lxca'] = lxca = LXCA(user='admin')
                                lxca.ipv6 = line_tokens[0]
                                lxca.name = line_tokens[-1]
                                lxca.dc = ip.user_ns['cx']
                        elif tokens[-2] == '2':
                            host = Host()
                            hosts.append(host)
                            host.ipv6 = line_tokens[0]  
                            host.name = line_tokens[-1]
                            host.dc = ip.user_ns['cx']
                            imm = IMM(user='USERID')
                            imms.append(imm)
                            imm.ipv6 = '%s:40::3:%s' % (prefix, tokens[-1])
                            imm.dc = ip.user_ns['cx']
                        elif tokens[-2] == '4':
                            sw = Switch(user='admin')
                            switches.append(sw)
                            sw.ipv6 = line_tokens[0]  
                            sw.name = line_tokens[-1]
                            sw.dc = ip.user_ns['cx']
                        elif tokens[-2] == '10':
                            cmm = CMM(user='USERID')
                            cmms.append(cmm)
                            cmm.ipv6 = line_tokens[0]  
                            cmm.name = line_tokens[-1]
                            cmm.dc = ip.user_ns['cx']
        except:
            pass

        dc.prefix = prefix
        dc.namesuffix = namesuffix
        dc.name = 'ThinkAgile CX %s' % namesuffix
        st = Nimble()
        st.ip = '172.20.5.1'
        st.name = 'Lenovo Array %s' % namesuffix
        st.dc = dc
        storage.append(st)
 
if __name__ == "__main__":
   
    logging.basicConfig(level=logging.ERROR)

    if len(sys.argv) == 1:
        usage()
        exit()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:p:a:vf:c:l", ["help", \
            "user=", "passwd=", "addr=", "verbose", "func=", "cmd=", "list", ])
    except getopt.GetoptError as err:
        print str(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    user = "USERID"
    #passwd = "PASSW0RD"
    passwd = "Th1nkAg!le"
    addr = None
    one_cmd = None
    one_func = None
    imm = IMM()
    verbose = False
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-u", "--user"):
            user = a
        elif o in ("-p", "--passwd"):
            passwd = a
        elif o in ("-a", "--addr"):
            addr = a
        elif o in ("-f", "--func"):
            one_func = a
        elif o in ("-c", "--cmd"):
            one_cmd = a
        elif o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-l", "--list"):
            all_members = [x for x in dir(CX) if not x.startswith('_')]
            all_members_str = ', '.join(all_members)
            print('Possible list of functions are %s' % all_members_str)
        else:
            assert False, "unhandled option"

