## IdP customizations for UW

These files are customization configuration for the UW Shib IdP.

Presently they are for reference only.  Not meant to be installed.

Jim Fox
fox@uw.edu


There are four configuration files that are dynamically managed by scripts.
These scan the SPRegistry database for updates and rebuild the files as needed.

local-bin/spreg_processor.py manages
  conf/authn/dynamic-mfa.txt using conf/authn/dynamic-mfa.base
  conf/rp-filter.xml using template text from local-bin/spreg_conf.py
  conf/uw-auto-rps.xml using conf/uw-auto-rps.xml.j2
local-bin/filter_scan.py manages
  conf/saml-nameid-exceptions.xml using conf/saml-nameid-exceptions.j2

Both Python scripts are called by local-bin/refresh_uw.sh.

