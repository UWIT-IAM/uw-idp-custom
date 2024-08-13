#!/bin/bash

# This script compares the contents of the uw-idp-custom source code repository (which holds
# our source-controlled configuration) with the contents of a Shibboleth deployment directory
# and copies files from the repo to the deployment to synchronize them.
#
# Note that both the comparison and the copy is only from the repository to the deployment,
# not in the other direction. This means that afterwards the deployment may contain files
# not reflected in the repository. (Use the diffFromRepo.sh script to detect such cases).
# This script is intended to support deployments where updated files are pushed
# from the repository into the deployment.
#
# The script will first check for and display differences, then prompt the caller to review
# those differences before confirming the file copy.

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

echo ""
echo "Checking for differences between repository $REPO_DIR and deployment $IDP_DIR..."
echo ""

cd $REPO_DIR
FILES_TO_UPDATE=""
# This finds every file in the repository, ignoring Git-related files.
for fyle in $(find . -name .git -prune -o -name .gitignore -prune -o -type f -print)
do
    if [[ $(cmp $fyle $IDP_DIR/$fyle) ]]
    then
        FILES_TO_UPDATE="${FILES_TO_UPDATE} $fyle"
    fi
done

# Display each file to be updated.
for fyle in $FILES_TO_UPDATE
do
    echo $fyle
done

# Prompt the user to confirm the update.
echo ""
echo "The repository is $REPO_DIR"
echo "The deployment is $IDP_DIR"
echo "Do you want to update files as shown above? (y/n)"
read SHOULD_UPDATE

# Updated if approved.
if [[ ("y" = "$SHOULD_UPDATE") || ("Y" = "$SHOULD_UPDATE") ]]
then
    echo ""
    echo "Synchronizing the following files:"
    for file_to_update in $FILES_TO_UPDATE
    do
        echo $file_to_update
        cp -p $file_to_update $IDP_DIR/$file_to_update
    done
else
    echo "Aborting, no files updated."
fi

