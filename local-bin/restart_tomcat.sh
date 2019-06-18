#!/bin/bash

# forcefully stop tomcat and restart

# if tomcat gets stuck certain ways, e.g. no heap space, the standard scripts don't stop it

tcpid=0
function get_tomcat_pid {
  tcpid="`ps auxw|grep 'org.apache.catalina.startup.Bootstrap'|grep -vw grep|awk '{print $2}'`"
}
  
function wait_for_gone {
  i=0
  while ((i<4)) 
  do
    tcpid=0
    get_tomcat_pid
    (( tcpid == 0 )) && break
    sleep 1
    (( i += 1 ))
  done
}

get_tomcat_pid
(( tcpid > 0 )) && {
  echo "found process: $tcpid"
  kill -9  $tcpid
}

# maybe try harder
# wait_for_gone
# (( tcpid > 0 )) && {
  # echo "found process still: $tcpid"
  # kill -9 $tcpid
# }

wait_for_gone
(( tcpid > 0 )) && {
  echo "could not kill: $tcpid"
}

# restart

/usr/local/tomcat/bin/startup.sh

exit 0


