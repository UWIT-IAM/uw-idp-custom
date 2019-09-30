#!/bin/bash
# get a copy of incommon metadata
# run by cron

cd /data/local/idp-3.4/metadata
curl -o InCommon-metadata.xml http://md.incommon.org/InCommon/InCommon-metadata.xml


