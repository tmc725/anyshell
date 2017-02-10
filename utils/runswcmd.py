#! /bin/sh
""":"
exec python $0 ${1+"$@"}
"""
#
# -*- coding: utf-8 -*-
#
__version__ = 0.1
__author__ = 'T Chen'
__copyright__ = 'Copyright (c) 2016'
__doc__ = '''Script to run a cmd on the switch'''

import os
import sys
import json
import pdb
import re
from time import sleep
import getopt
import paramiko.client as sc
import socket
import time
import logging
logger = logging.getLogger(__name__)

sys.path.append("../lci")
sys.path.append("../../lci")
sys.path.append("../../../lci")
from nimble.lci_utils import warn_not_exit
from nimble.runcmd import RunCmd
from switch_cmd import SwitchCmd

def vprint(verbose, msg):
    if verbose:
        print(msg)

def run_single_command(target, user, passwd, cmd, verbose):
    try:
        vprint(verbose, 'attempted to log in to %s' % target)
        sw = SwitchCmd(target, user, passwd)
        sw.login()
        vprint(verbose, 'logged in to %s' % target)
        resp = sw.execute(cmd, None)
        print(resp)
        resp = sw.exit()
        vprint(verbose, resp)
        sw.close()
    except Exception as e:
        msg = 'Error running %s on the switch due to %s' % (cmd, e)
        warn_not_exit(msg)
    return resp

def usage():
    print('Usage: runswcmd.py [OPTIONS]\n'
          'A utility program to run a switch command.\n'
          'Options:\n'
          '       -h --help \t\t\tprint this usage\n' 
          '       -u --user=<user_id>\t\tuser for the switch\n'
          '       -p --passwd=<storage_passwd>\tpassword for the switch\n'
          '       -n --num=<number_esxi>\t\tnumber of switches for this script\n'
          '       -f --func=<function>\t\trun a canned function on the switch\n'
          '       -c --cmd=<command>\t\trun a ssh command on the switches\n'
          '       -t --targets=<list of targets>\t\trun a ssh command on targets\n'
          '       -v --verbose \t\t\tprint details\n'
          '       -l --list \t\t\tlist available functions\n'
         )

