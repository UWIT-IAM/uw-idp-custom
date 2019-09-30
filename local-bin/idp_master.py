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

#
# idp monitor and controller - idp 3.4
#

from urllib.request import urlopen

import threading
from subprocess import call
from subprocess import check_output
from subprocess import Popen
from subprocess import PIPE

import json
import ssl

import sys
import os
import string
import time
import re
import random
import socket
import smtplib
from smtplib import SMTPException
from email.mime.text import MIMEText

import idp_master_conf as config
from alertlib import send_alert

import syslog
log = syslog.syslog
log_debug = syslog.LOG_DEBUG
log_info = syslog.LOG_INFO
log_err = syslog.LOG_ERR
log_alert = syslog.LOG_ALERT

# timeouts
connectTimeout = 20.0
readTimeout = 30.0


IDLE_DELAY_SEC = 2

# alert messages and etc
myHostName = socket.gethostname()
alertMsg1 = 'The IdP experienced a fatal error and is restarting.'
alertMsg2 = 'The IdP successfully restarted.'


maxFixes = 5
numFixes = 0
init_d = 0

# counters for Graphite export
num_audit = 0  # num audits since last report
min_audit = 0  # epoch minute of last report
gws_msec = 0   # total wait for gws get
num_gws = 0    # number gws gets
num_logout = 0 # number logouts

# idp states


class IdpState:
    UNKNOWN, STARTING, UP, STOPPING, RESTARTING = range(5)

idp_state = IdpState.UNKNOWN


def setState(s):
    global idp_state
    log(log_info, 'state now: %d' % s)
    idp_state = s

#
# activity mailer
#


def sendMail(to, sub, msg=None):

    if msg is None:
        msg = sub
    try:
        mailhost = 'appsubmit.cac.washington.edu'
        s = smtplib.SMTP(mailhost)

        sender = 'iamidp@' + myHostName
        message = MIMEText(msg)
        message['Subject'] = sub
        message['From'] = sender
        message['Reply-To'] = config.reply_to
        message['To'] = ','.join(to)

        s.sendmail(sender, to, message.as_string())
        log(log_info, "Successfully sent email")
    except SMTPException:
        log(log_info, "Error: unable to send email")


# set this host down - will need manual restart - incident has been requested
def setClusterStatus(status_message):
    try:
        with open(config.host_status_file, 'w') as status_file:
            status_file.write(status_message)
    except OSError:
        log(log_err, 'cluster remove failed')

# are we in the cluster?
def inTheCluster():
    r = call('cat /www/host_status.txt|grep Enabled>/dev/null', shell=True)
    return r == 0

# is this a tomcat restart?
def tomcatStarting():
    r = call('cat /www/host_status.txt|grep Starting>/dev/null', shell=True)
    return r == 0

#
# get file inode
#
def getFileId(st):
    return '%x-%x' % (st.st_dev, st.st_ino)

#
# log file watcher
#
# watches = [{string, action},...]

# timeouts
connectTimeout = 20.0
readTimeout = 30.0


class LogWatcher(threading.Thread):

    def __init__(self, filename, watches):
        threading.Thread.__init__(self)
        self.filename = filename
        self.watches = watches

    def run(self):
        log(log_info, 'logwatcher watching ' + self.filename)
        file = open(self.filename, encoding='utf-8', mode='r')
        # get to the end
        fstat = os.stat(self.filename)
        fend = fstat[6]
        file.seek(fend)

        emptyCount = 0
        while True:
            p = file.tell()
            try:
                line = file.readline()
            except UnicodeDecodeError:
                log(log_info, 'caught a decode error')
                continue

            if not line:
                emptyCount += 1
                if emptyCount > 5:
                    fs = os.stat(self.filename)
                    if not (fs.st_dev == fstat.st_dev and fs.st_ino == fstat.st_ino):
                        log(log_info, 'logwatcher reopening ' + self.filename)
                        file.close()
                        file = open(self.filename, 'r')
                        fstat = fs
                    else:
                        emptyCount = 0
                else:
                    time.sleep(2)
                    file.seek(p)
            else:
                for pat, action in self.watches:
                    if re.search(pat, line) is not None:
                        if action(line):
                            # get to the new end
                            fstat = os.stat(self.filename)
                            fend = fstat[6]
                            file.seek(fend)


