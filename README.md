# IdP customizations for UW

These files are customization configuration for the UW Shib IdP.

Our idp servers are at:

- idp1[1-6].s.uw.edu

## File Details

There are five configuration files that are dynamically managed by scripts.
These scan the SPRegistry database for updates and rebuild the files as needed.

local-bin/spreg_processor.py manages
  conf/authn/dynamic-mfa.txt using conf/authn/dynamic-mfa.base
  conf/rp-filter.xml using template text from local-bin/spreg_conf.py
  conf/uw-auto-rps.xml using conf/uw-auto-rps.xml.j2
local-bin/filter_scan.py manages
  conf/attribute-resolver-activators.xml using conf/attribute-resolver-activators.js
  conf/saml-nameid-exceptions.xml using conf/saml-nameid-exceptions.j2

Both Python scripts are called by local-bin/refresh_uw.sh.
