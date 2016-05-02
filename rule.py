#!/usr/bin/python
# -*- coding: utf-8 -*-

""" This script is intended to build a whitelist for mod_security. This script takes all blocked request and builds an exception rule list.  """

__author__ = 'Tobias Sturzenegger'
__copyright__ = 'Copyright (c) 2016 Tobias Sturzenegger'
__license__ = 'The MIT License (MIT)'
__version__ = '1.0.0'
__email__ = 'mail@tobiassturzenegger'

import sys
import re
import os
import getopt


def run(sourceFile=None, ip=None):
    if sourceFile == None:
        sourceFile = '/var/log/httpd/modsec_audit.log'
    httpInfo = re.compile(r'--.+.+.+.+.+.+.+.+-B--')
    newRequest = re.compile(r'--.+.+.+.+.+.+.+.+-A--')
    newID = re.compile(r'.*\[id \"\d{1,6}\"\].*')
    ruleSet = set()
    with open(str(sourceFile), 'r') as f:
        line = f.readline()
        fSize = os.fstat(f.fileno()).st_size
        while f.tell() != fSize:

            # --- Check prerequisites ---

            if newRequest.match(line) != None:
                line = f.readline()
                if re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"
                              , line)[0] == str(ip) or ip == None:

                    # --- Find HTTP Method ---

                    while httpInfo.match(line) == None:
                        line = f.readline()
                    line = f.readline()
                    method = line

                    # --- Find Matched Rule ID ---

                    while newID.match(line) == None:
                        line = f.readline()
                    id = re.findall(r'\[id \"\d{1,6}\"\]', line)[0]

                    # ---Put Rule together ---

                    ruleSet.add('<LocationMatch "' + method.split(' '
                                )[1].split('?')[0] + '">' + '\n  '
                                + 'SecRuleRemoveById ' + id.split('"'
                                )[1] + '\n</LocationMatch>')

            # --- Iterate ---

            line = f.readline()

    for item in ruleSet:
        print item


def usage():
    print '''
This script is intended to build a whitelist for mod_security. This script takes all blocked request and builds an exception rule list.
You can overwrite the input file and specify a secure IP address. This is intended for systems already in production and might had faced real attacks.

Optional switches:

-f:\tOverwrite default input file (default /var/log/httpd/modsec_audit.log)
-s:\tOnly use events generated by this IP address

Example: ''' \
        + os.path.basename(__file__) \
        + '-f ./modsec_audit.log -s 192.168.20.2'


def main(argv):
    inputFile = None
    ip = None
    try:
        (opts, args) = getopt.getopt(argv, 'f:s:h', ['inputFile=', 'ip='
                , 'help'])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for (opt, arg) in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(2)
        if opt in ('-f', '--inputFile'):
            inputFile = arg
        if opt in ('-s', '--ip'):
            ip = arg

    run(sourceFile=inputFile, ip=ip)


if __name__ == '__main__':
    main(sys.argv[1:])