class Switch(object):
  
    def backup_switch(self, target, user, passwd, verbose=False, node=None, args=None):
        try:
            src = args[0]
            path = args[1]
            vprint(verbose, 'attempted to log in to %s' % target)
            sw = SwitchCmd(target, user, passwd)
            sw.login()
            vprint(verbose, 'logged in to %s' % target)
            resp = sw.execute('copy %s tftp address 172.20.243.1 filename %s data-port' % (src, path), None)
            print(resp)
            resp = sw.exit()
            vprint(verbose, resp)
            sw.close()
        except Exception as e:
            msg = 'Error running backup_switch on the switch due to %s' % e
            warn_not_exit(msg)

    def save_run(self, target, user, passwd, verbose=False, node=None, args=None):
        try:
            vprint(verbose, 'attempted to log in to %s' % target)
            sw = SwitchCmd(target, user, passwd)
            sw.login()
            vprint(verbose, 'logged in to %s' % target)
            resp = sw.execute('write', None)
            print(resp)
            resp = sw.execute('copy run backup', None)
            print(resp)
            resp = sw.exit()
            vprint(verbose, resp)
            sw.close()
        except Exception as e:
            msg = 'Error running save_run on the switch due to %s' % e
            warn_not_exit(msg)

    def enable_ssh(self, target, user, passwd, verbose=False, node=None, args=None):
        try:
            vprint(verbose, 'attempted to log in to %s' % target)
            sw = SwitchCmd(target, user, passwd)
            sw.login()
            vprint(verbose, 'logged in to %s' % target)
            resp = sw.execute('config t', None)
            print(resp)
            resp = sw.execute('ssh enable', None)
            print(verbose, resp)
            resp = sw.execute('ssh scp-enable', None)
            print(verbose, resp)
            resp = sw.exit()
            vprint(verbose, resp)
            resp = sw.execute('write', None)
            print(resp)
            resp = sw.execute('copy run backup', None)
            print(resp)
            resp = sw.exit()
            vprint(verbose, resp)
            sw.close()
        except Exception as e:
            msg = 'Error running enable_switch on the switch due to %s' % e
            warn_not_exit(msg)

    def set_passwd(self, target, user, passwd, verbose=False, node=None, args=None):
        try:
            new_passwd = args[0] if args else 'admin'
            vprint(verbose, 'attempted to log in to %s' % target)
            sw = SwitchCmd(target, user, passwd)
            sw.login()
            vprint(verbose, 'logged in to %s' % target)
            resp = sw.execute('config t', None)
            print(resp)
            resp = sw.execute('access user administrator-password', 'password:')
            print(verbose, resp)
            resp = sw.execute(passwd, ':')
            print(verbose, resp)
            resp = sw.execute(new_passwd, 'password:')
            print(verbose, resp)
            resp = sw.execute(new_passwd, None)
            print(verbose, resp)
            resp = sw.exit()
            vprint(verbose, resp)
            resp = sw.execute('write', None)
            print(resp)
            resp = sw.execute('copy run backup', None)
            print(resp)
            resp = sw.exit()
            vprint(verbose, resp)
            sw.close()
        except Exception as e:
            msg = 'Error running set_passwd on the switch due to %s' % e
            warn_not_exit(msg)

    def set_snmp_server(self, target, user, passwd, verbose=False, node=None, args=None):
        try:
            vprint(verbose, 'attempted to log in to %s' % target)
            sw = SwitchCmd(target, user, passwd)
            sw.login()
            vprint(verbose, 'logged in to %s' % target)
            resp = sw.execute('config t', None)
            print(resp)
            resp = sw.execute('snmp-server read-community public', None)
            print(verbose, resp)
            # switch will log us out
            sw.close()
        except Exception as e:
            msg = 'Error running set_snmp_server on the switch due to %s' % e
            warn_not_exit(msg)

    def no_snmp_server(self, target, user, passwd, verbose=False, node=None, args=None):
        try:
            vprint(verbose, 'attempted to log in to %s' % target)
            sw = SwitchCmd(target, user, passwd)
            sw.login()
            vprint(verbose, 'logged in to %s' % target)
            resp = sw.execute('config t', None)
            print(resp)
            resp = sw.execute('no snmp-server read-community', None)
            print(verbose, resp)
            # switch will log us out
            sw.close()
        except Exception as e:
            msg = 'Error running no_snmp_server on the switch due to %s' % e
            warn_not_exit(msg)

    def disable_telnet(self, target, user, passwd, verbose=False, node=None, args=None):
        try:
            vprint(verbose, 'attempted to log in to %s' % target)
            sw = SwitchCmd(target, user, passwd)
            sw.login()
            vprint(verbose, 'logged in to %s' % target)
            resp = sw.execute('config t', None)
            print(resp)
            resp = sw.execute('no access telnet enable', None)
            print(verbose, resp)
            # switch will log us out
            sw.close()
        except Exception as e:
            msg = 'Error running disable_telnet on the switch due to %s' % e
            warn_not_exit(msg)

    def set_ipv6(self, target, user, passwd, verbose=False, node=None, args=None):
        prefix = args[0]
        prefixlen = args[1]
        node = args[2]
        ipv6 = "%s40::4:%s" % (prefix, node)
        port = 3 if node < 3 else 125
        try:
            vprint(verbose, 'attempted to log in to %s' % target)
            sw = SwitchCmd(target, user, passwd)
            sw.login()
            vprint(verbose, 'logged in to %s' % target)
            resp = sw.execute('config t', None)
            print(resp)
            resp = sw.execute('no interface ip %s' % port, None)
            print(resp)
            resp = sw.exit()
            vprint(verbose, resp)
            sw.close()
        except Exception as e:
            pass

        try:
            sw = SwitchCmd(target, user, passwd)
            sw.login()
            vprint(verbose, 'logged in to %s' % target)
            resp = sw.execute('config t', None)
            print(resp)
            resp = sw.execute('interface ip %s' % port, None)
            print(resp)
            resp = sw.execute('ipv6 address %s %s enable\n' % (ipv6, prefixlen), None)
            print(resp)
            resp = sw.execute('write', None)
            print(resp)
            resp = sw.execute('copy run backup', None)
            print(resp)
            resp = sw.exit()
            vprint(verbose, resp)
            resp = sw.exit()
            vprint(verbose, resp)
            resp = sw.exit()
            vprint(verbose, resp)
            sw.close()
        except Exception as e:
            msg = 'Error running set_ipv6 on the switch due to %s' % e
            print msg
            print 'Retrying...'
            try:
                sw = SwitchCmd(target, user, passwd)
                sw.login()
                vprint(verbose, 'logged in to %s' % target)
                resp = sw.execute('write', None)
                print(resp)
                resp = sw.execute('copy run backup', None)
                print(resp)
                resp = sw.exit()
                vprint(verbose, resp)
            except Exception as e: 
                warn_not_exit(msg)

    def show_ip(self, target, user, passwd, verbose=False, node=None, args=None):
        try:
            vprint(verbose, 'attempted to log in to %s' % target)
            sw = SwitchCmd(target, user, passwd)
            sw.login()
            vprint(verbose, 'logged in to %s' % target)
            resp = sw.execute('show ip int brief', None)
            print(resp)
            resp = sw.exit()
            vprint(verbose, resp)
            sw.close()
        except Exception as e:
            msg = 'Error running show ip on the switch due to %s' % e
            warn_not_exit(msg)

    def show_mac(self, target, user, passwd, verbose=False, node=None, args=None):
        try:
            vprint(verbose, 'attempted to log in to %s' % target)
            sw = SwitchCmd(target, user, passwd)
            sw.login()
            vprint(verbose, 'logged in to %s' % target)
            #resp = sw.execute('show ip int brief', None)
            resp = sw.execute('show mac', None)
            print(resp)
            resp = sw.exit()
            vprint(verbose, resp)
            sw.close()
        except Exception as e:
            msg = 'Error running show mac on the switch due to %s' % e
            warn_not_exit(msg)

