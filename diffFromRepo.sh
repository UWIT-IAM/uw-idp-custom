#!/bin/bash

# This script compares the contents of the uw-idp-custom source code repository (which holds
# our source-controlled configuration) with the contents of a Shibboleth deployment directory
# to verify that the two are synchronized, or to identify differences.
#
# There are a few complexities due to the fact that the deployment intentionally contains files
# and directories that are not source-controlled and therefore not in the repository. This script
# handles and skips those known cases. In particular:
# 1. There are five dynamically managed files under the conf/ directory not in the repository.
# 2. The local-bin/ directory contains some Python system directories not in the repository.
# 3. The deployment contains other directories holding secrets, metadata, and Shibboleth system files.
#
# To ensure full synchronization, this script tests both directions, verifying that all files in the
# repository are reflected in the deployment and vice versa (ignoring the known exceptions).

echo "Enter path to the repository (default: /data/local/src/uw-idp-custom):"
read REPO_DIR
if [[ -z $REPO_DIR ]]
then
    REPO_DIR="/data/local/src/uw-idp-custom"
fi
if [[ ! -d $REPO_DIR ]]
then
    echo "Directory not found: $REPO_DIR"
    exit 1
fi

echo "Enter path to the Shibboleth deployment (default: /data/local/idp):"
read IDP_DIR
if [[ -z $IDP_DIR ]]
then
    IDP_DIR="/data/local/idp"
fi
if [[ ! -d $IDP_DIR ]]
then
    echo "Directory not found: $IDP_DIR"
    exit 1
fi

echo "Comparing repository $REPO_DIR to deployment $IDP_DIR"
echo ""

cd $REPO_DIR
# This compares every file in the repo directory to the matching file in the idp directory.
# The GIt-related files are ignored.
find . -name .git -prune -o -name .gitignore -prune -o -type f -exec cmp \{\} ${IDP_DIR}/\{\} \;

echo ""
echo "Comparing deployment $IDP_DIR to repository $REPO_DIR"
echo ""

# This is the more complicated logic to do the back comparison.
# First, we iterate over directories that are in the repo, which are the only ones to compare.
# Skip the .git directory.
cd $REPO_DIR
for dir in $(/bin/ls -AF . | fgrep -v .git | fgrep '/')
do
    cd $IDP_DIR
    # in the deployment, iterate over all files in the identified directory
    # exclude a few subdirectories of local-bin that are not version controlled
    for fyle in $(find $dir -path local-bin/.cpan -prune \
                         -o -path local-bin/__pycache__ -prune \
                         -o -path local-bin/py-env -prune \
                         -o -path local-bin/xmlsectool\* -prune \
                         -o -type f -print)
    do
        if [[ "$fyle" == "conf/attribute-resolver-activators.xml" \
           || "$fyle" == "conf/rp-filter.xml" \
           || "$fyle" == "conf/saml-nameid-exceptions.xml" \
           || "$fyle" == "conf/uw-auto-rps.xml" \
           || "$fyle" == "conf/authn/dynamic-mfa.txt" ]]
       then
           # do nothing, these are dynamic files not version controlled
           DUMMY_VAR=""
       else
            # compare files
            cmp $fyle ${REPO_DIR}/$fyle
        fi
    done
done

# Finally, compare files at the root of the deployment
cd $IDP_DIR
find . -maxdepth 1 -type f -exec cmp \{\} ${REPO_DIR}/\{\} \;

echo ""
echo "Comparison complete."
