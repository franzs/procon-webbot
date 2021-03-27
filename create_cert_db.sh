#!/bin/bash

NSS_DIR=nss
CERT_DIR=certs

rm -rf -- "${NSS_DIR}" && mkdir "${NSS_DIR}"

for cert in ${CERT_DIR}/*; do
  cn="$(openssl x509 -in "${cert}" -noout -subject | sed -e 's/^.*, CN = //')"
  certutil -A -n "${cn}" -t "c,c," -d "${NSS_DIR}" -t ,, -i "${cert}"
done
