#!/bin/bash

# Run the SP Contacts recon. 
# Updates groups: u_weblogin_sp-contacts, u_weblogin_sp-contacts-uw
#
# should be redone in python?
#

# local perl libraries required
# ~iamidp/.cpan -> ./.cpan

cd /data/local/idp/local-bin

idpdev11(iamidp)$ export PERL5LIB=~iamidp/.cpan/build/XML-DOM-1.46-CAyV12/blib/arch:~iamidp/.cpan/build/XML-DOM-1.46-CAyV12/blib/lib:~iamidp/.cpan/build/XML-RegExp-0.04-EkvIVE/blib/arch:~iamidp/.cpan/build/XML-RegExp-0.04-EkvIVE/blib/lib

perl sp-contacts.pl >> /logs/idp/sp-contacts.log


