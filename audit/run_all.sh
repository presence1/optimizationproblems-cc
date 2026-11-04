#!/bin/sh
# Run the whole audit.  ROOT must have been filled by fetch_all.sh.
# Requires python3 with numpy, python-flint and mpmath importable under
# `python3 -I` (i.e. NOT installed with `pip --user`: -I ignores the user
# site, and then check_c1d.py silently skips its FLINT cross-check).
# About 15 minutes on 4 cores; the mutation tests dominate.
set -eu
ROOT=${1:?usage: run_all.sh ROOT [OUTDIR]}
OUT=${2:-$ROOT/audit_logs}
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$OUT"
D=$ROOT/data
C=$ROOT/clean

# 1. reproduce the documented commands of each branch (run from the branch
#    checkout, data passed by path; nothing is run inside a third-party clone)
( cd "$C/v1d" && python3 -I verification/1d/check_c1d.py --selftest \
  && python3 -I verification/1d/check_c1d.py --data "$D/1d" ) > "$OUT/repro_1d.txt" 2>&1
( cd "$C/v1c" && python3 -I verification/1c/check_c1c.py --selftest \
  && python3 -I verification/1c/check_c1c.py --data "$D/1c" --knots 24577 --interior 2000 ) > "$OUT/repro_1c.txt" 2>&1
( cd "$C/v70a" && python3 -I verification/70a/check_c70.py --selftest \
  && python3 -I verification/70a/check_c70.py --json "$D/70a/c70-certificate/certificates/c70_candidate.json" ) > "$OUT/repro_70a.txt" 2>&1
( cd "$C/v16a" && python3 -I verification/16a/check_c16_lower.py \
  --json "$D/16a/c16-bgw-certificates/lower_certificate.json" ) > "$OUT/repro_16a.txt" 2>&1
( cd "$C/v49a" && python3 -I verification/49a/check_c49_cla2026.py --selftest \
  && python3 -I verification/49a/check_c49_cla2026.py \
  && python3 -I verification/49a/check_c49_syl2026.py --data "$D/49a/syl" \
  && python3 -I verification/49a/check_c49_irsi2026.py --data "$D/49a/irsi" ) > "$OUT/repro_49a.txt" 2>&1

# 2. the auditor's independent checks
python3 -I "$HERE/c1_independent.py" --d1 "$D/1d" --c1 "$D/1c" > "$OUT/c1_independent.txt" 2>&1
python3 -I "$HERE/c70_independent.py" --mc-repeats 16 > "$OUT/c70_independent.txt" 2>&1
python3 -I "$HERE/c16_readings.py" > "$OUT/c16_readings.txt" 2>&1
python3 -I "$HERE/c49_independent.py" --deep --syl "$D/49a/syl" --irsi "$D/49a/irsi" > "$OUT/c49_independent.txt" 2>&1

# 3. mutation tests (checker copies and mutated data go to ROOT/mut_work)
python3 -I "$HERE/mutation_tests.py" --clean "$C" --data "$D" --work "$ROOT/mut_work" -j 3 \
  --json-out "$OUT/mutation_results.json" > "$OUT/mutation_tests.txt" 2>&1 || true

grep -H -E "RESULT|SUMMARY|integrity|selftest passed" "$OUT"/*.txt
