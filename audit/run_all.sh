#!/bin/sh
# Re-run everything on replay/package.  ROOT must have been filled by fetch_all.sh.
# The code under test is the checkout that contains this script.
# Requires python3 with numpy, python-flint and mpmath importable under
# `python3 -I`, i.e. NOT installed with `pip --user` (-I ignores the user
# site).  Without python-flint, check_c1d.py and check_c1c.py now stop with
# exit status 2 instead of skipping their FLINT cross-check.
# About 20 minutes on 4 cores; the two mutation runs dominate.
set -eu
ROOT=${1:?usage: run_all.sh ROOT [OUTDIR]}
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/.." && pwd)
OUT=${2:-$ROOT/package_logs}
mkdir -p "$OUT"
D=$ROOT/data

# 1. every checker's documented commands, run from this checkout (data passed
#    by path; nothing is run inside a third-party clone)
( cd "$REPO" && python3 -I verification/1d/check_c1d.py --selftest \
  && python3 -I verification/1d/check_c1d.py --data "$D/1d" ) > "$OUT/run_1d.txt" 2>&1
( cd "$REPO" && python3 -I verification/1c/check_c1c.py --selftest \
  && python3 -I verification/1c/check_c1c.py --data "$D/1c" --knots 24577 --interior 2000 ) > "$OUT/run_1c.txt" 2>&1
( cd "$REPO" && python3 -I verification/70a/check_c70.py --selftest \
  && python3 -I verification/70a/check_c70.py --json "$D/70a/c70-certificate/certificates/c70_candidate.json" ) > "$OUT/run_70a.txt" 2>&1
( cd "$REPO" && python3 -I verification/16a/check_c16_lower.py \
  --json "$D/16a/c16-bgw-certificates/lower_certificate.json" ) > "$OUT/run_16a.txt" 2>&1
( cd "$REPO" && python3 -I verification/49a/check_c49_cla2026.py --selftest \
  && python3 -I verification/49a/check_c49_cla2026.py \
  && python3 -I verification/49a/check_c49_syl2026.py --data "$D/49a/syl" \
  && python3 -I verification/49a/check_c49_irsi2026.py --data "$D/49a/irsi" ) > "$OUT/run_49a.txt" 2>&1

# 2. the auditor's independent checks
python3 -I "$HERE/c1_independent.py" --d1 "$D/1d" --c1 "$D/1c" > "$OUT/c1_independent.txt" 2>&1
python3 -I "$HERE/c70_independent.py" --mc-repeats 16 > "$OUT/c70_independent.txt" 2>&1
python3 -I "$HERE/c16_readings.py" > "$OUT/c16_readings.txt" 2>&1
python3 -I "$HERE/c49_independent.py" --deep --syl "$D/49a/syl" --irsi "$D/49a/irsi" > "$OUT/c49_independent.txt" 2>&1

# 3. mutation tests: the full suite against this checkout, then the same
#    suite against the original (audited) checkers, to show which tests the
#    fixes turned from red to green.  Checker copies and mutated data go to
#    ROOT/mut_work*.
python3 -I "$HERE/mutation_tests.py" --package "$REPO" --data "$D" --work "$ROOT/mut_work" -j 3 \
  --json-out "$OUT/mutation_results.json" > "$OUT/mutation_tests.txt" 2>&1 || true
python3 -I "$HERE/mutation_tests.py" --clean "$ROOT/clean" --data "$D" --work "$ROOT/mut_work_original" -j 3 \
  --json-out "$OUT/mutation_results_original_checkers.json" > "$OUT/mutation_tests_original_checkers.txt" 2>&1 || true

grep -H -E "RESULT|SUMMARY|integrity|selftest passed|cross-checks" "$OUT"/run_*.txt "$OUT"/c*_*.txt "$OUT"/mutation_tests*.txt \
  | grep -v "mut_work"
