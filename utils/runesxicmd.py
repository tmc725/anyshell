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
__doc__ = '''Script to run a cmd on the esxi host'''

import os
import sys
import json
import pdb
import re
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
    vprint(verbose, 'INFO: Ready to send the following commands to the esxi at %s:\n%s\n' % (target, cmd))
    conn = get_conn(target, user, passwd)
    (stdin, stdout, stderr) = conn.exec_command(cmd)
    resp = ''
    for line in stdout.readlines(): 
        resp += line
        print line
    error = ''
    for line in stderr.readlines(): 
        error += line
        if verbose: 
            print line
    conn.close()
    return resp, error

def usage():
    print('Usage: runesxicmd.py [OPTIONS]\n'
          'A utility program to run a command on esxi hosts.\n'
          'Options:\n'
          '       -h --help \t\t\tprint this usage\n' 
          '       -u --user=<user_id>\t\tuser for the esxi host\n'
          '       -p --passwd=<storage_passwd>\tpassword for the esxi host\n'
          '       -n --num=<number_esxi>\t\tnumber of esxi for the vcenter\n'
          '       -f --func=<function>\t\trun a canned function on esxi hosts\n'
          '       -c --cmd=<command>\t\trun a ssh command on esxi hosts\n'
          '       -t --targets=<list of targets>\t\trun a ssh command on targets\n'
          '       -v --verbose \t\t\tprint details\n'
          '       -l --list \t\t\tlist available functions\n'
         )

class ESXi(object):
  
    def get_scratch_config(self, target, user, passwd, verbose=False, node=None, args=None):
        cmd = 'vim-cmd hostsvc/advopt/view ScratchConfig.ConfiguredScratchLocation'    
        run_single_command(target, user, passwd, cmd, verbose)

    def set_autostart(self, target, user, passwd, verbose=False, node=None, args=None):
        cmd = 'vim-cmd hostsvc/autostartmanager/enable_autostart true'
        run_single_command(target, user, passwd, cmd, verbose)
        cmd = 'vim-cmd vmsvc/getallvms'
        resp, error = run_single_command(target, user, passwd, cmd, verbose)
        vm_lines = resp.split('\n')[1:]
        order = 1
        for line in vm_lines:
            id = line.lstrip(' ').split(' ')[0]
            cmd = 'vim-cmd hostsvc/autostartmanager/update_autostartentry %s poweron 60 %s suspend 60 no' % (id, order)
            print cmd
            run_single_command(target, user, passwd, cmd, verbose)
            order += 1
        cmd = 'vim-cmd hostsvc/autostartmanager/get_autostartseq'
        run_single_command(target, user, passwd, cmd, verbose)

    def set_scratch_config(self, target, user, passwd, verbose=False, node=None, args=None):
        folder = args if args else '/vmfs/volumes/Storage1-vmfs1/%s'%node
        cmd = 'mkdir -p %s' % folder
        run_single_command(target, user, passwd, cmd, verbose)
        cmd = 'vim-cmd hostsvc/advopt/view ScratchConfig.ConfiguredScratchLocation'
        resp, error = run_single_command(target, user, passwd, cmd, verbose)
        #print resp
        #print resp.split('\n')[3].lstrip().split(' ')[2]
        #cmd = 'cp -rf %s/* %s' % (resp.split('\n')[3].lstrip().split(' ')[2], folder)
        #run_single_command(target, user, passwd, cmd, verbose)
        cmd = 'vim-cmd hostsvc/advopt/update ScratchConfig.ConfiguredScratchLocation string %s' % folder
        run_single_command(target, user, passwd, cmd, verbose)
        cmd = 'vim-cmd hostsvc/advopt/view ScratchConfig.ConfiguredScratchLocation'
        resp, error = run_single_command(target, user, passwd, cmd, verbose)

    def backup_config(self, target, user, passwd, verbose=False, node=None, args=None):
        folder = args if args else '/vmfs/volumes/Storage1-vmfs1/backup/%s/'%node
        cmd = 'mkdir -p %s' % folder
        run_single_command(target, user, passwd, cmd, verbose)
        cmd = 'vim-cmd hostsvc/firmware/sync_config'
        resp, error = run_single_command(target, user, passwd, cmd, verbose)
        cmd = 'vim-cmd hostsvc/firmware/backup_config'
        resp, error = run_single_command(target, user, passwd, cmd, verbose)
        sl = resp.split()[6].split('/')
        src = '/scratch/%s/%s/%s'%(sl[3],sl[4],sl[5])
        cmd = 'cp -rf %s %s' % (src, folder)
        resp, error = run_single_command(target, user, passwd, cmd, verbose)

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

    user = "root"
    passwd = "Th1nkAg!le"
    one_func = None
    one_cmd = None
    num_nodes = 14
    verbose = False
    esxi = ESXi()
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
            all_members = [x for x in dir(ESXi) if not x.startswith('_')]
            all_members_str = ', '.join(all_members)
            print('Possible list of functions are %s' % all_members_str) 
        else:
            assert False, "unhandled option"

    if not one_cmd and not one_func:
        # nothing to do
        sys.exit()

    list_nodes = []
    if targets:
        list_nodes = re.split(r'[,;\s]\s*', targets.lstrip().rstrip())
    else:
        if num_nodes > 0 and num_nodes < 10:
            list_nodes = ['ch01n0%s'%x for x in range(1, int(num_nodes)+1)] 
        elif num_nodes >= 10 and num_nodes <= 14:
            list_nodes = ['ch01n0%s'%x for x in range(1, 10)] 
            list_nodes += ['ch01n1%s'%x for x in range(0, int(num_nodes)-9)] 
        elif num_nodes > 14 and num_nodes < 24:
            list_nodes = ['ch01n0%s'%x for x in range(1, 10)] 
            list_nodes += ['ch01n1%s'%x for x in range(0, 5)]
            list_nodes += ['ch02n0%s'%x for x in range(1, int(num_nodes)-13)]
        else:
            list_nodes = ['ch01n0%s'%x for x in range(1, 10)] 
            list_nodes += ['ch01n1%s'%x for x in range(0, 5)]
            list_nodes += ['ch02n0%s'%x for x in range(1, 10)]
            list_nodes += ['ch02n1%s'%x for x in range(0, int(num_nodes)-23)]

    try:
        vprint(verbose, "Talk to esxi hosts using %s and %s" % (user, passwd))

        vprint(verbose, list_nodes)
        for node in list_nodes:
            ai = []
            for a in socket.getaddrinfo(node, None, socket.AF_INET6, socket.SOCK_STREAM, socket.IPPROTO_TCP):
                ai.append(a[4][0])
            if not ai:
                ai.append(socket.gethostbyname(node))
            for target in ai:
                vprint(verbose, target)
                if one_func:
                    clist = one_func.split()
                    cmd = clist[0]
                    args = clist[1:] 
                    method = getattr(esxi, cmd)
                    print('Running %s on %s' % (cmd, node))
                    method(target, user, passwd, verbose, node, args)
                if one_cmd:
                    run_single_command(target, user, passwd, one_cmd, verbose)
    except Exception as e:
        raise

