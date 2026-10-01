#!/usr/bin/env bash
set -euo pipefail
CERT_DIR="${CERT_DIR:-./certs}"
CN="${TLS_CN:-localhost}"
mkdir -p "$CERT_DIR"
if [[ -f "$CERT_DIR/fullchain.pem" && -f "$CERT_DIR/privkey.pem" ]]; then
  echo "Certs already exist, skipping."; exit 0
fi
openssl req -x509 -nodes -newkey rsa:2048 -days 365 \
  -subj "/C=RU/ST=Local/L=Local/O=Dev/CN=$CN" \
  -addext "subjectAltName=DNS:$CN,DNS:localhost,IP:127.0.0.1" \
  -keyout "$CERT_DIR/privkey.pem" -out "$CERT_DIR/fullchain.pem"
chmod 600 "$CERT_DIR/privkey.pem"
echo "Done: $CERT_DIR/"
