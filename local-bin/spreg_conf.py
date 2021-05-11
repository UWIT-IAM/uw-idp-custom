
idp_base = '/data/local/idp/'

tgtid_db = {
 "db_host": "localhost",
 "db_name": "idp",
 "db_user": "shib",
 "db_pass": "spud123",
}

# setting for iam-tools-test spreg
spreg_db_TEST = {
 'db_host': 'iamdbdev20',
 'db_name': 'spregistry',
 'db_user': 'spreg1',
 'db_pass': 'ae500169-e8b9-4945-ba56-10d59d380067',
}

# setting for iam-tools spreg
spreg_db = {
 'db_host': 'iamdb21',
 'db_name': 'spregistry',
 'db_user': 'spreg1',
 'db_pass': '47dafbe2-2c28-4a16-a549-591285c62e5a',
}

conf_dir = idp_base + 'conf/'
metadata_dir = idp_base + 'rp-metadata/'
metadata_cache_dir = idp_base + '/rp-metadata-cache/'
tmp_dir = idp_base + 'tmp/'
archive_dir = idp_base + 'archive/'
template_dir = conf_dir

filter_dir = idp_base + 'conf/'
filter_filename = 'rp-filter.xml'
filter_id = 'uwrp'
filter_min_rows = 300

metadata_id = 'uwrp'
metadata_min_rows = 500

# old config 
idp_conf_files = {
    'groups': [
      {'type': 'metadata', 'id':'uwrp', 'dir': 'metadata', 'filename': 'UW-rp-metadata.xml', 'min_rows': 500},
      {'type': 'filter', 'id':'uwrp', 'dir': 'conf', 'filename': 'rp-filter.xml', 'min_rows': 300}
    ]
}

# auto config elements
autorps_filename = 'uw-auto-rps.xml'
autotoken_filename = 'autotoken.txt'
dynamic_filename = 'dynamic-mfa.txt'
dynamic_path = idp_base + 'conf/authn/' + dynamic_filename
dynamic_base_filename = 'dynamic-mfa.base'
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

rp_filter_file = filter_filename
attribute_resolver_activators = 'attribute-resolver-activators.xml'
attribute_resolver_activators_j2 = 'attribute-resolver-activators.j2'
nameid_exceptions = 'saml-nameid-exceptions.xml'
nameid_exceptions_j2 = 'saml-nameid-exceptions.j2'

syslog_facility = 'LOG_LOCAL5'

alert_component = 'spreg-updater'
alert_kba = 'KB0028719'
alert_ci_name = 'Shibboleth IDP Cluster'

# headers

filter_header_xml = '<?xml version="1.0" encoding="UTF-8"?>' \
     '<AttributeFilterPolicyGroup id="ServerRegFilterPolicy" ' \
     'xmlns="urn:mace:shibboleth:2.0:afp" '\
     'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
     'xmlns:oidcext="org.geant.idpextension.oidc.attribute.filter" ' \
     'xsi:schemaLocation="urn:mace:shibboleth:2.0:afp classpath:/schema/shibboleth-2.0-afp.xsd ' \
         'org.geant.idpextension.oidc.attribute.filter classpath:/schema/idp-oidc-extension-afp.xsd" >'
filter_footer_xml = '</AttributeFilterPolicyGroup>'


