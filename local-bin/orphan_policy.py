#  ========================================================================
#  Copyright (c) 2014 The University of Washington
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#  ========================================================================
#

# scans metadata and filter files for orphaned policies.  No SP in metadata

import os
import time
import string
import shutil
import copy
import re

from lxml import etree
import psycopg2 as dbapi2
import smtplib
from email.mime.text import MIMEText

from optparse import OptionParser
import json
import jinja2

import syslog
log = syslog.syslog
log_debug = syslog.LOG_DEBUG
log_info = syslog.LOG_INFO
log_err = syslog.LOG_ERR
log_alert = syslog.LOG_ALERT

j2_env = None

db = None
config = None

def _print(str):
    pass

# some namespaces we need
filter_ns = {
   'beans': 'http://www.springframework.org/schema/beans',
   'afp': 'urn:mace:shibboleth:2.0:afp',
   'resolver': 'urn:mace:shibboleth:2.0:resolver',
}


known_rps = set()
policy_rps = set()


# parse a metadata file, adding sp entities to our list

def parseMetadata(file):

    global known_rps
    ns = {'md': 'urn:oasis:names:tc:SAML:2.0:metadata'}

    doc = etree.parse(file)
    eds_root = doc.getroot()
    eds = eds_root.findall('md:EntityDescriptor', ns)
    for ed in eds:
        if ed.find('md:SPSSODescriptor', ns) is not None:
            known_rps.add(ed.get('entityID'))


# parse a filter file, adding sp requestors our list

def parseFilter(file):

    global policy_rps

    doc = etree.parse(file)

    afps = doc.getroot()
    for afp in afps:
        prr = afp.find('afp:PolicyRequirementRule', filter_ns)
        policy_rps.add(prr.get('value'))
         



def sendNotice(sub):
    msg = MIMEText(sub)
    msg['Subject'] = sub
    msg['From'] = config['mail_from']
    msg['To'] = config['mail_to']
    s = smtplib.SMTP(config['mail_smtp'])
    s.sendmail(msg['From'], [msg['To']], msg.as_string())
    s.quit


# ---------
#
# Main
#
# ----------


parseMetadata('/data/local/idp/metadata/InCommon-metadata.xml')
parseMetadata('/data/local/idp/metadata/UW-rp-metadata.xml')

print '{} metadata rps'.format(len(known_rps))

parseFilter('/data/local/idp/conf/rp-filter.xml')

print '{} filter rps'.format(len(policy_rps))

no = 0
for filter in policy_rps:
    if not filter in known_rps:
        print 'policy for {} is orphan'.format(filter)
        no += 1
print '{} orphan policies'.format(no)
