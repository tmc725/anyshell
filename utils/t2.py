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

from nimble.lci_utils import warn_not_exit
from nimble.runcmd import RunCmd

imm_config = None
imm_config_file = '/lci/immconfig.json'
commands = []
imm_hosts = []
reset_cmd = 'users -1 -p PASSW0RD'

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
    
def run_single_command(cmd, verbose):
    vprint(verbose, 'INFO: Ready to send the following commands to the storage:\n%s\n' % cmd)
    status, response, err = conn.execute(cmd)
    print('INFO: cmd execution status for \"%s\" is \n%s\n' % (cmd[:32], (status if status else 'Success')))
    print('INFO: response message is \n%s\n' % (response if response else 'None'))
    print('INFO: error message is \n%s\n' % (err if err else 'None'))

def run_command(cmd, verbose=True):
    if cmd:
        run_single_command(cmd, verbose)
    else:
        pause = 1
        for cmd in commands:
            run_single_command(cmd, verbose)
            sleep(pause)


def usage():
    print('Usage: resetpasswd.py [OPTIONS]\n'
          'A utility program to reset IMM password via SSH.\n'
          'Options:\n'
          '       -h --help \t\t\tprint this usage\n' 
          '       -u --user=<user_id>\t\tuser for the IMM\n'
          '       -p --passwd=<storage_passwd>\tpassword for the IMM\n'
          '       -c --cmd=<command>\t\tNimble OS CLI command\n' 
          '       \t\t\t\t\t\tno command = run an additional command\n' 
         )

if __name__ == "__main__":

    mac = "08:94:ef:13:7f:9d"
    mac_list = mac.split(":")
    first_octet = format(int(mac_list[0], 16), '08b')
    print first_octet
    print first_octet[6]
    first_octet_list = list(first_octet)
    first_octet_list[6] = '1' if first_octet_list[6] == '0' else '0'
    first_octet = ''.join(first_octet_list)
    print first_octet[6]
    ipv6 = "fe80::%s%s:%sff:fe%s:%s%s" % (format(int(first_octet, 2), '02x'), mac_list[1], mac_list[2], \
            mac_list[3], mac_list[4], mac_list[5])
    print ipv6
    sys.exit(0)
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:p:", ["help", \
            "user=", "passwd=", "cmd=", ])
    except getopt.GetoptError as err:
        print str(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    user = "USERID"
    passwd = "Passw0rd!"
    cmd = reset_cmd
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-u", "--user"):
            user = a
        elif o in ("-p", "--passwd"):
            passwd = a
        else:
            assert False, "unhandled option"

    try:
        read_config()
    except Exception as e:
        print("Error: cannot retrieve configurations for imm")

    for h in imm_hosts:
        try:
            conn = RunCmd()
            conn.login(h, user, passwd)
            run_command(cmd)
            # temporary code to set up a route for 10.240.38.73
        except:
            raise
        finally:
            if conn: conn.close()

