#!/bin/bash

# simple script to test responsiveness of dependencies 
# PDS, (PWS), GWS

host=`hostname -s`

gws_service=groups.uw.edu
pws_service=ws.admin.washington.edu

log=test_dependencies.log
((start_sec = `date +%s`))

wd="`dirname \"$0\"`"
cd $wd

## . /data/local/iam-test/testlib.sh
## . /data/local/gws-provisioning/bin/gws_lib.sh
certdir=/data/local/idp/credentials

gws_hosts="iam21 iam22 iam23 iam26"
pds_hosts="seneca21 seneca22 seneca23"
pds_hosts="seneca21 seneca22 seneca23 seneca31 seneca32 seneca33"
pws_hosts="it-ws1 it-ws2 it-ws3 it-ws4"

## [[ "$1" == "" ]] || hosts="$1"

# notifier
function tell_someone {
   echo "GWS failed: $1" | mailto 2064198630@txt.att.net -s "GWS failure"
}

# test if host is loadr idled
function is_it_enabled {
  host="$1"
  load="`/usr/local/bin/ding dnsload11 loadm su1 | egrep \" ${host}\"|awk '{print $1}'`"
  [[ -z $load ]] && return 2  # dead
  [[ $load == *"M"* ]] && return 1
  (( load < 900000 )) && return 0   # up
  return 1
}

# curl --cert xxx --key xxx --cacert xxx --resolve 'groups.uw.edu:128.208.178.148' https://groups.uw.edu/group_sws/v3/group/u_fox/member

esec=0
function is_gws_up {
   host=$1
   sec="`echo -n $(($(date +%s%N)/1000000))`"
   n="`/usr/bin/time -f %e /usr/local/curl/bin/curl \
       --resolve ${gws_service}:${host} \
       --cert ${certdir}/gws.cac-uw.crt \
       --key ${certdir}/gws.cac-uw.key \
       --silent \
       https://${gws_service}/group_sws/v3/group/u_fox/member 2>/dev/null | grep '"id": "u_fox"' | wc -l`" 2>/dev/null
   (( esec = `echo -n $(($(date +%s%N)/1000000))` - sec ))
   (( n == 0 )) && return 999999
   return 0
}

esec=0
function is_pds_up {
   host=$1
   sec="`echo $(($(date +%s%N)/1000000))`"
   n="`/usr/bin/time -f %e /usr/bin/ldapsearch \
       -h $host -p 389 \
       -b "dc=personregistry,dc=washington,dc=edu" \
       -Z -Y EXTERNAL \
       -s subtree "(uwnetid=fox)" eduPersonAffiliation 2>/dev/null | grep 'eduPersonAffiliation:' | wc -l`"
   (( esec = `echo $(($(date +%s%N)/1000000))` - sec ))
   (( n == 0 )) && return 999999
   return 0
}

esec=0
function is_pws_up {
   host=$1
   sec="`echo $(($(date +%s%N)/1000000))`"
   n="`/usr/bin/time -f %e /usr/local/curl/bin/curl \
       --resolve ${pws_service}:${host} \
       --cert ${certdir}/idp-uw.crt \
       --key ${certdir}/idp-uw.key \
       --silent \
       https://${pws_service}/identity/v2/person/fox.json 2>/dev/null | grep '"DisplayName":"Jim Fox"' | wc -l`"
   (( esec = `echo $(($(date +%s%N)/1000000))` - sec ))
   (( n == 0 )) && return 999999
   return 0
}

interactive=0
if [ -t 1 ]; then
  interactive=1
fi
# skip the question
interactive=1

  for host in $gws_hosts
  do
     echo -n "$host "
     is_it_enabled $host
     st=$?
     (( st>0 )) && {
        txt="idled"
        (( st==2 )) && txt="dead"
        (( interactive==0 )) && {
           echo "$txt"
           continue
        }
        read -p "( loadr=$txt ) Test anyway? (y)" ans
        case $ans in
          [Nn]* ) continue;;
        esac
        echo -n "$host "
     }

     is_gws_up $host
     (( st = $? ))
     (( $st==0 )) && echo "gws=$esec "
     (( $st!=0 )) && echo "gws=fail "
  done

  for host in $pds_hosts
  do
     echo -n "$host "
     is_it_enabled $host
     st=$?
     (( st>0 )) && {
        txt="idled"
        (( st==2 )) && txt="dead"
        (( interactive==0 )) && {
           echo "$txt"
           continue
        }
        read -p "( loadr=$txt ) Test anyway? (y)" ans
        case $ans in
          [Nn]* ) continue;;
        esac
        echo -n "$host "
     }

     is_pds_up $host
     (( st = $? ))
     (( $st==0 )) && echo "pds=$esec "
     (( $st!=0 )) && echo "pds=fail, "

  done

(( 0 )) && {
  for host in $pws_hosts
  do
     echo -n "$host "
     is_it_enabled $host
     st=$?
     (( st>0 )) && {
        txt="idled"
        (( st==2 )) && txt="dead"
        (( interactive==1 )) && {
           echo "$txt"
           continue
        }
        read -p "( loadr=$txt ) Test anyway? (y)" ans
        case $ans in
          [Nn]* ) continue;;
        esac
        echo -n "$host "
     }

     is_pws_up $host
     (( st = $? ))
     (( $st==0 )) && echo "pws=$esec "
     (( $st!=0 )) && echo "pws=fail, "

  done
}

  exit 0

