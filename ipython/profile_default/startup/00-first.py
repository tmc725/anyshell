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
__doc__ = '''First startup file'''

from IPython.terminal.prompts import Prompts, Token
import os
import logging
logger = logging.getLogger(__name__)
import sys
sys.path.append(os.environ["SHELLBASE"])
from datacenter.thinkagile.cx import CX

class MyPrompt(Prompts):

    def in_prompt_tokens(self, cli=None):  
        return [(Token.Prompt, 'Anyshell>')]

if __name__ == "__main__":
    
    logging.basicConfig(level=logging.ERROR)

    ip=get_ipython()
    ip.prompts=MyPrompt(ip)

    # create the datacenter and append the racks to it
    ip.user_ns['dc']= dc = []
    ip.user_ns['cx']= cx = CX()
    dc.append(cx)
    cx.initialize()
