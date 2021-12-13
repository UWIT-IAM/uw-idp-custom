#!/bin/bash

# run the netid_exceptions script

# args:  "method" "type" "netid" "remote_user_cn" "remote_addr"

export LD_LIBRARY_PATH=/usr/local/pgsql-12.2/lib

cd /data/local/idp/local-bin
. py-env/bin/activate

python netid_exception.py $*


