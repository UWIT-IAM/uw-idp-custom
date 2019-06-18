#!/bin/bash

# run the idp master

echo $$ > /var/run/idpmaster.pid

cd /data/local/idp-3.4/local-bin
. py-env/bin/activate

while :;
do
  python idp_master.py
  sleep 5
done


