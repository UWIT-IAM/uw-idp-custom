#!/bin/bash

# Run the SP Contacts recon. 
# Updates groups: u_weblogin_sp-contacts, u_weblogin_sp-contacts-uw
#
# should be redone in python?
#

# local perl libraries required
# ~fox/.cpan -> /data/local/src/fox/.cpan

cd /data/local/idp-3.4/local-bin

export PERL5LIB=/usr/lusers/fox/.cpan/build/XML-DOM-1.46-5M9hkB/blib/arch:/usr/lusers/fox/.cpan/build/XML-DOM-1.46-5M9hkB/blib/lib:/usr/lusers/fox/.cpan/build/XML-RegExp-0.04-mVkl0x/blib/arch:/usr/lusers/fox/.cpan/build/XML-RegExp-0.04-mVkl0x/blib/lib

perl sp-contacts.pl >> /logs/idp/sp-contacts.log


