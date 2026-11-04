#!/bin/sh
# Download the pinned certificate files checked by check_c1d.py into DIR.
# Files are only read as data by the checker (never executed); their SHA-256
# digests are compared against the values pinned in check_c1d.py.
set -eu
DIR=${1:?usage: fetch.sh DIR}
mkdir -p "$DIR"
RAW=https://raw.githubusercontent.com
curl -fsS -o "$DIR/steps_construction.json" \
  "$RAW/steps-re/c1d-certificate/9a091494facc801eaf6b92b175b63c58b7c3b30b/construction.json"
curl -fsS -o "$DIR/problem_4_signed_autoconvolution_bounds.py.txt" \
  "$RAW/unclegareth-create/alphaevolve_repository_of_problems/4b3bbd2a44db92442e4ebb4e64e0bb90f229aad1/experiments/autocorrelation_problems/problem_4_signed_autoconvolution_bounds.py"
curl -fsS -o "$DIR/cert300_construction.json" \
  "$RAW/extremal-values-registry/extremal-values-registry/50520b971e5d234bc9c4ccbdcd5a5107d5bb8791/certificates/third_autocorrelation_abs_inside/construction.json"
sha256sum "$DIR"/*
