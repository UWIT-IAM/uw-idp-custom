"""Contains config values used by the scripts in this folder.

TODO: De-duplicate this file with the other conf.py file."""

import yaml

idp_base = '/data/local/idp/'

creds_dir = idp_base + "credentials/"
conf_dir = idp_base + '/conf/'
filter_dir = idp_base + '/conf/'
metadata_dir = idp_base + '/rp-metadata/'
metadata_cache_dir = idp_base + '/rp-metadata-cache/'
tmp_dir = idp_base + 'tmp/'
archive_dir = idp_base + 'archive/'
template_dir = conf_dir

# Prefer this config object for creds
spreg_creds = None
with open(creds_dir + "db.yaml", "r") as creds_file:
  spreg_creds = yaml.safe_load(creds_file)

# Shortcuts for backward compatibility, deprecated
tgtid_db = spreg_creds["tgtid_db"]
spreg_db_TEST = spreg_creds["spreg_db_TEST"]
spreg_db = spreg_creds["spreg_db"]

idp_conf_files = {
    'groups': [
      {'type': 'metadata', 'id':'uwrp', 'dir': 'metadata', 'filename': 'UW-rp-metadata.xml', 'min_rows': 500},
      {'type': 'filter', 'id':'uwrp', 'dir': 'conf', 'filename': 'rp-filter.xml', 'min_rows': 300}
    ]
}
autorps_filename = 'uw-auto-rps.xml'
autotoken_filename = 'autotoken.txt'
dynamic_filename = 'dynamic-mfa.txt'
dynamic_path = idp_base + 'conf/authn/' + dynamic_filename
dynamic_filename_base = 'dynamic-mfa.base'
dynamic_json = 'dynamic-mfa.json'

# unedited files 
#      {'type': 'filter', 'id':'uwcore', 'dir': 'conf', 'filename': 'core-filter.xml', 'min_rows': 2},
#      {'type': 'metadata', 'id':'uwbase', 'dir': 'metadata', 'filename': 'UW-base-metadata.xml', 'min_rows': 1},

metadata_files = [
    idp_base + '/metadata/UW-base-metadata.xml',
    idp_base + '/metadata/UW-rp-metadata.xml',
    idp_base + '/metadata-cache/InCommon-metadata.xml'
 ]
saml_validator = idp_base + 'local-bin/verify_schema.sh'

emails = {
 'mail_to': 'fox@uw.edu',
 'mail_from': 'The IdP at idpdev01 <somebody@idpdev01.s.uw.edu>',
 'mail_smtp': 'appsubmit.cac.washington.edu',
}

rp_filter_file = 'rp-filter.xml'
attribute_resolver_activators = 'attribute-resolver-activators.xml'
attribute_resolver_activators_j2 = 'attribute-resolver-activators.j2'
nameid_exceptions = 'saml-nameid-exceptions.xml'
nameid_exceptions_j2 = 'saml-nameid-exceptions.j2'

syslog_facility = 'LOG_LOCAL5'

alert_component = 'spreg-updater'
alert_kba = 'KB0028719'
alert_ci_name = 'Shibboleth IDP Cluster'

# headers

xml_headers = [
  {'type':'filter', 'row':'header_xml', 'id':'uwrp', 'xml':
     '<?xml version="1.0" encoding="UTF-8"?>' \
     '<AttributeFilterPolicyGroup id="ServerRegFilterPolicy" ' \
     'xmlns="urn:mace:shibboleth:2.0:afp" '\
     'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
     'xmlns:oidcext="org.geant.idpextension.oidc.attribute.filter" ' \
     'xsi:schemaLocation="urn:mace:shibboleth:2.0:afp classpath:/schema/shibboleth-2.0-afp.xsd ' \
         'org.geant.idpextension.oidc.attribute.filter classpath:/schema/idp-oidc-extension-afp.xsd" >'
  },
  {'type':'filter', 'row':'footer_xml', 'id':'uwrp', 'xml': '</AttributeFilterPolicyGroup>'},
]


