#!/bin/sh
# Fetch everything the audit scripts read, into a fresh directory ROOT:
#   ROOT/clean/v1d ... v49a       clones of the verify/* branches (the code under audit)
#   ROOT/data/1d, 1c, 70a, 16a, 49a/{syl,irsi}   certificate data, pinned and hash-checked
# Every certificate file is checked against a pinned SHA-256 (or, where the
# constant page records none, against the value observed during this audit).
# Nothing fetched here is executed; the audit scripts read it as data.
set -eu
ROOT=${1:?usage: fetch_all.sh EMPTY_DIR}
FORK=${FORK:-https://github.com/presence1/optimizationproblems-cc}
mkdir -p "$ROOT/clean" "$ROOT/data/1d" "$ROOT/data/1c" "$ROOT/data/70a" "$ROOT/data/16a" \
         "$ROOT/data/49a/syl" "$ROOT/data/49a/irsi" "$ROOT/data/49a/clones"
RAW=https://raw.githubusercontent.com

for b in 1d 1c 70a 16a 49a; do
  git clone -q --depth 5 --branch "verify/$b" "$FORK" "$ROOT/clean/v$b"
done
# branch tips audited
( cd "$ROOT/clean" && for b in 1d 1c 70a 16a 49a; do printf 'v%s %s\n' "$b" "$(git -C v$b rev-parse --short HEAD)"; done )

curl -fsS -o "$ROOT/data/1d/steps_construction.json" \
  "$RAW/steps-re/c1d-certificate/9a091494facc801eaf6b92b175b63c58b7c3b30b/construction.json"
curl -fsS -o "$ROOT/data/1d/problem_4_signed_autoconvolution_bounds.py.txt" \
  "$RAW/unclegareth-create/alphaevolve_repository_of_problems/4b3bbd2a44db92442e4ebb4e64e0bb90f229aad1/experiments/autocorrelation_problems/problem_4_signed_autoconvolution_bounds.py"
curl -fsS -o "$ROOT/data/1d/cert300_construction.json" \
  "$RAW/extremal-values-registry/extremal-values-registry/50520b971e5d234bc9c4ccbdcd5a5107d5bb8791/certificates/third_autocorrelation_abs_inside/construction.json"
curl -fsS -o "$ROOT/data/1c/K24576_0.4103333.json" \
  "$RAW/DennisKoshta/c1c-autocorrelation-certificate/a4ee94ef29ff630f4a36d0d93b8e998cf20127af/K24576_0.4103333.json"
curl -fsS -o "$ROOT/data/1c/certificate.json" \
  "$RAW/rozetyp/barnard-steinerberger-lower-bound/19f397152222caaef2c838bdd9c41295adb94310/certificate.json"

git clone -q https://github.com/rpinho/c70-certificate "$ROOT/data/70a/c70-certificate"
git -C "$ROOT/data/70a/c70-certificate" checkout -q 680e074bb50929734bfd76484d716cd3e85827f0
git clone -q https://github.com/maximusrufus/c16-bgw-certificates "$ROOT/data/16a/c16-bgw-certificates"
git -C "$ROOT/data/16a/c16-bgw-certificates" checkout -q 0c570700f080ca23549e10380901addfc8b7b8ae

git clone -q https://github.com/xSyllaa/sunflower-pendant-chain "$ROOT/data/49a/clones/syl"
git -C "$ROOT/data/49a/clones/syl" show 8e21d02:data/B.txt > "$ROOT/data/49a/syl/B.txt"
git -C "$ROOT/data/49a/clones/syl" show 8e21d02:data/Bprime.txt > "$ROOT/data/49a/syl/Bprime.txt"
git clone -q https://github.com/Aspect5/sunflower-free-capacity "$ROOT/data/49a/clones/irsi"
# by commit, not by tag (tags can be moved): v1.0, v1.1, v1.2
git -C "$ROOT/data/49a/clones/irsi" show 4d23c9ad391c9a087cad03a3c3346b5f79badae0:cert_c49_chain20.json > "$ROOT/data/49a/irsi/v10.json"
git -C "$ROOT/data/49a/clones/irsi" show f685bfab116e36568aacc9558eb582376764b88d:cert_c49_chain20_s17.json > "$ROOT/data/49a/irsi/v11_s17.json"
git -C "$ROOT/data/49a/clones/irsi" show e478c81d8b57eba956fdaf621643eb6f0781f820:cert_c49_chain20_v12.json > "$ROOT/data/49a/irsi/v12.json"

cd "$ROOT/data"
sha256sum -c <<'EOF'
3dd39fae744555179b0356b84e752db724e892bd23dda51403976edfb5b3a28c  1d/steps_construction.json
1a290ad1074c10a871adaf2bd44402af56be8cf151f1f775a8fc37c7bdff54b2  1d/problem_4_signed_autoconvolution_bounds.py.txt
51f864ee95205f06b98923c382d23cb3dfde5f0d4208a4c591bad015e5908a0e  1d/cert300_construction.json
963cb7273062e7360fdfa460bb19c1cf37729364b8f708b09580b6655b783c9e  1c/K24576_0.4103333.json
62ac49ddbbfc9aa1053406363d9df9c912022ab85b72a447cf73c94bb9c1fd0e  1c/certificate.json
03ff0d6df3dfa6ea06f901a9319c968eb7c013f5d0cc3f1f00cfa58e9490c0cc  70a/c70-certificate/certificates/c70_candidate.json
de314c10bd4a63d35604d28c0d0556b8b5ae67ab1840c06628039d8fd64b6991  16a/c16-bgw-certificates/lower_certificate.json
340cef5e71124ed624425abf81e9621839406cbf44b3fd242594d8edcb7d37af  49a/syl/B.txt
2a72385704b8203269cda4f4b0dfdabc74d5adb8f4a2bc1dac1f570cb96b5cec  49a/syl/Bprime.txt
c30a74fed64616c5c6980fae91f94ae5899fed6a4cb338b537480ee9517d715b  49a/irsi/v10.json
c12d0dd62500a97484cb4f72743803ea7b54e74272e2b474cbabeac7b256fc7b  49a/irsi/v11_s17.json
7472112ced9d98da8cf7b6a3d586b93ea66750e39989e7a6d6d5f52ffeb4e82e  49a/irsi/v12.json
EOF