class GraphiteReporter(threading.Thread):

    udp_host = config.udp_host
    udp_port = config.udp_port
    udp_socket = None
    myHostId = myHostName.replace('.', '_')

    def __init__(self):
        threading.Thread.__init__(self)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def run(self):
        global num_audit
        global num_gws
        global gws_msec
        log(log_info, 'graphite reporter starting')

        num_audit = 0
        while True:
            time.sleep(60)
            log(log_debug, 'sending %d logins to graphite' % num_audit)
            ave_gws = gws_msec/num_gws if num_gws > 0 else 0
            log(log_debug, '%d gws gets,  %d ave msec' % (num_gws, ave_gws))
            msg = '%s.%s %d %d\n' % (config.graphite_node, self.myHostId, num_audit, int(time.time()))
            gmsg = '%s.%s %d %d\n' % (config.graphite_node_gws, self.myHostId, ave_gws, int(time.time()))
            try:
                self.udp_socket.sendto(msg.encode(), (self.udp_host, self.udp_port))
                self.udp_socket.sendto(gmsg.encode(), (self.udp_host, self.udp_port))
            except socket.error as err:
                log(log_alert, 'graphite reporter socket error: %s' % err)
            num_audit = 0
            num_gws = 0
            gws_msec = 0


#
# check status of apache/tomcat/idp
#

class ServiceWatcher(threading.Thread):

    def run(self):
        global idp_state, init_d
        log(log_info, 'service watcher starting')

        while True:
            # skip if system is out of cluster
            if not inTheCluster():
                time.sleep(60)
                continue

            # check apache
            r = check_output('ps uww -C httpd  --no-heading | wc -l', shell=True)
            if int(r) == 0:
                log(log_alert, "No apache process!  Attempting start")
                r = call('/data/local/bin/ansible_command apache restart', shell=True)
                if not r == 0:
                    log(log_alert, "Could not start apache! rc=%d" % r)
                    setClusterStatus(config.apache_restart_failed);
                    send_alert(config.alert_component, 2, 'Unable to start Apache',
                       'The idp master on %s was unable to restart apache.  The system has been taken out of the cluster.' % (os.uname()[1]),
                       kba=config.alert_kba)
                else:
                    log(log_info, "Apache restarted")
                sendMail(config.gets_mail, 'IdP %s restarted apache, status %d' % (myHostName, r), alertMsg1)

            # check tomcat
            r = check_output('ps uww -C java --no-heading | grep tomcat | wc -l', shell=True)
            if int(r) == 0:
                log(log_alert, "No tomcat process!  Attempting start")
                r = call(['/usr/local/tomcat/bin/startup.sh'])
                if not r == 0:
                    log(log_alert, "Could not restart tomcat! rc=%d" % r)
                    setClusterStatus(config.tomcat_restart_failed);
                    send_alert(config.alert_component, 2, 'Unable to start Tomcat',
                       'The idp master on %s was unable to restart tomcat.  The system has been taken out of the cluster.' % (os.uname()[1]),
                       kba=config.alert_kba)
                else:
                    log(log_info, "Tomcat restarted")
                sendMail(config.gets_mail, 'IdP %s restarted tomcat, status %d' % (myHostName, r), alertMsg1)
                time.sleep(10)

            # check idp
            try:
                res = urlopen('http://localhost/idp/status')
                # log(log_debug,'idp test')
                if res.getcode() == 200:
                    # log(log_debug,'idp is up: state=%d' % idp_state)
                    if idp_state == IdpState.UNKNOWN or idp_state == IdpState.RESTARTING:
                        setState(IdpState.UP)
                        log(log_info, 'IdP seems to be up')
                        with open(config.host_status_file, 'w') as status_file:
                            status_file.write(config.host_up_msg)
                        init_d = 1
                else:
                    log(log_err, 'got error from idp status')
                    idp_state = IdpState.UNKNOWN
                res.close()
            except IOError:
                log(log_alert, 'could not get idp status!')
                idp_state = IdpState.UNKNOWN

            time.sleep(60)


#
#
# log handlers
#

def match_gws(line):
    global gws_msec
    global num_gws
    try:
        gws_msec += int(re.split(' |/', line[line.find('GWS attr time')+15:])[1])
        num_gws += 1
    except ValueError:
        pass
    return False

def match_audit(line):
    global num_audit
    num_audit += 1
    return False

