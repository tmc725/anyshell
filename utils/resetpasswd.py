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
__doc__ = '''Script to reset IMM password''' 

#from Exscript.util.start import start
#from Exscript.util.file  import get_hosts_from_file
import sys
import json
import pdb
from time import sleep
import getopt
import logging
logger = logging.getLogger(__name__)

sys.path.append("../lci")
sys.path.append("../../lci")
from nimble.lci_utils import warn_not_exit
from nimble.runcmd import RunCmd

imm_config = None
imm_config_file = '/lci/utils/immconfig.json'
commands = []
imm_hosts = []
#reset_cmd = 'resetsp'
reset_cmd = 'users -1 -p PASSW0RD'
resetsp_cmd = 'resetsp'
dhcp_cmd = 'ifconfig eth0 -c dhcp'
default_cmd = 'restoredefaults'

def build_hosts():
    global imm_hosts
    for n in imm_config['nodes']:
        imm_hosts.append(n)

def read_config():
    global imm_config
    config_file = imm_config_file
    try:
        with open(config_file) as imm_json_file:
            imm_config = json.load(imm_json_file)
    except Exception as e:
        warn_not_exit('Error: unable to load config file due to %s' % e)

    try:
        build_hosts()
    except Exception as e:
        warn_not_exit('Error: unable to build a config string due to %s' % e)

def vprint(verbose, msg):
    if verbose:
        print(msg)
    
def run_single_command(conn, cmd, verbose):
    vprint(verbose, 'INFO: Ready to send the following commands to the storage:\n%s\n' % cmd)
    status, response, err = conn.execute(cmd)
    print('INFO: cmd execution status for \"%s\" is \n%s\n' % (cmd[:32], (status if status else 'Success')))
    print('INFO: response message is \n%s\n' % (response if response else 'None'))
    print('INFO: error message is \n%s\n' % (err if err else 'None'))

def run_command(conn, cmd, verbose=True):
    if cmd:
        run_single_command(conn, cmd, verbose)

def usage():
    print('Usage: resetpasswd.py [OPTIONS]\n'
          'A utility program to reset IMM password via SSH.\n'
          'Options:\n'
          '       -h --help \t\t\tprint this usage\n' 
          '       -u --user=<user_id>\t\tuser for the IMM\n'
          '       -p --passwd=<passwd>\tpassword for the IMM\n'
          '       -a --addr=<address>\t\tMac address for IMM\n' 
         )

if __name__ == "__main__":
   
    logging.basicConfig(level=logging.DEBUG)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:p:a:", ["help", \
            "user=", "passwd=", "addr=", ])
    except getopt.GetoptError as err:
        print str(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    user = "USERID"
    #passwd = "PASSW0RD"
    passwd = "Th1nkAg!le"
    addr = None
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
        else:
            assert False, "unhandled option"

    if not addr:
        try:
            read_config()
        except Exception as e:
            print("Error: cannot retrieve configurations for imm")
    else:
        imm_hosts.append(addr)

    conn = None
    for h in imm_hosts:
        try:
            conn = RunCmd()
            conn.login(h, user, passwd)
            run_command(conn, reset_cmd)
            #run_command(conn, dhcp_cmd)
            #run_command(conn, default_cmd)
            # temporary code to set up a route for 10.240.38.73
        except Exception as e:
            print('Failed to reset password for %s due to %s' % (h, e))  
        finally:
            if conn: conn.close()

