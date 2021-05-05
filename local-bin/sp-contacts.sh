#!/bin/bash

# Run the SP Contacts recon. 
# Updates groups: u_weblogin_sp-contacts, u_weblogin_sp-contacts-uw
#
# should be redone in python?
#

# need the full InCommon metadata file
# curl -o /data/local/idp/tmp/icmd.xml http://md.incommon.org/InCommon/InCommon-metadata.xml

# need a combined UW RP metadata
# echo "<rpmd>" > /data/local/idp/tmp/uwmd.xml
# cat /data/local/idp/rp-metadata/*.xml >> /data/local/idp/tmp/uwmd.xml
# echo "</rpmd>" >> /data/local/idp/tmp/uwmd.xml

# local perl libraries required
## export PERL5LIB=/data/local/idp/local-bin/.cpan/build/XML-DOM-1.46-CAyV12/blib/arch:/data/local/idp/local-bin/.cpan/build/XML-DOM-1.46-CAyV12/blib/lib:/data/local/idp/local-bin/.cpan/build/XML-RegExp-0.04-EkvIVE/blib/arch:/data/local/idp/local-bin/.cpan/build/XML-RegExp-0.04-EkvIVE/blib/lib

export PERL5LIB=/data/local/idp/local-bin/.perl5/lib/perl5

# perl sp-contacts.pl >> /logs/idp/sp-contacts.log
perl sp-contacts.pl 


