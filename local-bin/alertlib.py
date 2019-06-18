# send alert to connect
# ( python 3 version )

import sys
import os
import json
import time
import requests
import alert_conf as conf
import syslog

hostname = os.uname()[1]

deployment_type_text = None

with open(conf.PROPS,'r') as props:
   for line in props:
     if line.find('idp.entityID')>=0:
       v = line.split('=')[1].strip()
       if v == 'urn:mace:incommon:washington.edu':
         deployment_type_text = 'prod'
       if v == 'urn:mace:incommon:washington.edu:dev':
         deployment_type_text = 'dev'
       if v == 'urn:mace:incommon:washington.edu:eval':
         deployment_type_text = 'eval'

def deployment_type():
    return deployment_type_text

def send_alert(component, urgency, title, message, kba=None, ci_name=None):

    if deployment_type() is None:
        return

    msg = {}
    if ci_name is None:
        msg['ci'] = {'name': os.uname()[1], 'organization': 'UW-IT'}
    else:
        msg['ci'] = {'name': ci_name, 'organization': 'UW-IT'}
    msg['component'] = {'name': component}
    msg['urgency'] = urgency
    if title is not None:
        msg['title'] = title
    msg['message'] = message
    if kba is not None:
        msg['message'] = message + '\nSee the Knowledge Base article.'
        msg['kba'] = {'number': kba}

    post_headers = {"Content-type": "application/json"}
    data = json.dumps(msg)
    url = conf.URL[deployment_type_text]
    # print ('URL: ' + url)

    resp = requests.post(url, headers=post_headers, data=data, cert=(conf.CERT_FILE, conf.KEY_FILE))
    # print (resp.status_code)
    return (resp.status_code, resp.text)

# if this module was run (not imported) send a test alert
if 'alertlib' not in sys.modules:
    if len(sys.argv) == 2 and sys.argv[1] == 'test':
        print ('test component: alertlib-test, level=3')
        st, dat = send_alert('alertlib-test', 3, 'This just a test', 'This just a test.  Please delete')
        print (st)
        print (dat)
    else:
        print ('usage: $ python %s test\n  sends test message to connect' % (sys.argv[0]))
