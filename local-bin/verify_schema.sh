#!/bin/bash
echo "[[ $1 ]]"
SCRIPT_DIR=$(dirname $0)
. $SCRIPT_DIR/setJavaHome.sh
/data/local/idp/local-bin/xmlsectool-3.0.0/xmlsectool.sh \
   --inFile $1 \
     --validateSchema \
     --schemaDirectory /data/local/idp/local-bin/xmlsectool-3.0.0/schemas 