def match_logout(line):
    global num_logout
    num_logout += 1
    return False


# error detected that can be fixed with restart
def match_error_fatal(line):
    log(log_err, 'got a fatal error: ' + line)
    sendAlertAndRestart('line')
    return True

# error detected that needs some dependency to be fixed
def match_error_personreg(line):
    log(log_err, 'got a personreg error: ' + line)
    send_alert(config.alert_component, 2, 'Unable to restart the IdP service',
        'The idp master on %s was unable to restart the idp service.  The system has been taken out of the cluster.' % (os.uname()[1]),
         kba=config.alert_kba)
    sendAlertAndRestart('line')
    return True


#
# state controllers
#
def _wait_for_idp():
    
    global init_d
    global idp_state
    init_d = 0
    count = 0
    log(log_info, 'waiting for idp to start')
    while init_d == 0:
        res = urlopen('http://localhost/idp/status')
        if res.getcode() == 200:
            log(log_info,'idp is up: state=%d' % idp_state)
            setState(IdpState.UP)
            with open(config.host_status_file, 'w') as status_file:
                status_file.write(config.host_up_msg)
                init_d = 2
        else:
            if res.getcode() != 503:
                log(log_debug, 'got %d from idp status' % (res.getcode()))
            time.sleep (10);
        res.close()
        count += 1
        if count == 60:
            log(log_err, 'IdP did not start! (5 minutes wait)')
        
def restartTomcat():
    global idp_state
    try:
        log(log_info, 'restarting tomcat')
        r = call([config.tomcat_restarter])
        if r == 0:
            log(log_info, 'tomcat restarted')
            idp_state = IdpState.RESTARTING
            _wait_for_idp()  # watcher thread will see this
            sendMail(config.gets_mail, 'IdP %s restarted' % myHostName)
        else:
            log(log_alert, 'restart of tomcat failed (script)!')
    except OSError:
        log(log_alert, 'restart of tomcat failed (oserror)!')


def sendAlertAndRestart(msg):
    global idp_state
    global numFixes, maxFixes

    if not inTheCluster():
        return

    if idp_state == IdpState.STOPPING:
        log(log_info, 'extra alert while stopping')
    elif idp_state == IdpState.STARTING or idp_state == IdpState.RESTARTING:
        log(log_err, 'alert while starting!')
    else:
        log(log_err, 'alert received, attempting restart')
        sendMail(config.gets_mail, 'IdP %s restarting' % myHostName)
        try:
            with open(config.host_status_file, 'w') as status_file:
                status_file.write(config.host_down_msg)
            idp_state = IdpState.STOPPING
            restartTomcat()
            numFixes += 1
            if numFixes >= maxFixes:
                log(log_err, 'too many fixes, alerting connect')
                send_alert(config.alert_component, 2, 'Unable to restart the IdP service',
                   'The idp master on %s was unable to restart the idp service.  The system has been taken out of the cluster.' % (os.uname()[1]),
                       kba=config.alert_kba)
        except OSError:
            log(log_err, 'cluster remove failed')


#
# main - initialize, watch, fix
#

logname = 'idp_master'
log_facility = eval('syslog.' + config.syslog_facility)
syslog.openlog(logname, syslog.LOG_PID, log_facility)

log(log_info, 'IdP master starting')

# if tomcat starting, wait for idp up
time.sleep(5)
if tomcatStarting():
    _wait_for_idp();

serviceWatcherThread = ServiceWatcher()
serviceWatcherThread.start()

graphiteReporterThread = GraphiteReporter()
graphiteReporterThread.start()

logWatcherThread = LogWatcher('/logs/idp/process.log', [
     (r'ERROR.*Too many open files', match_error_fatal),
     (r'NestedServletException.*java.lang.OutOfMemoryError', match_error_fatal),
     (r'GWS attr time:', match_gws),
     (r'Shibboleth-Audit.SSO', match_audit)
  ])

##      (r'Shibboleth-Audit.Logout', match_logout)

logWatcherThread.start()
log(log_info, 'idp master watching')
logWatcherThread.join()
graphiteReporterThread.join()
serviceWatcherThread.join()
log(log_info, 'idp master exiting')

# no ldap: (r'resolver.ResolutionException.*personreg.*Unable to execute LDAP search', match_error_personreg)
# no pws: (r'resolver.ResolutionException.*
# no gws: (r'resolver.ResolutionException.*
