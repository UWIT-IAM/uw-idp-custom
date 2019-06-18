#!/bin/bash
# cleanup logs and directories

cd /logs/idp

find . -maxdepth 1 -name 'process-*log*' -mtime +30 -delete
find . -maxdepth 1 -name 'warn-*log*' -mtime +30 -delete
find . -maxdepth 1 -name 'audit-*log*' -mtime +90 -delete

# keep the updater logs short
tail -1000 refresh_uw.log > refresh_uw.new
mv refresh_uw.new refresh_uw.log
tail -1000 refresh_ic.log > refresh_ic.new
mv refresh_ic.new refresh_ic.log


