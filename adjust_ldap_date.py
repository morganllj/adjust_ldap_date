#!/usr/bin/env python3
#

import getopt
import re
import sys
import yaml
from datetime import datetime, timezone, date
from dateutil.relativedelta import relativedelta

from ldap3 import Server, Connection, ALL, MODIFY_REPLACE

def print_usage():
    print ("usage: "+sys.argv[0]+" [-n] -c <config>.yml ")
    exit()

opts, args = getopt.getopt(sys.argv[1:], "nc:")

print_only = 0
config_file = None

for opt, arg in opts:
    if opt in ('-n'):
        print_only = 1
    elif opt in ('-c'):
        config_file = arg

if (config_file is None):
    print_usage()

# https://martin-thoma.com/configuration-files-in-python/open
with open (config_file, 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

server = Server(cfg["ldap"]["host"])
conn = Connection(server, cfg["ldap"]["binddn"], cfg["ldap"]["bindpass"], auto_bind=True)

rc = conn.search(cfg["ldap"]["basedn"], cfg["ldap"]["search"], attributes=['*'])

re_yr = re.compile(r'\d\d\d\d')
for e in conn.response:
    ldapdate = e["attributes"][cfg["ldap"]["dateattr"]]
    print (e["dn"], ldapdate, " ", end="")

    mo = re.search(re_yr, ldapdate)
    if mo:
        newyear = int(mo.group(0)) - 1;
        newdate = re.sub(r'^\d\d\d\d', str(newyear), ldapdate)
        print (newdate)
        if (not print_only):
            conn.modify(e["dn"],
                { cfg["ldap"]["dateattr"]: [(MODIFY_REPLACE, [newdate])] })
            if conn.result["result"]:
                print ("modify failed:", conn.result)
                sys.exit()
