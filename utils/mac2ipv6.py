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
sys.path.append("/lci")
from nimble.lci_utils import warn_not_exit
from nimble.runcmd import RunCmd

imm_config = None
imm_config_file = '/lci/immconfig.json'
commands = []
imm_hosts = []
reset_cmd = 'users -1 -p PASSW0RD'

def usage():
    print('Usage: mac2ipv6.py [OPTIONS]\n'
          'A utility program to convert mac to/from ipv6.\n'
          'Options:\n'
          '       -h --help \t\t\tprint this usage\n' 
          '       -m --mac=<address>\t\tconvert this mac to ipv6 link local\n' 
          '       -i --ipv6=<address>\t\tconvert this ipv6 to mac\n' ,
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

def ipv62mac(ipv6):
    # remove subnet info if given
    subnetIndex = ipv6.find("/")
    if subnetIndex != -1:
        ipv6 = ipv6[:subnetIndex]

    ipv6Parts = ipv6.split(":")
    macParts = []
    for ipv6Part in ipv6Parts[-4:]:
        while len(ipv6Part) < 4:
            ipv6Part = "0" + ipv6Part
        macParts.append(ipv6Part[:2])
        macParts.append(ipv6Part[-2:])

    # modify parts to match MAC value
    macParts[0] = "%02x" % (int(macParts[0], 16) ^ 2)
    del macParts[4]
    del macParts[3]

    return ":".join(macParts)

if __name__ == "__main__":

    logging.basicConfig(level=logging.ERROR)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hm:i:", ["help", \
            "mac=" ])
    except getopt.GetoptError as err:
        print str(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    mac = None
    ipv6 = None
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-m", "--mac"):
            mac = a
        elif o in ("-i", "--ipv6"):
            ipv6 = a
        else:
            assert False, "unhandled option"

    #try:
    #    read_config()
    #except Exception as e:
    #    print("Error: cannot retrieve configurations for imm")

    if mac: 
        print mac_to_ipv6(mac)
    if ipv6:
        print ipv62mac(ipv6)

