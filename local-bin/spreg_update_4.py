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

# update the local (UW) metadata and filter resources as needed from the spregistry database
# version for v2 of the spreg database ( includes the access control flags )

import os
import time
import string
import shutil
import re
import socket

from optparse import OptionParser
import json
import jinja2

import subprocess

import psycopg2 as dbapi2
import datetime
import smtplib
from email.mime.text import MIMEText

import spreg_conf_4 as config
from alertlib import send_alert

# syslog shortcuts
import syslog
log = syslog.syslog
log_debug = syslog.LOG_DEBUG
log_info = syslog.LOG_INFO
log_err = syslog.LOG_ERR
log_alert = syslog.LOG_ALERT

j2_env = None

tmpdir = 'tmp'

needFilterScan = False

db = None


# modify time of a file
def mTime(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)


def openDb():
    global db
    db = dbapi2.connect(host=config.spreg_db['db_host'],
                        database=config.spreg_db['db_name'],
                        user=config.spreg_db['db_user'],
                        password=config.spreg_db['db_pass'])
    log(log_info, 'db is %s %s' % (config.spreg_db['db_host'], config.spreg_db['db_name']))
    


def countNewRows(group):
    global db
    c1 = db.cursor()
    mtime = None

    mtime = mTime(config.idp_base + group['dir'] + '/' + group['filename'])
    if 'id' in group:
        query = "select count(*) from %s where end_time is null and group_id='%s' and start_time > '%s';" % (group['type'], group['id'], mtime)
    else:
        query = "select count(*) from %s where end_time is null and start_time > '%s';" % (group['type'], mtime)
    c1.execute(query)
    row = c1.fetchone()
    c1.close()
    # print ('num new = ', row[0])
    return row[0]


# copy a database row unless we have canned test

def copyRow(type, row, id, f):
    global db

    print ('copyRow: %s %s %s' % (type, row, id))
    for hdr in config.xml_headers:
        if hdr.get('type') == type and hdr.get('row') == row and hdr.get('id') == id:
           print('using canned xml')
           f.write(hdr.get('xml') + '\n')
           return

    print('using db xml')
    c1 = db.cursor()
    c1.execute("select %s from %s where status=1 and id='%s'" % (row, type + '_group', id))
    rows = c1.fetchall()
    for row in rows:
        f.write(row[0] + '\n')
    return


# copy a filter entry, fixing as needed for 3.x -> 4.x upgrade

def copyData(table, id, f):
    # print ('table=%s, id=%s, f=%s' % (table, id, f))
    global db
    num = 0
    c1 = db.cursor()
    c1.execute("select xml, entity_id from %s where status=1 and group_id='%s'" % (table, id))
    rows = c1.fetchall()
    for row in rows:
        out = row[0]
        if table == 'filter':
            out = out.replace('basic:Rule','Rule').replace('basic:OR','OR').replace('basic:ANY','ANY')\
                        .replace('basic:AttributeRequesterString','Requester').replace('basic:AttributeRequesterRegex','RequesterRegex')\
                        .replace('basic:AttributeValueString','Value').replace('basic:AttributeValueRegex','ValueRegex')
        f.write(out + '\n')
        num += 1
    return num


# verify a saml xml file
def verifySaml(file):
    ret = subprocess.call([config.saml_validator, file])

    if ret != 0:
        log(log_err, 'saml document %s is not valid' % (file))
        return False
    return True


# update a conf file
def updateIdpConfig(group):
    id = group['id']
    filename = group['filename']
    file_path = config.idp_base + '/' + group['dir'] + '/' + filename
    tmp_path = config.tmp_dir + filename + '.' + str(os.getpid())

    f = open(tmp_path, 'w')
    copyRow(group['type'], 'header_xml', id, f)
    num_row = copyData(group['type'], id, f)
    copyRow(group['type'], 'footer_xml', id, f)
    f.close()

    # verify the new file

    if num_row < group['min_rows']:
        log(log_err, '%s document %s is too short: %d<%d' % (group['type'], tmp_path, num_row, group['min_rows']))
        return False

    if not verifySaml(tmp_path):
        return False

    # is ok, replace original

    sav = config.archive_dir + filename + time.strftime('%d%H%M%S')
    shutil.copy2(file_path, sav)
    os.rename(tmp_path, file_path)

    log(log_info, "Created new %s file %s" % (group['type'], filename))
    needFilterScan = True
    return True


