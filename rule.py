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

# --- static members ---

sourceFile = '/var/log/httpd/modsec_audit.log'
ip = None
ruleThreshold = 3
directoryThreshold = 5


def run():
    httpInfo = re.compile(r'--.+.+.+.+.+.+.+.+-B--')
    newRequest = re.compile(r'--.+.+.+.+.+.+.+.+-A--')
    newID = re.compile(r'.*\[id \"\d{1,6}\"\].*')
    ruleDict = dict()
    with open(str(sourceFile), 'r') as f:
        line = f.readline()
        fSize = os.fstat(f.fileno()).st_size
        while f.tell() != fSize:

            # --- Check prerequisites ---

            if newRequest.match(line) != None:
                line = f.readline()
                if re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"
                              , line)[0] == str(ip) or ip == None:

                    # --- Find HTTP Location ---

                    while httpInfo.match(line) == None:
                        line = f.readline()
                    line = f.readline()
                    location = line

                    # --- Find Matched Rule ID ---

                    while newID.match(line) == None:
                        line = f.readline()
                    id = re.findall(r'\[id \"\d{1,6}\"\]', line)[0]

                    # ---Put Rule together ---

                    if ruleDict.get(id.split('"')[1]) == None:
                        ruleDict.update({id.split('"'
                                )[1]: set([location.split(' '
                                )[1].split('?')[0]])})
                    else:

                        ruleDict.get(id.split('"'
                                )[1]).add(location.split(' '
                                )[1].split('?')[0])

            # --- Iterate ---

            line = f.readline()

    # --- Generate Rule List  ---

    # First sort out "SecRuleEngine Off" candidates

    itemdict = dict()
    for item in ruleDict.values():
        for location in item.copy():
            itemdict[location] = itemdict.setdefault(location, 0) + 1
            if itemdict[location] >= int(directoryThreshold):
                print '<LocationMatch "' + location \
                    + '''">
  SecRuleEngine Off
</LocationMatch>'''
                for item in ruleDict.copy():
                    ruleDict[item].discard(location)
                    if len(ruleDict[item]) == 0:
                        del ruleDict[item] #Delete empty rules

    # Now all other rules

    for item in ruleDict:
        locations = ruleDict.get(item)
        if len(locations) == 1:
            print '<LocationMatch "' + next(iter(locations)) + '">' \
                + '\n  ' + 'SecRuleRemoveById ' + item \
                + '\n</LocationMatch>'
        elif ruleThreshold > len(locations):
            sys.stdout.write('<LocationMatch "(')
            for location in locations:
                sys.stdout.write(location + '|')
            print ')">' + '\n  ' + 'SecRuleRemoveById ' + item \
                + '\n</LocationMatch>'
        else:
            print 'SecRuleRemoveById ' + item

def usage():
    print '''
This script is intended to build a whitelist for mod_security. This script takes all blocked request and builds an exception rule list.
You can overwrite the input file and specify a secure IP address. This is intended for systems already in production and might had faced real attacks.

Optional switches:

-f:\tOverwrite default input file (default /var/log/httpd/modsec_audit.log)
-s:\tOnly use events generated by this IP address
-t:\tSets threshold until creation of wildcard exclusion for rule (default 3)
-o:\tSets threshold until creation of wildcard exclusion for directory (default 5)

Example: ''' \
        + os.path.basename(__file__) \
        + '-f ./modsec_audit.log -s 192.168.20.2'


def main(argv):
    global sourceFile
    global ip
    global ruleThreshold
    global directoryThreshold
    try:
        (opts, args) = getopt.getopt(argv, 'f:s:t:o:h', ['inputFile=',
                'ip=', 'ruleThreshold=', 'directoryThreshold=', 'help'])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for (opt, arg) in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(2)
        if opt in ('-f', '--inputFile'):
            sourceFile = arg
        if opt in ('-s', '--ip'):
            ip = arg
        if opt in ('-t', '--Threshold'):
            ruleThreshold = arg
        if opt in ('-o', '--off'):
            directoryThreshold = arg

    run()


if __name__ == '__main__':
    main(sys.argv[1:])
