import os

CERT_FILE = '/data/local/idp/credentials/idp-uw.crt'
KEY_FILE = '/data/local/idp/credentials/idp-uw.key'

PROPS = '/data/local/idp/conf/idp.properties'
DNS_NAME = 's.uw.edu'

URL = {
    'prod': 'https://api.alerts.s.uw.edu/v1/alert',
    'eval': 'https://api.alerts-test.s.uw.edu/v1/alert',
    'dev':  'https://api.alerts-test.s.uw.edu/v1/alert'
}