def findGroup(type, id):
    for g in config.idp_conf_files['groups']:
        if g['type'] == type:
            if 'id' not in g or g['id'] == id:
                return g
    return None


def updateFiles(group):
    ret = updateIdpConfig(group)
    if not ret:
        print ('update files error: ' + group['type'])
        print (group)
        send_alert(config.alert_component, 3, 'IdP update of spreg data failed',
           'SPReg update: new data from spreg is not valid.  New changes from spreg will not propagate.',
           kba=config.alert_kba, ci_name=config.alert_ci_name)

# -------- access control update ------------------

warning_msg = '<!-- DON\'T EDIT!  This file created by, and overwritten by, spreg_update_2.py -->'

def updateAccess(group):
    global db
    num = 0

    auth_sps = {
        'authz': set([]),
        'mfa': set([]),
        'mfa_authz': set([])
    }

    c1 = db.cursor()
    c1.execute('select entity_id,conditional,auto_2fa from access_control where end_time is null order by entity_id')
    rows = c1.fetchall()
    for row in rows:
        if row[1]:
            auth_sps['authz'].add(row[0])
        if row[2]:
            auth_sps['mfa'].add(row[0])
        num += 1

    # output the specials bean
    auth_sps['warning'] = warning_msg
    dest = config.idp_base + group['dir'] + '/' + group['filename']
    template = j2_env.get_template(group['filename'] + '.j2')
    tout = config.tmp_dir + group['filename']
    with open(tout, 'w') as f:
        f.write(template.render(info=auth_sps))
    arc = config.archive_dir + group['filename'] + '.' + time.strftime('%s')
    shutil.copy2(dest, arc)
    os.rename(tout, dest)
    log(log_info, "Created new " + dest)

    # output the autotoken list
    dest = config.idp_base + group['dir'] + '/authn/' + config.autotoken_filename
    tout = config.tmp_dir + config.autotoken_filename
    with open(tout, 'w') as f:
        f.write('# list of SPs needing auto 2fa\n# created by spreg_update_4.py\n')
        f.write('urn:amazon:webservices\n')
        f.write('http://www.workday.com\n')
        for l in auth_sps['mfa']:
            f.write(l + '\n')
    arc = config.archive_dir + config.autotoken_filename + '.' + time.strftime('%s')
    shutil.copy2(dest, arc)
    os.rename(tout, dest)
    log(log_info, "Created new " + dest)


# ---------
#
# Main
#
# ---------

parser = OptionParser()
parser.add_option('-v', '--verbose', action='store_true', dest='verbose', help='?')
# parser.add_option('-c', '--conf', action='store', type='string', dest='config', help='config file')
parser.add_option('-f', '--force', action='store_true', dest='force', help='force update')
parser.add_option('-t', '--type', action='store', type='string', dest='type', help='type to update (filter|metadata)')
parser.add_option('-g', '--group', action='store', type='string', dest='group', help='group to update')
options, args = parser.parse_args()
# config_source = 'spreg_conf_2'
# if options.config is not None:
#     config_source = options.config
#     print ('using config=' + config_source)
# config = __import__(config_source)

# setup logging
logname = 'spreg_update'
if hasattr(config, 'log_name'):
    logname = config.log_name

log_facility = syslog.LOG_SYSLOG
if hasattr(config, 'syslog_facility'):
    logf = config. syslog_facility
    if re.match(r'LOG_LOCAL[0-7]', logf):
        log_facility = eval('syslog.'+logf)

option = syslog.LOG_PID
if options.verbose:
    option |= syslog.LOG_PERROR
syslog.openlog(logname, option, log_facility)
log(log_info, "spreg update starting.")

openDb()

j2_env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True, loader=jinja2.FileSystemLoader(config.template_dir))

if options.group is not None or options.type is not None:
    log(log_info, "just for'%s' in '%s'" % (options.group, options.type))
    group = findGroup(options.type, options.group)
    if group is not None:
        if options.force or countNewRows(group) > 0:
            if group['type'] == 'access_control':
                updateAccess(group)
            else:
                updateFiles(group)
        else:
            log(log_info, 'no changes')
    else:
        print (options.group + ' not found')

else:

    for group in config.idp_conf_files['groups']:
        log(log_info, "checking '%s %s'" % (group['type'], group['id'] if 'id' in group else ''))
        if options.force or countNewRows(group) > 0:
            if group['type'] == 'access_control':
                updateAccess(group)
            else:
                updateFiles(group)

    # send keepalive every time script is run--dash alert will happen

log(log_info, "completed.")
