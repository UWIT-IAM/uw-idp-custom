# Sample credentials

The Idp deployment contains a credentials folder containing domain-specific values and secrets.
Because of the secrets, nothing in that folder is version controlled.
This README file describes the function of the files in the credentials folder,
and this directory contains sample files that illustrate the expected content.

Two tables are below. The first lists properties files that contain configuration or secret data.
The second table lists the SSL certificates used for various purposes.

File    | Description
domain.properties | Domain-specific properties, no secrets.
secrets.properties | Various secrets defined as key-value pairs, mostly used by core Shibboleth modules.
db.yaml | DB credentials for spregistry and other DBs. Used by Python scripts.

File    | Description
iamtools-client-cert.pem | The public key for the SPRegistry DB connection.
iamtools-client-key.pem | The private key for the SPRegistry DB connection.
iamtools-server-ca.pem | The public key for the SPRegistry CA, used for the SPRegistry DB connection.
gws.cac-uw.crt | Public key for one of the UWCA certificates used to get group attributes from the UW Group Service.
gws.cac-uw.crt | Private key for that certificate.
uw-idp.crt | Public key for the other UWCA certificate used to lookup Duo and authz groups from the UW Group Service, and attributes from PWS.
uw-idp.crt | Private key for that certificate.
uw-incommon-ca.crt | A CA file containing the certificate chains for the UWCA and InCommon certificate authorities.
idp-ss-2021.crt | The Shibboleth IdP signing and encryption certificate.
idp-ss.key | The private key for that certificate.
idp-ic.crt | The Shibboleth IdP ic signing certificate, used by legacy SPs.
idp-ic.key | The private key for that certificate.
sealer.jks | Sealer key for Shibboleth.
sealer.kver | Version for the sealer key.
net.shibboleth.\* | Directories holding truststores with the public keys for Shibboleth plugins.
