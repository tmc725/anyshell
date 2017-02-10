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
__doc__ = '''Script to configure vcenter params'''

import sys
import json
import pdb
from time import sleep
import getopt
import paramiko.client as sc
import socket
import logging
logger = logging.getLogger(__name__)

sys.path.append("/lci")
from nimble.lci_utils import warn_not_exit
from nimble.runcmd import RunCmd

def vprint(verbose, msg):
    if verbose:
        print(msg)
    
def get_conn(target, user, passwd):
    s = sc.SSHClient()
    s.set_missing_host_key_policy(sc.AutoAddPolicy())
    s.connect(target, username=user, password=passwd)
    return s

def run_single_command(target, user, passwd, cmd, verbose):
    vprint(verbose, 'INFO: Ready to send the following commands to the vcenter:\n%s\n' % cmd)
    conn = get_conn(target, user, passwd)
    (stdin, stdout, stderr) = conn.exec_command(cmd)
    for line in stdout.readlines(): print line
    if verbose: 
        for line in stderr.readlines(): print line
    conn.close()

def usage():
    print('Usage: setvcenterparams.py [OPTIONS]\n'
          'A utility program to configure vcenter parameters.\n'
          'Options:\n'
          '       -h --help \t\t\tprint this usage\n' 
          '       -t --target=<vcenter_address>\taddress of the vcenter\n' 
          '       -u --user=<user_id>\t\tuser for the vcenter\n'
          '       -p --passwd=<storage_passwd>\tpassword for the vcenter\n'
          '       -n --num=<number_esxi>\t\tnumber of esxi for the vcenter\n'
          '       -c --cmd=<command>\t\trun a command on the vcenter\n'
          '       -l --list=<nodes>\t\tlist of nodes in the vcenter\n'
          '       -v --verbose \t\t\tprint details\n'
         )

if __name__ == "__main__":

    logging.basicConfig(level=logging.ERROR)

    if len(sys.argv) == 1:
        usage()
        exit()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "ht:u:p:n:c:l:v", ["help", "target=", \
            "user=", "passwd=", "num=", "cmd=", "list=", "verbose"])
    except getopt.GetoptError as err:
        print str(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    target = "127.0.0.1"
    user = "root"
    passwd = "Th1nkAg!le"
    one_cmd = None
    num_nodes = 8
    verbose = False
    list_nodes = []
    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-u", "--user"):
            user = a
        elif o in ("-p", "--passwd"):
            passwd = a
        elif o in ("-n", "--num"):
            num_nodes = a
        elif o in ("-c", "--cmd"):
            one_cmd = a
        elif o in ("-l", "--list"):
            list_nodes = a.split()
        else:
            assert False, "unhandled option"

    try:
        print("Talk to vcenter at %s using %s and %s" % (target, user, passwd))
        cmds = []
        if not one_cmd:
            # First, enable bash 
            cmds.append('shell.set --enabled True')
            for node in list_nodes:
                for ai in socket.getaddrinfo(node, None, socket.AF_INET6, socket.SOCK_STREAM, socket.IPPROTO_TCP):
                    myip = ai[4][0]
                    cmds.append('shell echo {0} {1} >> /etc/hosts'.format(myip, node))
            cmds.append('shell.set --enabled False')
            cmds.append('com.vmware.appliance.version1.networking.dns.servers.set --mode static')
            #cmds.append('com.vmware.appliance.version1.networking.dns.servers.set --servers ""')
            cmds.append('com.vmware.appliance.version1.networking.ipv4.set --interface nic0 --mode dhcp')
            cmds.append('com.vmware.appliance.version1.networking.dns.servers.set --mode dhcp')
        else:
            # First, enable bash 
            cmds.append('shell.set --enabled True')
            for node in list_nodes:
                cmds.append(one_cmd)
            cmds.append('shell.set --enabled False')

        cmd = 'pwd'
        conn = get_conn(target, user, passwd)
        (stdin, stdout, stderr) = conn.exec_command(cmd)
        line = ''
        for l in stdout.readlines(): line += l
        line = line.lstrip().rstrip()
        conn.close()
        # test if shell is appliance. If not, set it to be.
        if line == '/root':
            vprint(verbose, "Bash!!!!!")
            conn = get_conn(target, user, passwd)
            (stdin, stdout, stderr) = conn.exec_command('chsh -s /bin/appliancesh')
            for line in stdout.readlines(): print line
            conn.close()
         
        for cmd in cmds:
            run_single_command(target, user, passwd, cmd, verbose)
 
    except:
        raise

