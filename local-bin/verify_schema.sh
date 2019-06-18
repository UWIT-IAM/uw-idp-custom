#!/bin/bash
echo "[[ $1 ]]"
/data/local/idp-3.4/local-bin/xmlsectool-2.0.0/xmlsectool.sh \
   --inFile $1 \
     --validateSchema \
     --schemaDirectory /data/local/idp-3.4/local-bin/xmlsectool-2.0.0/schemas 
