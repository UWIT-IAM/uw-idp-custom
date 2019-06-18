#!/bin/bash

file="$1"
[[ -n $file ]] || {
  echo "usage: $0 filter_file"
  exit 1
}

/usr/local/idp/samlsign-1.0/samlsign.sh --validateSchema --inFile $1 --schemaExtension /schema/shibboleth-2.0-afp.xsd --schemaExtension  /schema/shibboleth-2.0-afp-mf-basic.xsd --schemaExtension /schema/shibboleth-2.0-afp-mf-saml.xsd

