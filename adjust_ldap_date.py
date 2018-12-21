#!/usr/bin/env python3
#

import getopt
import re
import sys
import yaml
from datetime import datetime, timezone, date
from dateutil.relativedelta import relativedelta

#from ldap3 import Server, Connection, ALL
from ldap3 import ObjectDef, AttrDef, Reader, Writer, Entry, Attribute, OperationalAttribute, Server, Connection

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

person = ObjectDef(['top','person','organizationalPerson', 'inetOrgPerson','posixAccount','sdpAssociate','sdpEmployee','sdpZimbraPerson','shadowAccount','inetUser','ntUser','sambaSamAccount', 'sdprole', 'sdpServiceAccount'], conn)
query = 'cfg["ldap"]["search"]'
reader = Reader(conn, person, cfg["ldap"]["basedn"], cfg["ldap"]["search"]);
reader.search(attributes=['sdpAccountExpirationDate'])

re_yr = re.compile(r'\d\d\d\d')
for r in conn.entries:
    d = r.entry_attributes_as_dict;
    print (r.entry_dn, " ", end="")

    l = d["sdpAccountExpirationDate"];
    ldapdate = l[0]
    print (ldapdate, " ", end="")
    mo = re.search(re_yr, ldapdate)
    if mo:
        newyear = int(mo.group(0)) - 1;
        newdate = re.sub(r'^\d\d\d\d', str(newyear), ldapdate)
        print (newdate)

        i=0
        writer = Writer.from_cursor(reader);
        for w in writer:
            if w.entry_dn == r.entry_dn:
                writer[i].sdpAccountExpirationDate = newdate
                if (not print_only):
                    print (writer[i].entry_changes)
                    writer.commit()
                    if (writer[i].entry_changes):
                        print ("error modifying!")
                        sys.exit()
            i+=1
    else:
        print ("skipping!")

