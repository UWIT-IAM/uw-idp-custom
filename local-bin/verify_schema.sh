#!/bin/bash
echo "[[ $1 ]]"
export JAVA_HOME=/usr/local/java
/data/local/idp/local-bin/xmlsectool-3.0.0/xmlsectool.sh \
   --inFile $1 \
     --validateSchema \
     --schemaDirectory /data/local/idp/local-bin/xmlsectool-3.0.0/schemas 
