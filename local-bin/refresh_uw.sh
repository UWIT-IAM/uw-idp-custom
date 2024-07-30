#!/bin/bash

# update uw rp filter and metadata from database
# unless 'force', requires flag file present

[[ "$1" == "force" ]] || {
   [[ -f /www/refresh_uw/data/refresh ]] || exit 0
   [[ -f /www/refresh_uw/data/norefresh ]] && exit 0
   lockfile -r 0 -l 600 /www/refresh_uw/lock || exit 1
}

date
rm -f /www/refresh_uw/data/refresh

root=/data/local/idp
cd ${root}/local-bin

. py-env/bin/activate
. setJavaHome.sh
export LD_LIBRARY_PATH=/usr/local/pgsql-12.2/lib

{

md_pre="`date +%s -r ${root}/metadata/UW-rp-metadata.xml`"
filter_pre="`date +%s -r ${root}/conf/rp-filter.xml`"
nameid_pre="`date +%s -r ${root}/conf/saml-nameid-exceptions.xml`"
attrs_pre="`date +%s -r ${root}/conf/attribute-resolver-activators.xml`"
auto_pre="`date +%s -r ${root}/conf/uw-auto-rps.xml`"

uparg=
[[ $1 == "force" ]] && uparg="-f"
# python spreg_update_4.py $uparg -v
python spreg_processor.py $uparg -v

# if rp-metadata changed, notify idp
md_post="`date +%s -r ${root}/metadata/UW-rp-metadata.xml`"
(( md_post > md_pre + 60 )) && {
   echo "notify idp of metadata change"
   ## this causes too much overhead.. reloading incommon metadata
   ## ${root}/bin/reload-service.sh -id shibboleth.MetadataResolverService
}

filter_post="`date +%s -r ${root}/conf/rp-filter.xml`"
auto_post="`date +%s -r ${root}/conf/uw-auto-rps.xml`"

# if rp-filter changed, run the filter analyzer
(( filter_post > filter_pre + 60 )) && {
   echo "running the filter analyzer"
   python filter_scan.py
}

nameid_post="`date +%s -r ${root}/conf/saml-nameid-exceptions.xml`"
attrs_post="`date +%s -r ${root}/conf/attribute-resolver-activators.xml`"
 
(( nameid_post > nameid_pre + 60 )) && {
   echo "notify idp of nameid exceptions change"
   ${root}/bin/reload-service.sh -id shibboleth.NameIdentifierGenerationService
}

(( attrs_post > attrs_pre + 60 )) && {
   echo "notify idp of attribute resolver activators change"
   ${root}/bin/reload-service.sh -id shibboleth.AttributeResolverService
}

(( filter_post > filter_pre + 60 )) && {
   echo "notify idp of attribute filter change"
   ${root}/bin/reload-service.sh -id shibboleth.AttributeFilterService
}

(( auto_post > auto_pre + 60 )) && {
   echo "notify idp of auto rps change"
   ${root}/bin/reload-service.sh -id shibboleth.RelyingPartyResolverService
}

rm -f /www/refresh_uw/lock

} >> /logs/idp/refresh_uw.log