if __name__ == "__main__":

    #logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.ERROR)

    if len(sys.argv) == 1:
        usage()
        exit()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "ht:u:p:n:f:vlc:t:t:", ["help", "target=", \
            "user=", "passwd=", "num=", "func=", "verbose", "list", "cmd=", "targets="])
    except getopt.GetoptError as err:
        print str(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    user = "admin"
    passwd = "admin"
    one_func = None
    one_cmd = None
    num_nodes = 4
    verbose = False
    esxi = Switch()
    targets = None
    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-u", "--user"):
            user = a
        elif o in ("-p", "--passwd"):
            passwd = a
        elif o in ("-n", "--num"):
            num_nodes = a
        elif o in ("-f", "--func"):
            one_func = a
        elif o in ("-c", "--cmd"):
            one_cmd = a
        elif o in ("-t", "--targets"):
            targets = a
        elif o in ("-l", "--list"):
            all_members = [x for x in dir(Switch) if not x.startswith('_')]
            all_members_str = ', '.join(all_members)
            print('Possible list of functions are %s' % all_members_str) 
        else:
            assert False, "unhandled option"

    if not one_cmd and not one_func:
        # nothing to do
        sys.exit()

    list_nodes = ['172.20.4.%s'%x for x in range(1, int(num_nodes)+1)] if not targets else \
                 re.split(r'[,;\s]\s*', targets.lstrip().rstrip())
    try:
        vprint(verbose, "Talk to esxi hosts using %s and %s" % (user, passwd))

        vprint(verbose, list_nodes)
        for i, node in enumerate(list_nodes):
            ai = []
            '''
            try:
                for a in socket.getaddrinfo(node, None, socket.AF_INET6, socket.SOCK_STREAM, socket.IPPROTO_TCP):
                    ai.append(a[4][0])
            except:
                pass
            '''
            if not ai:
                ai.append(socket.gethostbyname(node))
            for target in ai:
                vprint(verbose, target)
                if one_func:
                    clist = one_func.split()
                    cmd = clist[0]
                    args = clist[1:] 
                    args.append(i+1)
                    method = getattr(esxi, cmd)
                    print('Running %s on %s using %s' % (cmd, node, target))
                    method(target, user, passwd, verbose, node, args)
                if one_cmd:
                    run_single_command(target, user, passwd, one_cmd, verbose)
                print
    except Exception as e:
        raise

