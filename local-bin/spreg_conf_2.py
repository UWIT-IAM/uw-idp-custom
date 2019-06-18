
idp_base = '/data/local/idp-3.4/'

tgtid_db = {
 "db_host": "localhost",
 "db_name": "idp",
 "db_user": "shib",
 "db_pass": "spud123",
}

spreg_db_DEV = {
 'db_host': 'iamdbdev01',
 'db_name': 'spreghistory2018',
 'db_user': 'spreg1',
 'db_pass': 'ae500169-e8b9-4945-ba56-10d59d380067',
}
spreg_db = {
 'db_host': 'iamdb11',
 'db_name': 'spregistry',
 'db_user': 'spreg1',
 'db_pass': '47dafbe2-2c28-4a16-a549-591285c62e5a',
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
      {'type': 'filter', 'id':'uwrp', 'dir': 'conf', 'filename': 'rp-filter.xml', 'min_rows': 300},
      {'type': 'access_control', 'dir': 'conf', 'filename': 'uw-auto-rps.xml', 'min_rows': 0}
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

alert_component = 'spreg-updater'
alert_kba = 'KB0028719'
alert_ci_name = 'Shibboleth IDP Cluster'

