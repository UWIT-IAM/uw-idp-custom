#!/bin/bash

# test apis used by idp

host=`hostname -s`

service=groups.uw.edu

log=test_dependencies.log
((start_sec = `date +%s`))

wd="`dirname \"$0\"`"
cd $wd

. /data/local/iam-test/testlib.sh
. /data/local/gws-provisioning/bin/gws_lib.sh
certdir=/data/local/idp-3.4/credentials

gws_hosts="iam21 iam22 iam23 iam26"
pws_hosts="it-ws1 it-ws2 it-ws3 it-ws4"

## [[ "$1" == "" ]] || hosts="$1"

# notifier
function tell_someone {
   echo "GWS failed: $1" | mailto 2064198630@txt.att.net -s "GWS failure"
}

# test if host is loadr idled
function is_it_enabled {
  host="$1"
  load="`ding dnsload11 loadm su1 | egrep \" ${host}\"|awk '{print $1}'`"
  [[ -z $load ]] && return 9999999  # dead
  (( load < 900000 )) && return 0   # up
  return $load
}

#  curl --cert xxx --key xxx --cacert xxx --resolve 'groups.uw.edu:128.208.178.148' https://groups.uw.edu/group_sws/v3/group/u_fox/member
# creates a new file descriptor 3 that redirects to 1 (STDOUT)
exec 3>&1 
# Run curl in a separate command, capturing output of -w "%{http_code}" into HTTP_STATUS
# and sending the content to this command's STDOUT with -o >(cat >&3)
HTTP_STATUS=$(curl -w "%{http_code}" -o >(cat >&3) 'http://example.com')

curl -I http://www.example.org -o >(cat >&1) -w "%{http_code}" 1>&2


gsec=0
function is_gws_up {
   host=$1

   gsec="`/usr/bin/time -f %e /data/local/bin/webisoget \
       -map groups.uw.edu=${gws} \
       -out ufox.$$ \
       -header 'accept: text/xml' \
       -cert ${certdir}/gws.cac-uw.crt \
       -key ${certdir}/gws.cac-uw.key \
       -url https://${service}/group_sws/v2/group/u_fox${mbr} 2>&1`"
   n="`grep \"class=\\"${class}\\"\" ufox.$$ | wc -l`"
   rm -r ufox.$$
   (( n == 0 )) && return 999999
   return 0
}

status_page="/www/iam-status/gws-status.html"
status_page_tmp=${status_page}.$$
function start_status_page {
   now="`date +"%a %b %d %X"`"
   echo "<html><head><title>IdP Status</title>" > $status_page_tmp
   echo "<link rel=\"stylesheet\" type=\"text/css\" href=\"iam-status.css\"/>" >> $status_page_tmp
   echo "<meta http-equiv=\"refresh\" content=\"20\"></head><body><b>GWS status</b><p>" >> $status_page_tmp
}
function end_status_page {
   echo "<div class=\"footer\">reported by: $host<br>$now</div></body></html>" >> $status_page_tmp
   mv $status_page_tmp $status_page
   [[ $host == "iamtools11" ]] && scp $status_page iamtools12:$status_page
   [[ $host == "iamtools12" ]] && scp $status_page iamtools11:$status_page
}



#
# interactive,
#
if [ -t 1 ]; then
  # try all hosts in the list
  echo "Testing GWS service on $service"
  for gws in $hosts
  do
     echo -n "$gws "
     is_gws_enabled $gws
     st=$?
     (( st>=900000 )) && {
        txt="idled"
        (( st==9999999 )) && txt="dead"
        read -p "( loadr=$txt ) Test anyway? (y)" ans
        case $ans in
          [Nn]* ) continue;;
        esac
        echo -n "$gws "
     }

     is_gws_up $gws
     (( st = $? ))
     (( $st==0 )) && echo -n "gws-db ($gsec), "
     (( $st!=0 )) && echo -n "gws-db fail, "

     is_gws_up $gws ldap
     (( st = $? ))
     (( $st==0 )) && echo "gws-ldap ($gsec) "
     (( $st!=0 )) && echo "gws-ldap fail "
  done
  exit 0
fi

#
# not interactive.  test, write log, send alerts
#
# exit_if_not_master

{
echo -n "`date`. "
start_status_page

[[ -n $1 ]] && hosts="$*"


# try all hosts in the list

fail1=
for gws in $hosts
do
   echo -n "$gws "
   is_gws_enabled $gws
   (( $?>=900000 )) && {
      echo -n "(disabled) "
      echo "<span class=\"idle\" title=\"not in cluster\">$gws</span> " >> $status_page_tmp
      continue
   }
   is_gws_up $gws
   st=$?
   (( $st==0 )) && echo "<span class=\"good\" title=\"$gsec sec\">${gws}-db</span>" >> $status_page_tmp
   (( $st!=0 )) && fail1="$fail1 ${gws}" && echo "<span class=\"bad\" title=\"database access failed\">${gws}-db</span>" >> $status_page_tmp
   is_gws_up $gws ldap
   st=$?
   (( $st==0 )) && echo "<span class=\"good\" title=\"$gsec sec\">${gws}-ldap</span>" >> $status_page_tmp
   (( $st!=0 )) && fail1="$fail1 ${gws}" && echo "<span class=\"bad\" title=\"ldap access failed\">${gws}-ldap</span>" >> $status_page_tmp
done

[[ -z $fail1 ]] && {
  ((et = `date +%s` - start_sec))
  echo "OK, in $et seconds"
  end_status_page
  exit 0
}
echo ""
echo "  fail1 = $fail1"
echo "<p>retry<p>" >> $status_page_tmp

# retry the failed ones
sleep 10

fail2=
for gws in $fail1
do
   echo -n "retry $gws "
   is_gws_enabled $gws
   (( $?!=0 )) && {
      echo -n "(disabled) "
      continue
   }
   is_gws_up $gws
   st=$?
   (( $st==0 )) && echo "<span class=\"good\" title=\"$gsec sec\">${gws}-db</span>" >> $status_page_tmp
   (( $st!=0 )) && fail2="$fail2 ${gws}-db" && echo "<span class=\"bad\" title=\"group access failed\">${gws}-db</span>" >> $status_page_tmp
   is_gws_up $gws ldap
   st=$?
   (( $st==0 )) && echo "<span class=\"good\" title=\"$gsec sec\">${gws}-ldap</span>" >> $status_page_tmp
   (( $st!=0 )) && fail2="$fail2 ${gws}-ldap" && echo "<span class=\"bad\" title=\"group access failed\">${gws}-ldap</span>" >> $status_page_tmp
done

((et = `date +%s` - start_sec))

[[ -n $fail2 ]] && {
   echo "  retry fails for $fail2.  Reporting to Connect."
   urgency=2
   (( nfail = `echo "$fail2" | wc -w` ))
   (( nfail > 2 )) && urgency=1
   for gws in $fail2
   do
      send_alert "${gws%-*}.s.uw.edu" "GWS API test" $urgency "gws test failed for $gws" "GWS API test failed for $gws" 
   done
   end_status_page
   exit 1
}
echo "  retry OK, in $et seconds"
end_status_page

} >> $log
