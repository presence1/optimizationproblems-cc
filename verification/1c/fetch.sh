#!/bin/sh
# Download the pinned certificate files checked by check_c1c.py into DIR.
# They are read as JSON data only; SHA-256 digests are checked by the script.
set -eu
DIR=${1:?usage: fetch.sh DIR}
mkdir -p "$DIR"
RAW=https://raw.githubusercontent.com
curl -fsS -o "$DIR/K24576_0.4103333.json" \
  "$RAW/DennisKoshta/c1c-autocorrelation-certificate/a4ee94ef29ff630f4a36d0d93b8e998cf20127af/K24576_0.4103333.json"
curl -fsS -o "$DIR/certificate.json" \
  "$RAW/rozetyp/barnard-steinerberger-lower-bound/19f397152222caaef2c838bdd9c41295adb94310/certificate.json"
sha256sum "$DIR"/*
