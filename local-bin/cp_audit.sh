#!/bin/bash

# copy daily audit to stats system

SRC=/logs/idp
TGT=idpstats@ovid.u.washington.edu:public_html/drop-`hostname -s`

[[ -n $1 ]] && YDAY="$1" || YDAY="`TZ=PST32PDT date +'%Y-%m-%d'`"

src="${SRC}/audit-${YDAY}.log"
tmp="${TGT}/audit-${YDAY}.log"

scp -i /usr/local/idp/credentials/id_rsa ${SRC}/audit-${YDAY}.log ${TGT}/audit-${YDAY}.log


# cleanup mod_evasive's logging
rm /logs/mod_evasive/dos-*

