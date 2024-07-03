# Credentials

Important: Don't run `git add -f` on this folder. Only use `git add`.

This contains the credentials folder we store on the idp server.

At a minimum, this folder should contain:

File    | Description
------- | ---
db.yaml | DB credentials for spregistry and other DBs. Used by Python scripts.
iamtools-client-cert.pem | The public key for the DB
iamtools-client-key.pem  | The private key for the DB
iamtools-server-ca.pem   | The public key for the CA, used for DB connections
