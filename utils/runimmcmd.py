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
__doc__ = '''Script to run IMM cmds''' 

#from Exscript.util.start import start
#from Exscript.util.file  import get_hosts_from_file
import sys
import json
import pdb
from time import sleep
import getopt
import logging
logger = logging.getLogger(__name__)
import re
import socket
import paramiko.client as sc

sys.path.append("/lci")
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
vpd_sys_cmd = 'vpd sys'
vpd_imm_cmd = 'vpd imm'
vpd_uefi_cmd = 'vpd uefi'
vpd_dsa_cmd = 'vpd dsa'
vpd_comp_cmd = 'vpd comp'
vpd_fw_cmd = 'vpd fw'
vpd_pcie_cmd = 'vpd pcie'
clearcfg_cmd = "clearcfg"

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

def get_conn(target, user, passwd):
    s = sc.SSHClient()
    s.set_missing_host_key_policy(sc.AutoAddPolicy())
    s.connect(target, username=user, password=passwd)
    return s
    
def run_single_command(target, user, passwd, cmd, verbose):
    vprint(verbose, 'INFO: Ready to send the following commands to IMM at %s:\n%s\n' % (target, cmd))
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
          '       -a --addr=<address>\t\tAddress for the IMM\n' 
          '       -f --func=<function>\t\tRun a function for the IMM\n'
          '       -c --cmd=<command>\t\tRun a command  for the IMM\n'
          '       -l --list\t\tList all possible functions\n' 
          '       -v --verbose\t\tVerbose mode\n' 
         )

class IMM(object):
    def set_dhcp(self, target, user, passwd, verbose=False, node=None, args=None):
        run_single_command(target, user, passwd, dhcp_cmd, verbose)
        run_single_command(target, user, passwd, resetsp_cmd, verbose)
    
    def get_info(self, target, user, passwd, verbose=False, node=None, args=None):
        run_single_command(target, user, passwd, vpd_sys_cmd, verbose)
        run_single_command(target, user, passwd, vpd_imm_cmd, verbose)
        run_single_command(target, user, passwd, vpd_uefi_cmd, verbose)
        run_single_command(target, user, passwd, vpd_fw_cmd, verbose)
        run_single_command(target, user, passwd, vpd_comp_cmd, verbose)
        run_single_command(target, user, passwd, vpd_dsa_cmd, verbose)
        run_single_command(target, user, passwd, vpd_pcie_cmd, verbose)

    def reset_pw(self, target, user, passwd, verbose=False, node=None, args=None):
        pw = argv[0] if argv else "Th1nkAg!le"
        cmd = 'users -1 -p %s' % pw
        run_single_command(target, user, passwd, cmd, verbose)
        
    def reset(self, target, user, passwd, verbose=False, node=None, args=None):
        run_single_command(target, user, passwd, 'resetsp', verbose)

    def wipe(self, target, user, passwd, verbose=False, node=None, args=None):
        run_single_command(target, user, passwd, clearcfg_cmd, verbose)

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
            all_members = [x for x in dir(IMM) if not x.startswith('_')]
            all_members_str = ', '.join(all_members)
            print('Possible list of functions are %s' % all_members_str)
        else:
            assert False, "unhandled option"

    if not one_cmd and not one_func:
        # nothing to do
        sys.exit()

    if not addr:
        try:
            read_config()
        except Exception as e:
            print("Error: cannot retrieve configurations for imm")
    else:
        imm_hosts = re.split(r'[,;\s]\s*', addr.lstrip().rstrip())

    try:
        vprint(verbose, "Talk to imm using %s and %s" % (user, passwd))

        vprint(verbose, imm_hosts)
        for node in imm_hosts:
            ai = []
            try:
                for a in socket.getaddrinfo(node, None, socket.AF_INET6, socket.SOCK_STREAM, socket.IPPROTO_TCP):
                    ai.append(a[4][0])
            except:
                pass
            if not ai:
                ai.append(socket.gethostbyname(node))
            for target in ai:
                vprint(verbose, target)
                if one_func:
                    clist = one_func.split()
                    cmd = clist[0]
                    args = clist[1:]
                    method = getattr(imm, cmd)
                    print('Running %s on %s' % (cmd, node))
                    method(target, user, passwd, verbose, node, args)
                if one_cmd:
                    run_single_command(target, user, passwd, one_cmd, verbose)
    except Exception as e:
        raise
