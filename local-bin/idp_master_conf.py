# config for the idp watcher

gets_mail = ['fox@uw.edu']

reply_to = 'iam-support@uw.edu'

graphite_node = 'services.idp.logins'
graphite_node_gws = 'services.idp.gws_ms'
udp_host = 'graphs-in.s.uw.edu'
udp_port = 2003

syslog_facility = 'LOG_LOCAL5'

host_down_msg = 'server-status: Down\n\nstatus-by: idp_master: waiting on apache/tomcat restart\n'
host_up_msg = 'server-status: Enabled\n\nstatus-by: idp_master\n'
apache_restart_failed = 'server-status: Down\n\nstatus-by: idp_master: apache restart failed\n'
tomcat_restart_failed = 'server-status: Down\n\nstatus-by: idp_master: tomcat restart failed\n'
host_status_file = '/www/host_status.txt'

tomcat_restarter = '/data/local/idp-3.4/local-bin/restart_tomcat.sh'

alert_component = 'idp-master'
alert_kba = 'KB0028717'
