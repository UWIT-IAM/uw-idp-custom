#/bin/bash
#
# Client metadata is stored in XML files. The filename is defined as the SHA-1 hash of the entityId (see spreg_processor.py).
# This script is an alternate way to generate the filename matching a particular client.
# The script takes one argument, which is the entityId (or client_id, for OIDC clients).
# Example:
# ./getMetadataFilename.sh "https://urizen.s.uw.edu/shibboleth"

if [ $# -lt 1 ]
then
  echo "Usage: getMetadataFilename.sh <entityId>"
  exit 1
fi
ENTITY_ID=$1

# Note carefully the -n argument to the echo command. This suppresses the line feed so that the hash is computed
# only on the supplied value. Without this argument, the line feed would be included which would create a
# completely different hash value. Also, sha1sum prints a useless value after the hash, so the awk command
# returns only the first field which is the actual hash value.

HASH=$(echo -n $ENTITY_ID | sha1sum | awk '{print $1}')


# Print the filename, which is the hash value with '.xml' appended.
echo ${HASH}.xml
