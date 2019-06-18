import os

CERT_FILE = '/data/local/idp-3.4/credentials/idp-uw.crt'
KEY_FILE = '/data/local/idp-3.4/credentials/idp-uw.key'

PROPS = '/data/local/idp-3.4/conf/idp.properties'
DNS_NAME = 's.uw.edu'

URL = {
    'prod': 'https://api.alerts.s.uw.edu/v1/alert',
    'eval': 'https://api.alerts-test.s.uw.edu/v1/alert',
    'dev':  'https://api.alerts-test.s.uw.edu/v1/alert'
}
