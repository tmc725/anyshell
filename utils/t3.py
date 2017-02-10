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
from nimble.lci_utils import loop
from nimble.runcmd import RunCmd

imm_config = None
imm_config_file = '/lci/immconfig.json'
commands = []
imm_hosts = []
reset_cmd = 'users -1 -p PASSW0RD'

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

def mac_to_ipv6(mac):
    mac_list = mac.split(":")
    first_octet = format(int(mac_list[0], 16), '08b')
    #print first_octet
    #print first_octet[6]
    first_octet_list = list(first_octet)
    first_octet_list[6] = '1' if first_octet_list[6] == '0' else '0'
    first_octet = ''.join(first_octet_list)
    #print first_octet[6]
    ipv6 = "fe80::%s%s:%sff:fe%s:%s%s" % (format(int(first_octet, 2), '02x'), mac_list[1], mac_list[2], \
            mac_list[3], mac_list[4], mac_list[5])
    return ipv6

if __name__ == "__main__":

    for i in range(100):
        sleep(0.1)
        print 'Downloading File FooFile.txt [%d%%]\r'%i, 
        sys.stdout.flush()

    try:
        while (1): 
            loop()
            sleep(0.1)
    except KeyboardInterrupt:
        sys.exit()

    logging.basicConfig(level=logging.ERROR)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hm:", ["help", \
            "mac=" ])
    except getopt.GetoptError as err:
        print str(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    mac = None
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-m", "--mac"):
            mac = a
        else:
            assert False, "unhandled option"

    #try:
    #    read_config()
    #except Exception as e:
    #    print("Error: cannot retrieve configurations for imm")

    print mac_to_ipv6(mac)
