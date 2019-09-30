
idp_base = '/data/local/idp-3.4/'
gateway_base = '/data/local/gateway/'

tgtid_db = {
 "db_host": "localhost",
 "db_name": "idp",
 "db_user": "shib",
 "db_pass": "spud123",
}

prod_spreg_db = {
 'db_host': 'iamdb11',
 'db_host_dev': 'iamdbdev01',
 'db_name': 'spregistry',
 'db_user': 'spreg1',
 'db_pass': '47dafbe2-2c28-4a16-a549-591285c62e5a',
 'db_pass_dev': 'ae500169-e8b9-4945-ba56-10d59d380067',
}

spreg_db = {
 'db_host': 'iamdbdev01',
 'db_name': 'spregtestimport2',
 'db_user': 'spreg1',
 'db_pass': 'ae500169-e8b9-4945-ba56-10d59d380067',
}

conf_dir = idp_base + '/conf/'
metadata_dir = idp_base + '/metadata/'
tmp_dir = idp_base + 'tmp/'
archive_dir = idp_base + 'archive/'
template_dir = conf_dir

idp_conf_files = {
    'groups': [
      {'type': 'metadata', 'id':'uwbase', 'dir': 'metadata', 'filename': 'UW-base-metadata.xml', 'min_rows': 1},
      {'type': 'metadata', 'id':'uwrp', 'dir': 'metadata', 'filename': 'UW-rp-metadata.xml', 'min_rows': 500},
      {'type': 'filter', 'id':'uwcore', 'dir': 'conf', 'filename': 'core-filter.xml', 'min_rows': 2},
      {'type': 'filter', 'id':'uwrp', 'dir': 'conf', 'filename': 'rp-filter.xml', 'min_rows': 300}
    ]
}

metadata_files = [
    idp_base + '/metadata/UW-base-metadata.xml',
    idp_base + '/metadata/UW-rp-metadata.xml',
    idp_base + '/metadata-cache/InCommon-metadata.xml'
 ]
saml_sign = idp_base + 'local-bin/samlsign-1.0/samlsign.sh'

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
