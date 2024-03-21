#  ========================================================================
#  Copyright (c) 2020 The University of Washington
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
# also issues reports 

import os
import sys
import re
import time

import psycopg2
import datetime
import json
import jinja2

import spreg_conf as config

# syslog shortcuts
import syslog
log = syslog.syslog
log_debug = syslog.LOG_DEBUG
log_info = syslog.LOG_INFO
log_err = syslog.LOG_ERR
log_alert = syslog.LOG_ALERT

db = None

def openDb():
    global db
    db = psycopg2.connect(host=config.spreg_db['db_host'],
                        database=config.spreg_db['db_name'],
                        user=config.spreg_db['db_user'],
                        password=config.spreg_db['db_pass'])
    log(log_info, 'db is %s %s' % (config.spreg_db['db_host'], config.spreg_db['db_name']))
    

# setup logging
logname = 'netid_exception'
log_facility = syslog.LOG_SYSLOG
option = syslog.LOG_PID
option |= syslog.LOG_PERROR
syslog.openlog(logname, option, log_facility)
log(log_info, "netid_exception invoked.")

def _bad(msg):
    log(log_info, msg)
    print(msg)
    sys.exit(1)
    
# send json report
def __report(type):
    print('**** status ***')
    entries = []
    try:
        openDb()
        cursor = db.cursor()
        query = "select netid,start_time,updated_by from netid_exceptions where type='%s'" % (type)
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        for row in rows:
            entries.append({'netid': row[0], 'start_time': str(row[1]), 'updated_by': row[2]})
    except Exception as e:
        log(log_err, "DB select failed: " + str(e))
        print("DB select failed: " + str(e))
        sys.exit(2)

    return json.dumps({'netid-exception': 'disuser' if type=='ciso' else 'forget', 'entries': entries})

# simpler all-type report
def _report(type):
    report = {'meta': {
            'resource': 'IdP netid excptions',
            'timestamp': int(time.time()),
            'host': os.uname()[1]},
        'data': {}
    }
    report['data']['auto'] = []   
    report['data']['no2fa'] = []   
    report['data']['disuser'] = []   
    report['data']['reuser'] = []   
    report['data']['zlink'] = []   

    with open(config.dynamic_path, 'r') as f:
        lines = f.readlines()
    for line in [x.strip() for x in lines]:
        items = line.split('|')
        if len(items)<2:
            continue
        if items[0] == 'auto' or items[0] == 'no2fa':
            report['data'][items[0]].append({"sp": items[1]})
        elif items[0] == 'disuser' or items[0] == 'reuser':
            report['data'][items[0]].append({"netid": items[1], "time": items[2]})
        elif items[0] == 'zlink':
            report['data'][items[0]].append({"sp": items[1], "url": items[2]})
        else:
            pass

    if type == 'html':
        j2 = jinja2.Environment(trim_blocks=True, lstrip_blocks=True,
                                loader=jinja2.FileSystemLoader(config.idp_base + '/local-bin/'))
        template = j2.get_template('netid_exceptions_html.j2')
        return template.render(items=report['data'])
    return json.dumps(report)

    
# args: type netid remote_user remote_addr
if len(sys.argv)<3:
    _bad('bad invoke: args < 3')

method = sys.argv[1]
type=''
if sys.argv[2] == 'disuser':
    type = 'disuser'
elif sys.argv[2] == 'reuser':
    type = 'reuser'
elif sys.argv[2] == 'json':
    type = 'json'
elif sys.argv[2] == 'html':
    type = 'html'
else:
    _bad('invalid type')

if method=='GET':
    print(_report(type))
    sys.exit(0)
 
if len(sys.argv)<5:
    _bad('bad invoke: args < 4')

if  method!='PUT':
    _bad('bad method: ' + method)

netid = sys.argv[3]
if not bool(re.match('^[a-z][a-z0-9_-]+$', netid)):
   _bad('bad netid: ' + netid)

remote_user = sys.argv[4]
if not bool(re.match('^[a-z0-9_\.-]+$', remote_user)):
   _bad('bad remote_user: ' +remote_user)

remote_addr = sys.argv[5]
if not bool(re.match('^[a-z0-9_\.-]+$', remote_addr)):
   _bad('bad remote_addr: ' + remote_addr)

log(log_info, 'method=%s, type=%s, netid=%s' % (method, type, netid))

try:
    openDb()
    cursor = db.cursor()
    # we want only one entry per type/netid
    query = "delete from netid_exceptions where type='%s' and netid='%s'" % (type, netid)
    cursor.execute(query)
    # reuser deletes the preceding disuser
    if type=='reuser':
        query = "delete from netid_exceptions where type='disuser' and netid='%s'" % (netid)
        cursor.execute(query)
    # disuser deletes the preceding reuser
    if type=='disuser':
        query = "delete from netid_exceptions where type='reuser' and netid='%s'" % (netid)
        cursor.execute(query)
    query = "insert into netid_exceptions values ('%s','%s',now(),'%s@%s')" % (type, netid, remote_user, remote_addr)
    cursor.execute(query)
    db.commit()
    cursor.close()
    db.close()
    log(log_info, "completed.")
except Exception as e:
    log(log_err, "DB update failed: " + str(e))
    print("DB update failed: " + str(e))
    sys.exit(2)
