#!/bin/bash
# cleanup logs and directories

cd /logs/idp
[[ `pwd` == "/logs/idp" ]] || {
   echo "No /logs/idp??"
   exit 1
}

find . -maxdepth 1 -name 'process-*log*' -mtime +30 -delete
find . -maxdepth 1 -name 'warn-*log*' -mtime +30 -delete
find . -maxdepth 1 -name 'audit-*log*' -mtime +90 -delete

# keep the updater logs short
tail -1000 refresh_uw.log > refresh_uw.new
mv refresh_uw.new refresh_uw.log
tail -1000 refresh_ic.log > refresh_ic.new
mv refresh_ic.new refresh_ic.log

# cleanup the archive

cd /data/local/idp/archive
[[ `pwd` == "/data/local/idp/archive" ]] || {
   echo "No //data/local/idp/archive??"
   exit 1
}

find . -maxdepth 1 -name 'UW-rp-metadata*' -mtime +30 -delete
find . -maxdepth 1 -name 'attribute-resolver-activators*' -mtime +30 -delete
find . -maxdepth 1 -name 'rp-filter*' -mtime +30 -delete
find . -maxdepth 1 -name 'dynamic-mfa.txt*' -mtime +30 -delete
find . -maxdepth 1 -name 'uw-auto-rps*' -mtime +60 -delete
find . -maxdepth 1 -name 'autotoken*' -mtime +60 -delete
find . -maxdepth 1 -name 'saml-nameid-exceptions*' -mtime +60 -delete

