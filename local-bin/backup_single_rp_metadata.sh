#!/bin/bash

# This script makes a backup copy of a relying party configuration file,
#   located in /data/local/idp/rp-metadata
# This should always be used before making any changes to ensure
# that the previous file version is preserved.
#
# This script assumes and requires that a directory named
# '/data/local/idp/rp-metadata-history' exists in which the backup copy
# may be stored.

if [ $# -lt 1 ]
then
  echo "Usage: backup_single_rp_metadata.sh <relying party configuration file>"
  echo "       e.g. 'backup_single_rp_metadata.sh 7777777777777777777777777777777777777777.xml'"
  exit 1
fi
METADATA_FILE=$1

SRC_DIR=/data/local/idp/rp-metadata
ARCHIVE_DIR=/data/local/idp/rp-metadata-history
DATE_STRING=$(date '+%Y-%m-%d.%H:%M:%S')
BACKUP_FILE=${METADATA_FILE}.$DATE_STRING

cp -p ${SRC_DIR}/${METADATA_FILE} ${ARCHIVE_DIR}/$BACKUP_FILE
chmod 444 ${ARCHIVE_DIR}/$BACKUP_FILE
