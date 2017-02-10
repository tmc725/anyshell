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
__doc__ = '''Script to run CMM cmds''' 

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

cmm_config = None
cmm_config_file = '/lci/utils/cmmconfig.json'
commands = []
cmm_hosts = []
#reset_cmd = 'resetsp'
reset_cmd = 'users -1 -p PASSW0RD'
resetsp_cmd = 'resetsp'
dhcp_cmd = 'ifconfig eth0 -c dhcp'
default_cmd = 'restoredefaults'
vpd_sys_cmd = 'vpd sys'
vpd_cmm_cmd = 'vpd cmm'
vpd_uefi_cmd = 'vpd uefi'
vpd_dsa_cmd = 'vpd dsa'
vpd_comp_cmd = 'vpd comp'
vpd_fw_cmd = 'vpd fw'
vpd_pcie_cmd = 'vpd pcie'
list_cmd = 'list -l %s'

def build_hosts():
    global cmm_hosts
    for n in cmm_config['nodes']:
        cmm_hosts.append(n)

def read_config():
    global cmm_config
    config_file = cmm_config_file
    try:
        with open(config_file) as cmm_json_file:
            cmm_config = json.load(cmm_json_file)
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
    vprint(verbose, 'INFO: Ready to send the following commands to CMM at %s:\n%s\n' % (target, cmd))
    try:
        conn = get_conn(target, user, passwd)
    except:
        try:
            conn = get_conn(target, user, 'Th1nkAg!le')
        except:
            raise

    (stdin, stdout, stderr) = conn.exec_command(cmd)
    resp = ''
    for line in stdout.readlines():
        resp += line
        vprint(verbose, line)
    error = ''
    for line in stderr.readlines():
        error += line
        if verbose:
            vprint(verbose, line)
    conn.close()
    return resp, error

def run_command(conn, cmd, verbose=True):
    if cmd:
        run_single_command(conn, cmd, verbose)

def usage():
    print('Usage: runcmmcmd.py [OPTIONS]\n'
          'A utility program to run a cmm command via SSH.\n'
          'Options:\n'
          '       -h --help \t\t\tprint this usage\n' 
          '       -u --user=<user_id>\t\tuser for the CMM\n'
          '       -p --passwd=<passwd>\tpassword for the CMM\n'
          '       -a --addr=<address>\t\tAddress for the CMM\n' 
          '       -f --func=<function>\t\tRun a function for the CMM\n'
          '       -c --cmd=<command>\t\tRun a command  for the CMM\n'
          '       -l --list\t\tList all possible functions\n' 
          '       -v --verbose\t\tVerbose mode\n' 
         )

class CMM(object):
    def set_dhcp(self, target, user, passwd, verbose=False, node=None, args=None):
        run_single_command(target, user, passwd, dhcp_cmd, verbose)
        run_single_command(target, user, passwd, resetsp_cmd, verbose)
    
    def get_info(self, target, user, passwd, verbose=False, node=None, args=None):
        run_single_command(target, user, passwd, vpd_sys_cmd, verbose)
        run_single_command(target, user, passwd, vpd_cmm_cmd, verbose)
        run_single_command(target, user, passwd, vpd_uefi_cmd, verbose)
        run_single_command(target, user, passwd, vpd_fw_cmd, verbose)
        run_single_command(target, user, passwd, vpd_comp_cmd, verbose)
        run_single_command(target, user, passwd, vpd_dsa_cmd, verbose)
        run_single_command(target, user, passwd, vpd_pcie_cmd, verbose)

    def dir(self, target, user, passwd, verbose=False, node=None, args=None):
        level = args[0] if args else 2
        (resp, error) = run_single_command(target, user, passwd, list_cmd%level, verbose)
        print resp
        return resp, error

    def get_blades(self, target, user, passwd, verbose=False, node=None, args=None):
        (inv, err) = self.dir(target, user, passwd, verbose, node, args)
        hosts=[]
        for line in inv.split('\n'):
            tokens = line.split()
            for t in tokens:
                if 'blade[' in t:
                    hosts.append(t)
        hosts_str = " ".join(hosts)
        print hosts_str
        return hosts, err

    def imm_addrs(self, target, user, passwd, verbose=False, node=None, args=None):
        (hosts, err) = self.get_blades(target, user, passwd, verbose, node, args)
        addrs  = []
        for blade in hosts:
            cmd = 'ifconfig -eth1 -T %s' % blade
            (resp, error) = run_single_command(target, user, passwd, cmd, verbose)
            for line in resp.split('\n'):
                tokens = line.split()
                if len(tokens) == 3 and 'Link-local' in tokens[0]:
                    addrs.append(tokens[2])        
        addrs_str = "\n".join(addrs)
        print addrs_str
        return addrs, err 

    def reset_imm_pw(self, target, user, passwd, verbose=False, node=None, args=None):
        pw = args[0] if args else 'PASSW0RD'
        (hosts, err) = self.get_blades(target, user, passwd, verbose, node, args)
        for blade in hosts:
            cmd = 'users -1 -p %s -T %s' % (pw, blade)
            (resp, error) = run_single_command(target, user, passwd, cmd, verbose)
        return hosts, err
        

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
    passwd = "Passw0rd!"
    addr = "172.20.10.1"
    one_cmd = None
    one_func = None
    cmm = CMM()
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
            all_members = [x for x in dir(CMM) if not x.startswith('_')]
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
            print("Error: cannot retrieve configurations for cmm")
    else:
        cmm_hosts = re.split(r'[,;\s]\s*', addr.lstrip().rstrip())

    try:
        vprint(verbose, "Talk to cmm using %s and %s" % (user, passwd))

        vprint(verbose, cmm_hosts)
        for node in cmm_hosts:
            ai = []
            try:
                for a in socket.getaddrinfo(node, None, socket.AF_INET6, socket.SOCK_STREAM, socket.IPPROTO_TCP):
                    ai.append(a[4][0])
            except Exception as e:
                print("WARNING: ipv6 resolution failed for %s due to %s" % (node, e))

            if not ai:
                ai.append(socket.gethostbyname(node))
            for target in ai:
                vprint(verbose, target)
                if one_func:
                    clist = one_func.split()
                    cmd = clist[0]
                    args = clist[1:]
                    method = getattr(cmm, cmd)
                    print('Running %s on %s' % (cmd, node))
                    method(target, user, passwd, verbose, node, args)
                if one_cmd:
                    run_single_command(target, user, passwd, one_cmd, verbose)
    except Exception as e:
        raise
