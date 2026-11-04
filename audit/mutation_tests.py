#!/usr/bin/env python3
"""Mutation tests for the checkers in verification/{1d,1c,70a,16a,49a}/.

Written for the audit of the verify/* branches (AUDIT.md section 4, tests
1d-1 ... 49a-15) and extended on branch replay/package, after the checkers
were fixed, with tests for each new enforcement (1d-7 onwards, 1c-9 onwards,
70a-6, 16a-5, 49a-16 onwards).  1c-8 now expects failure: the recorded
minimiser is enforced.

Each test perturbs the certificate data, a recorded page value, or the
claimed bound, and runs the UNMODIFIED checker (or, where the perturbation
is of something hard-coded in the checker, a patched COPY of it) with
python3 -I in a scratch directory.  The code under test is never modified.
Some tests are code mutations: they change a line of the checker's own logic,
to see whether its internal cross-checks can fail (16a-3, 49a-4, 49a-17,
49a-19, 49a-21).  Tests marked "python3 -I -S" run the checker with the site
directories disabled, so that python-flint (and numpy, mpmath) cannot be
imported: a correct checker must then stop with a nonzero exit, never skip.

A test PASSES when the checker behaves as a correct checker must:
  - expect="fail": nonzero exit status (equal to `exit_expected` where given),
    and every marker string in `need` appears in its output (so it failed for
    the right reason);
  - expect="pass": exit status 0 (used for perturbations that a correct
    checker should accept).
A test whose patch target does not exist in the code under test is reported
as N/A ("check absent") and counts as NOT behaving correctly: that happens
when this suite is run against the original verify/* checkers, which lack
the check the test targets.
Hash-pinned data is tested twice where useful: once with the pin intact
(the checker must stop at the hash) and once with the pin updated in a
patched copy (so the mathematical path itself is exercised).

Usage:
  python3 -I mutation_tests.py (--package DIR | --clean DIR) --data DIR --work DIR
                               [--only 1d,1c,...] [-j 3] [--json-out FILE]
    --package: a checkout of replay/package (holds verification/<id>/ for
               all five constants); this is the code under test
    --clean  : instead, holds v1d v1c v70a v16a v49a, one tree per constant
               (e.g. the original verify/* checkers, see fetch_all.sh)
    --data   : holds 1d/ 1c/ 70a/c70-certificate/ 16a/c16-bgw-certificates/
               49a/syl/ 49a/irsi/  (fetched as the READMEs describe)
"""

import argparse
import concurrent.futures as cf
import hashlib
import itertools
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
from fractions import Fraction

PY = [sys.executable, "-I"]
PY_NOSITE = [sys.executable, "-I", "-S"]   # site dirs off: python-flint, numpy, mpmath unimportable
sys.dont_write_bytecode = True   # importing c49_independent must not leave __pycache__ behind


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(p):
    return sha_bytes(open(p, "rb").read())


class Ctx:
    def __init__(self, clean, data, work, package=None):
        self.clean, self.data, self.work, self.package = clean, data, work, package
        self.missing = {}   # checker-copy dir -> required patch targets that are absent

    def newdir(self, name):
        d = os.path.join(self.work, name)
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d)
        return d

    def copy_data(self, sub, name):
        d = self.newdir(name + "_data")
        src = os.path.join(self.data, sub)
        for f in os.listdir(src):
            p = os.path.join(src, f)
            if os.path.isfile(p):
                shutil.copy(p, d)
        return d

    def checker_copy(self, branch, rel_files, name, patches=()):
        """Copy checker file(s) to a fresh dir, applying (file, old, new) or
        (file, old, new, "optional") patches.  `old` must occur at most once.
        A missing optional target is skipped (e.g. a hash pin that the
        original checker does not have); a missing required target marks the
        test N/A, because the check it targets is absent."""
        d = self.newdir(name + "_code")
        root = self.package if self.package else os.path.join(self.clean, branch)
        for rel in rel_files:
            shutil.copy(os.path.join(root, rel), d)
        for patch in patches:
            fname, old, new = patch[:3]
            optional = len(patch) > 3 and patch[3] == "optional"
            p = os.path.join(d, fname)
            s = open(p, encoding="utf-8").read()
            n = s.count(old)
            assert n <= 1, (fname, old[:60], n)
            if n == 0:
                if not optional:
                    self.missing.setdefault(d, []).append("%s: %r" % (fname, old[:50]))
                continue
            open(p, "w", encoding="utf-8").write(s.replace(old, new))
        return d


def run(cmd, cwd, timeout=1800):
    t0 = time.perf_counter()
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        out = p.stdout + p.stderr
        code = p.returncode
    except subprocess.TimeoutExpired:
        out, code = "TIMEOUT", -999
    return code, out, time.perf_counter() - t0


# ---------------------------------------------------------------- helpers
def kron_R(strs):
    """R(f) for C_1d, binary64 reading (used only to choose mutations)."""
    vals = [Fraction(float(s)) for s in strs]
    D = 1
    for q in vals:
        D = D * q.denominator // __import__("math").gcd(D, q.denominator)
    a = [int(q * D) for q in vals]
    n = len(a)
    c = [0] * (2 * n - 1)
    for i in range(n):
        for j in range(n):
            c[i + j] += a[i] * a[j]
    S = sum(a)
    return Fraction(2 * n * max(abs(x) for x in c), S * S)


def find_sunflower_maker(fam, npts, rng, keep_status=None, allowed_mask=None, avoid=None):
    """Find (A, B, C) with A, B in fam, C not in fam, {A, B, C} a 3-sunflower
    (C n (A u B) = A n B) and fam + C still Sperner.  If keep_status=(u, v,
    su, sv) the new set must have those port statuses.  allowed_mask
    restricts C's points."""
    full = (1 << npts) - 1
    allowed = full if allowed_mask is None else allowed_mask
    famset = set(fam)
    pairs = list(itertools.combinations(range(len(fam)), 2))
    rng.shuffle(pairs)
    for i, j in pairs[:200000]:
        A, B = fam[i], fam[j]
        if avoid and (A in avoid or B in avoid):
            continue
        K = A & B
        if K & ~allowed:
            continue
        free = allowed & ~(A | B)
        bits = [b for b in range(npts) if (free >> b) & 1]
        for _ in range(30):
            X = 0
            for b in bits:
                if rng.random() < 0.5:
                    X |= 1 << b
            C = K | X
            if C in famset or C == 0:
                continue
            if keep_status:
                u, v, su, sv = keep_status
                if ((C >> u) & 1, (C >> v) & 1) != (su, sv):
                    continue
            if any((C & T) == C or (C & T) == T for T in fam if T not in (avoid or ())):
                continue
            return A, B, C
    return None


# ---------------------------------------------------------------- tests
def tests_1d(ctx):
    T = []
    files = ["verification/1d/check_c1d.py"]
    base = ctx.data_1d = os.path.join(ctx.data, "1d")
    steps_p = os.path.join(base, "steps_construction.json")
    aer_p = os.path.join(base, "problem_4_signed_autoconvolution_bounds.py.txt")
    common = ["--quick", "--random-points", "20"]

    def mutate_steps(dirname, delta=1e-3, idx=0):
        d = ctx.copy_data("1d", dirname)
        obj = json.loads(open(steps_p).read())
        obj["values"][idx] = obj["values"][idx] + delta
        open(os.path.join(d, "steps_construction.json"), "w").write(json.dumps(obj))
        return d, sha_file(os.path.join(d, "steps_construction.json")), obj

    # d1: value changed, pin intact
    d, newsha, obj = mutate_steps("d1")
    code = ctx.checker_copy("v1d", files, "d1")
    T.append(dict(id="1d-1", what="STEPS2026: v[0] += 0.001, hash pin intact",
                  cmd=PY + ["check_c1d.py", "--data", d] + common, cwd=code,
                  expect="fail", need=["MISMATCH", "PROBLEM"]))
    # d2: same, pin updated -> fraction mismatch and bound exceeded
    R2 = kron_R([repr(x) for x in obj["values"]])
    assert R2 > Fraction("1.460217284022874")
    code = ctx.checker_copy("v1d", files, "d2", patches=[(
        "check_c1d.py", '"3dd39fae744555179b0356b84e752db724e892bd23dda51403976edfb5b3a28c"',
        '"%s"' % newsha)])
    T.append(dict(id="1d-2", what="STEPS2026: v[0] += 0.001, pin updated (R rises to %.15f)" % float(R2),
                  cmd=PY + ["check_c1d.py", "--data", d] + common, cwd=code, expect="fail",
                  need=["equals the exact fraction recorded on the page: False",
                        r"re:C_1d <= 1\.460217284022874\s+NOT CONFIRMED"]))
    # d3: AER (no recorded fraction): one literal changed so that R > bound; pin updated
    d = ctx.copy_data("1d", "d3")
    src = open(aer_p, encoding="utf-8").read()
    m = re.search(r"STEP_FUNCTION_C4_PRIME_N600\s*=\s*\[\s*([-0-9.eE]+)", src)
    lit = m.group(1)
    newlit = repr(float(lit) + 1e-3)
    src2 = src[:m.start(1)] + newlit + src[m.end(1):]
    open(os.path.join(d, os.path.basename(aer_p)), "w", encoding="utf-8").write(src2)
    newsha = sha_bytes(src2.encode("utf-8"))
    code = ctx.checker_copy("v1d", files, "d3", patches=[(
        "check_c1d.py", '"1a290ad1074c10a871adaf2bd44402af56be8cf151f1f775a8fc37c7bdff54b2"',
        '"%s"' % newsha)])
    T.append(dict(id="1d-3", what="AER2026 (no recorded fraction): first literal %s -> %s, pin updated"
                  % (lit, newlit), cmd=PY + ["check_c1d.py", "--data", d] + common, cwd=code,
                  expect="fail", need=[r"re:C_1d <= 1\.459989046905384\s+NOT CONFIRMED"]))
    # d4: claimed bounds nudged just below the exact values (all three certificates)
    code = ctx.checker_copy("v1d", files, "d4", patches=[
        ("check_c1d.py", 'bound="1.460217284022874",', 'bound="1.460217284022873",'),
        ("check_c1d.py", 'bound="1.459989046905384",', 'bound="1.4599890469053831",'),
        ("check_c1d.py", 'bound="1.4630715826075594",', 'bound="1.4630715826075592",')])
    T.append(dict(id="1d-4", what="all three claimed bounds nudged just below the exact R of both readings "
                  "(CERT2026: 1.4630715826075592; its decimal reading gives R = 1.46307158260755929963...)",
                  cmd=PY + ["check_c1d.py", "--data", base] + common, cwd=code, expect="fail",
                  need=[r"re:C_1d <= 1\.460217284022873\s+NOT CONFIRMED",
                        r"re:C_1d <= 1\.4599890469053831\s+NOT CONFIRMED",
                        r"re:C_1d <= 1\.4630715826075592\s+NOT CONFIRMED"]))
    # d5: recorded page fraction off by one in the numerator
    code = ctx.checker_copy("v1d", files, "d5", patches=[(
        "check_c1d.py", "fraction=(698746209786798359455483373677229695641600,",
        "fraction=(698746209786798359455483373677229695641601,")])
    T.append(dict(id="1d-5", what="STEPS2026: recorded page fraction numerator + 1",
                  cmd=PY + ["check_c1d.py", "--data", base] + common, cwd=code, expect="fail",
                  need=["equals the exact fraction recorded on the page: False", "PROBLEM"]))
    # d6: one cell dropped (599 values), pin updated
    d = ctx.copy_data("1d", "d6")
    obj = json.loads(open(steps_p).read())
    obj["values"] = obj["values"][:-1]
    open(os.path.join(d, "steps_construction.json"), "w").write(json.dumps(obj))
    code = ctx.checker_copy("v1d", files, "d6", patches=[(
        "check_c1d.py", '"3dd39fae744555179b0356b84e752db724e892bd23dda51403976edfb5b3a28c"',
        '"%s"' % sha_file(os.path.join(d, "steps_construction.json")))])
    T.append(dict(id="1d-6", what="STEPS2026: last cell dropped (599 values), pin updated",
                  cmd=PY + ["check_c1d.py", "--data", d] + common, cwd=code, expect="fail",
                  need=["PROBLEM"]))
    # d7, d8: python-flint unavailable (python3 -I -S): must stop, never skip check B
    T.append(dict(id="1d-7", what="python-flint unavailable (python3 -I -S), full run: must stop, not skip check B",
                  cmd=PY_NOSITE + ["check_c1d.py", "--data", base] + common,
                  cwd=ctx.checker_copy("v1d", files, "d7"), expect="fail", exit_expected=2,
                  need=["python-flint is not importable"], nosite=True))
    T.append(dict(id="1d-8", what="python-flint unavailable (python3 -I -S), --selftest: must stop, not skip",
                  cmd=PY_NOSITE + ["check_c1d.py", "--selftest"],
                  cwd=ctx.checker_copy("v1d", files, "d8"), expect="fail", exit_expected=2,
                  need=["python-flint is not importable"], nosite=True))
    return T


def tests_1c(ctx):
    T = []
    files = ["verification/1c/check_c1c.py"]
    base = os.path.join(ctx.data, "1c")
    kos = os.path.join(base, "K24576_0.4103333.json")
    PIN = '"963cb7273062e7360fdfa460bb19c1cf37729364b8f708b09580b6655b783c9e"'
    common = ["--knots", "40", "--interior", "20"]

    def mut(name, fn):
        d = ctx.copy_data("1c", name)
        obj = json.loads(open(kos).read())
        fn(obj)
        p = os.path.join(d, "K24576_0.4103333.json")
        open(p, "w").write(json.dumps(obj))
        return d, sha_file(p)

    def inc(i, by):
        def f(o):
            o["weights_int"][i] += by
        return f
    d, s = mut("c1", inc(4, 1))
    T.append(dict(id="1c-1", what="Kos2026: w[4] += 1, pin intact",
                  cmd=PY + ["check_c1c.py", "--data", d] + common,
                  cwd=ctx.checker_copy("v1c", files, "c1"), expect="fail", need=["MISMATCH", "PROBLEM"]))
    code = ctx.checker_copy("v1c", files, "c2", patches=[("check_c1c.py", PIN, '"%s"' % s)])
    T.append(dict(id="1c-2", what="Kos2026: w[4] += 1, pin updated (tiny change)",
                  cmd=PY + ["check_c1c.py", "--data", d] + common, cwd=code, expect="fail",
                  need=["equals the exact fraction recorded on the page: False", "PROBLEM"]))
    d, s = mut("c3", inc(5000, 10**12))
    code = ctx.checker_copy("v1c", files, "c3", patches=[("check_c1c.py", PIN, '"%s"' % s)])
    T.append(dict(id="1c-3", what="Kos2026: w[5000] += 10^12 (mass added where lag 21264 cannot see it), pin updated",
                  cmd=PY + ["check_c1c.py", "--data", d] + common, cwd=code, expect="fail",
                  need=[r"re:C_1c >= 0\.4103333\s+NOT CONFIRMED"]))
    code = ctx.checker_copy("v1c", files, "c4", patches=[("check_c1c.py", 'bound="0.4103333",',
                                                          'bound="0.41033336",')])
    T.append(dict(id="1c-4", what="claimed bound nudged to 0.41033336 (> exact 0.4103333527...)",
                  cmd=PY + ["check_c1c.py", "--data", base] + common, cwd=code, expect="fail",
                  need=[r"re:C_1c >= 0\.41033336\s+NOT CONFIRMED"]))

    def neg(o):
        o["weights_int"][10] = -o["weights_int"][10]
    d, s = mut("c5", neg)
    code = ctx.checker_copy("v1c", files, "c5", patches=[("check_c1c.py", PIN, '"%s"' % s)])
    T.append(dict(id="1c-5", what="Kos2026: one weight made negative, pin updated",
                  cmd=PY + ["check_c1c.py", "--data", d] + common, cwd=code, expect="fail",
                  need=["negative weight"]))

    def flt(o):
        o["weights_int"][10] = o["weights_int"][10] + 0.5
    d, s = mut("c6", flt)
    code = ctx.checker_copy("v1c", files, "c6", patches=[("check_c1c.py", PIN, '"%s"' % s)])
    T.append(dict(id="1c-6", what="Kos2026: one weight made non-integer, pin updated",
                  cmd=PY + ["check_c1c.py", "--data", d] + common, cwd=code, expect="fail",
                  need=["JSON integers"]))

    def kchg(o):
        o["K"] = 24575
    d, s = mut("c7", kchg)
    code = ctx.checker_copy("v1c", files, "c7", patches=[("check_c1c.py", PIN, '"%s"' % s)])
    T.append(dict(id="1c-7", what="Kos2026: K changed 24576 -> 24575, pin updated",
                  cmd=PY + ["check_c1c.py", "--data", d] + common, cwd=code, expect="fail",
                  need=["SHAPE MISMATCH", "PROBLEM"]))
    code = ctx.checker_copy("v1c", files, "c8", patches=[("check_c1c.py", "argmin=21264,", "argmin=21265,")])
    T.append(dict(id="1c-8", what="recorded argmin changed 21264 -> 21265 (the minimiser must be enforced)",
                  cmd=PY + ["check_c1c.py", "--data", base] + common, cwd=code, expect="fail",
                  need=[r"re:argmin matches the page \(k = 21265[^)]*\): False", "PROBLEM"]))
    T.append(dict(id="1c-9", what="python-flint unavailable (python3 -I -S), full run: must stop, not skip check B",
                  cmd=PY_NOSITE + ["check_c1c.py", "--data", base] + common,
                  cwd=ctx.checker_copy("v1c", files, "c9"), expect="fail", exit_expected=2,
                  need=["python-flint is not importable"], nosite=True))
    T.append(dict(id="1c-10", what="python-flint unavailable (python3 -I -S), --selftest: must stop, not skip",
                  cmd=PY_NOSITE + ["check_c1c.py", "--selftest"],
                  cwd=ctx.checker_copy("v1c", files, "c10"), expect="fail", exit_expected=2,
                  need=["python-flint is not importable"], nosite=True))
    return T


def tests_70a(ctx):
    T = []
    files = ["verification/70a/check_c70.py"]
    cert = os.path.join(ctx.data, "70a", "c70-certificate", "certificates", "c70_candidate.json")
    for tid, old, new, what, extra in (
            ("70a-1", 'CLAIM = Fraction("1.20194336")', 'CLAIM = Fraction("1.2019433685")',
             "claim nudged to 1.2019433685 (> R = 1.20194336844...)", []),
            ("70a-2", 'CLAIM = Fraction("1.20194336")', 'CLAIM = Fraction("1.20194336847")',
             "claim set to the limit's printed value 1.20194336847 (the finite R is below it)", []),
            ("70a-3", "K = 367879441172", "K = 300000000000",
             "retained term k = 3*10^11 instead of 367879441172 (R = 1.19793...)", [])):
        code = ctx.checker_copy("v70a", files, tid, patches=[("check_c70.py", old, new)])
        T.append(dict(id=tid, what=what, cmd=PY + ["check_c70.py", "--skip-baseline"] + extra,
                      cwd=code, expect="fail", need=["NOT CONFIRMED"]))
    for tid, key, val, what in (("70a-4", "n", 10**12 + 2, "certificate JSON: n changed"),
                                ("70a-5", "normalized_side", "632120558830/367879441172",
                                 "certificate JSON: normalized side changed")):
        d = ctx.newdir(tid + "_data")
        obj = json.loads(open(cert).read())
        obj[key] = val
        p = os.path.join(d, "c70_candidate.json")
        open(p, "w").write(json.dumps(obj))
        T.append(dict(id=tid, what=what, cmd=PY + ["check_c70.py", "--skip-baseline", "--json", p],
                      cwd=ctx.checker_copy("v70a", files, tid), expect="fail",
                      need=["certificate parameters match the constant page: False", "NOT CONFIRMED"]))
    T.append(dict(id="70a-6", what="python-flint and mpmath unavailable (python3 -I -S): must stop",
                  cmd=PY_NOSITE + ["check_c70.py", "--skip-baseline", "--json", cert],
                  cwd=ctx.checker_copy("v70a", files, "70a-6"), expect="fail",
                  need=["ModuleNotFoundError"], nosite=True))
    return T


def tests_16a(ctx):
    T = []
    files = ["verification/16a/check_c16_lower.py"]
    cert = os.path.join(ctx.data, "16a", "c16-bgw-certificates", "lower_certificate.json")
    code = ctx.checker_copy("v16a", files, "s1", patches=[(
        "check_c16_lower.py", 'CLAIM = Fraction("2.1562247706")', 'CLAIM = Fraction("2.1562247707")')])
    T.append(dict(id="16a-1", what="claim nudged to 2.1562247707 (> L_trial = 2.15622477064...)",
                  cmd=PY + ["check_c16_lower.py", "--skip-calibration"], cwd=code, expect="fail",
                  need=["NOT CONFIRMED"]))
    T.append(dict(id="16a-2", what="trial function cut off at |k| <= 1000 instead of 4000 (no JSON)",
                  cmd=PY + ["check_c16_lower.py", "--skip-calibration", "--R", "1000"],
                  cwd=ctx.checker_copy("v16a", files, "s2"), expect="fail", need=["NOT CONFIRMED"]))
    code = ctx.checker_copy("v16a", files, "s3", patches=[(
        "check_c16_lower.py", "        r[a * a] += 1                                    # b = 0",
        "        r[a * a] += 0 if a == 7 else 1                   # b = 0 (MUTATED)")])
    T.append(dict(id="16a-3", what="r2 table corrupted (code mutation): lattice points (+-7, 0) dropped",
                  cmd=PY + ["check_c16_lower.py", "--skip-calibration"], cwd=code, expect="fail",
                  need=["Gauss count False", "NOT CONFIRMED"]))
    d = ctx.newdir("s4_data")
    obj = json.loads(open(cert).read())
    obj["mu"] = [1222, 10000]
    p = os.path.join(d, "lower_certificate.json")
    open(p, "w").write(json.dumps(obj))
    T.append(dict(id="16a-4", what="certificate JSON: mu changed to 1222/10000",
                  cmd=PY + ["check_c16_lower.py", "--skip-calibration", "--json", p],
                  cwd=ctx.checker_copy("v16a", files, "s4"), expect="fail",
                  need=["certificate R and mu match the page/README: False", "NOT CONFIRMED"]))
    T.append(dict(id="16a-5", what="numpy and python-flint unavailable (python3 -I -S): must stop",
                  cmd=PY_NOSITE + ["check_c16_lower.py", "--skip-calibration"],
                  cwd=ctx.checker_copy("v16a", files, "s5"), expect="fail",
                  need=["ModuleNotFoundError"], nosite=True))
    return T


def tests_49a(ctx, rng):
    T = []
    files = ["verification/49a/check_c49_cla2026.py", "verification/49a/check_c49_syl2026.py",
             "verification/49a/check_c49_irsi2026.py"]
    # ---- Cla2026 (families rebuilt from the page inside the checker)
    T.append(dict(id="49a-1", what="Cla2026: F loses one chair complement (74 sets)",
                  cmd=PY + ["check_c49_cla2026.py"], expect="fail", need=["NOT CONFIRMED"],
                  cwd=ctx.checker_copy("v49a", files, "l1", patches=[(
                      "check_c49_cla2026.py", "    comps = {full ^ ch for ch in chairs}\n",
                      "    comps = set(sorted(full ^ ch for ch in chairs)[1:])  # MUTATED\n")])))
    # a set C making a sunflower with two members of F while keeping Sperner
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "c49i", os.path.join(os.path.dirname(os.path.abspath(__file__)), "c49_independent.py"))
    c49i = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(c49i)
    F, _ = c49i.build_F()          # the auditor's own rebuild, only to choose C
    A, B, C = find_sunflower_maker(F, 10, rng)
    T.append(dict(id="49a-2", what="Cla2026: F plus one set C=%s forming a sunflower with %s, %s "
                  "(Sperner kept)" % (bin(C), bin(A), bin(B)),
                  cmd=PY + ["check_c49_cla2026.py"], expect="fail", need=["NOT CONFIRMED"],
                  cwd=ctx.checker_copy("v49a", files, "l2", patches=[(
                      "check_c49_cla2026.py", "    F = stars | k23 | comps\n",
                      "    F = stars | k23 | comps | {%d}  # MUTATED\n" % C)])))
    T.append(dict(id="49a-3", what="Cla2026: claim 1.5664286 nudged to 1.5664287 (> rho^(1/8) = 1.56642866...)",
                  cmd=PY + ["check_c49_cla2026.py"], expect="fail", need=["NOT CONFIRMED"],
                  cwd=ctx.checker_copy("v49a", files, "l3", patches=[(
                      "check_c49_cla2026.py", "arb(15664286) / 10**7", "arb(15664287) / 10**7")])))
    T.append(dict(id="49a-4", what="Cla2026 (code mutation, not data): transfer matrix built with the same-status rule "
                  "T[a][a'] = N_{a,a'} (wrong for XOR chains)",
                  cmd=PY + ["check_c49_cla2026.py"], expect="fail", need=["NOT CONFIRMED"],
                  cwd=ctx.checker_copy("v49a", files, "l4", patches=[(
                      "check_c49_cla2026.py", "    return [[N[(a, 1 - ap)] for ap in (0, 1)] for a in (0, 1)]",
                      "    return [[N[(a, ap)] for ap in (0, 1)] for a in (0, 1)]  # MUTATED")]),
                  note="caught by the page cross-checks (matrices as printed, trace/det, 20+2sqrt(66), "
                       "1042+2sqrt(261207), printed digits), which are now enforced"))
    T.append(dict(id="49a-16", what="Cla2026: recorded determinant of the page's product matrix changed "
                  "(641 -> 642 in 980*1104 - 1624*641)",
                  cmd=PY + ["check_c49_cla2026.py"], expect="fail", need=["NOT CONFIRMED"],
                  cwd=ctx.checker_copy("v49a", files, "l16", patches=[(
                      "check_c49_cla2026.py", "980 * 1104 - 1624 * 641", "980 * 1104 - 1624 * 642")])))
    # ---- Syl2026
    syl = os.path.join(ctx.data, "49a", "syl")
    PIN_BP = '"2a72385704b8203269cda4f4b0dfdabc74d5adb8f4a2bc1dac1f570cb96b5cec"'
    PIN_B = '"340cef5e71124ed624425abf81e9621839406cbf44b3fd242594d8edcb7d37af"'

    def read_lines(p):
        return open(p, encoding="utf-8").read().splitlines()

    def mask(line):
        return sum(1 << int(t) for t in line.split())
    bl = read_lines(os.path.join(syl, "Bprime.txt"))
    Bp = [mask(x) for x in bl if x.strip() and not x.startswith("#")]
    Bset = {mask(x) for x in read_lines(os.path.join(syl, "B.txt")) if x.strip() and not x.startswith("#")}
    extras = [S for S in Bp if S not in Bset]
    Hmask = sum(1 << q for q in range(9, 19))
    # replace one extra by C with the same statuses at points 0, 1 and no H-point
    found = None
    for T0 in extras:
        rest = [S for S in Bp if S != T0]
        r = find_sunflower_maker(rest, 19, rng, keep_status=(0, 1, T0 & 1, (T0 >> 1) & 1),
                                 allowed_mask=((1 << 19) - 1) & ~Hmask)
        if r:
            found = (T0, r)
            break
    assert found, "no sunflower-making replacement found"
    T0, (A, B, C) = found

    def fam_line(S):
        return " ".join(str(q) for q in range(19) if (S >> q) & 1)
    d = ctx.copy_data("49a/syl", "y1")
    newlines = [fam_line(C) if (x.strip() and not x.startswith("#") and mask(x) == T0) else x for x in bl]
    open(os.path.join(d, "Bprime.txt"), "w", encoding="utf-8").write("\n".join(newlines) + "\n")
    newsha = sha_file(os.path.join(d, "Bprime.txt"))
    T.append(dict(id="49a-5", what="Syl2026 B': one extra set replaced (same port statuses, no H-point) "
                  "by a set that closes a sunflower; pin intact",
                  cmd=PY + ["check_c49_syl2026.py", "--data", d], cwd=ctx.checker_copy("v49a", files, "y1"),
                  expect="fail", need=["MISMATCH", "NOT CONFIRMED"]))
    T.append(dict(id="49a-6", what="Syl2026 B': same replacement, pin updated",
                  cmd=PY + ["check_c49_syl2026.py", "--data", d], expect="fail",
                  need=["FOUND", "NOT CONFIRMED"],
                  cwd=ctx.checker_copy("v49a", files, "y2", patches=[(
                      "check_c49_syl2026.py", PIN_BP, '"%s"' % newsha)])))
    d = ctx.copy_data("49a/syl", "y3")
    keep = [x for x in bl if not (x.strip() and not x.startswith("#") and mask(x) == extras[0])]
    open(os.path.join(d, "Bprime.txt"), "w", encoding="utf-8").write("\n".join(keep) + "\n")
    T.append(dict(id="49a-7", what="Syl2026 B': one of the 15 extra sets deleted (4363 sets), pin updated",
                  cmd=PY + ["check_c49_syl2026.py", "--data", d], expect="fail", need=["NOT CONFIRMED"],
                  cwd=ctx.checker_copy("v49a", files, "y3", patches=[(
                      "check_c49_syl2026.py", PIN_BP, '"%s"' % sha_file(os.path.join(d, "Bprime.txt")))])))
    T.append(dict(id="49a-8", what="Syl2026: claim 1.5678015 nudged to 1.5678016",
                  cmd=PY + ["check_c49_syl2026.py", "--data", syl], expect="fail", need=["NOT CONFIRMED"],
                  cwd=ctx.checker_copy("v49a", files, "y4", patches=[(
                      "check_c49_syl2026.py", "arb(15678015) / 10**7", "arb(15678016) / 10**7")])))
    T.append(dict(id="49a-9", what="Syl2026 row 79: recorded N00 changed by +1",
                  cmd=PY + ["check_c49_syl2026.py", "--data", syl], expect="fail", need=["NOT CONFIRMED"],
                  cwd=ctx.checker_copy("v49a", files, "y5", patches=[(
                      "check_c49_syl2026.py", "page = {(0, 0): 148811965456,", "page = {(0, 0): 148811965457,")])))
    T.append(dict(id="49a-17", what="Syl2026 row 80 (code mutation): B' transfer matrix built with the same-status "
                  "rule (rho rises to about 2262; the bound would still pass)",
                  cmd=PY + ["check_c49_syl2026.py", "--data", syl], expect="fail", need=["NOT CONFIRMED"],
                  cwd=ctx.checker_copy("v49a", files, "y6", patches=[(
                      "check_c49_syl2026.py", "    rho, tr, det = perron(Np)",
                      "    rho, tr, det = perron({(0, 1): Np[(0, 0)], (1, 0): Np[(1, 1)], "
                      "(0, 0): Np[(0, 1)], (1, 1): Np[(1, 0)]})  # MUTATED")])))
    T.append(dict(id="49a-18", what="Syl2026 row 79: recorded gadget count changed (152351 -> 152352)",
                  cmd=PY + ["check_c49_syl2026.py", "--data", syl], expect="fail", need=["NOT CONFIRMED"],
                  cwd=ctx.checker_copy("v49a", files, "y7", patches=[(
                      "check_c49_syl2026.py", "(250659, (98308, 152351))", "(250659, (98308, 152352))")])))
    T.append(dict(id="49a-19", what="Syl2026 row 80 (code mutation): H-part mask widened to all 19 points, so "
                  "'the 15 extra sets avoid H' must fail",
                  cmd=PY + ["check_c49_syl2026.py", "--data", syl], expect="fail", need=["NOT CONFIRMED"],
                  cwd=ctx.checker_copy("v49a", files, "y8", patches=[(
                      "check_c49_syl2026.py", "Hmask = sum(1 << q for q in range(9, 19))",
                      "Hmask = sum(1 << q for q in range(0, 19))  # MUTATED")])))
    # ---- IRSI2026
    irsi = os.path.join(ctx.data, "49a", "irsi")
    v10 = json.loads(open(os.path.join(irsi, "v10.json")).read())
    fam = v10["bases"]["B"]["sets"]
    u, v = v10["word"][0]["u"], v10["word"][0]["v"]
    r = None
    for T0 in rng.sample(fam, 50):
        rest = [S for S in fam if S != T0]
        r = find_sunflower_maker(rest, 20, rng, keep_status=(u, v, (T0 >> u) & 1, (T0 >> v) & 1))
        if r:
            break
    assert r
    A, B, C = r

    PIN_V10 = '"c30a74fed64616c5c6980fae91f94ae5899fed6a4cb338b537480ee9517d715b"'

    def irsi_mut(name, fn, what, need, patches=()):
        d = ctx.copy_data("49a/irsi", name)
        obj = json.loads(open(os.path.join(irsi, "v10.json")).read())
        fn(obj)
        p = os.path.join(d, "v10.json")
        open(p, "w").write(json.dumps(obj))
        # the replay pins the v1.0 bytes (the page records no hash): update the
        # pin in the copy so that the mathematical path is exercised.  The
        # original checker has no pin, hence "optional".
        pin = ("check_c49_irsi2026.py", PIN_V10, '"%s"' % sha_file(p), "optional")
        T.append(dict(id=name, what=what + ", pin updated", cmd=PY + ["check_c49_irsi2026.py", "--data", d],
                      cwd=ctx.checker_copy("v49a", files, name, patches=tuple(patches) + (pin,)),
                      expect="fail", need=need))

    def repl(o):
        s = o["bases"]["B"]["sets"]
        s[s.index(T0)] = C
    irsi_mut("49a-10", repl, "IRSI v1.0 (no hash on the page): one set replaced, same port statuses, "
             "closing a sunflower (Sperner kept)", ["FOUND", "NOT ALL CONFIRMED"])

    def dup(o):
        s = o["bases"]["B"]["sets"]
        s.append(s[0])
    irsi_mut("49a-11", dup, "IRSI v1.0: one set duplicated", ["distinct: False", "NOT ALL CONFIRMED"])

    def sup(o):
        s = o["bases"]["B"]["sets"]
        x = s[0]
        y = x | (1 << next(q for q in range(20) if not (x >> q) & 1))
        s[1] = y
    irsi_mut("49a-12", sup, "IRSI v1.0: a set replaced by a strict superset of another member",
             ["Sperner: False", "NOT ALL CONFIRMED"])

    def port(o):
        o["word"][0]["u"] = 17
    irsi_mut("49a-13", port, "IRSI v1.0: port u changed 18 -> 17",
             ["[[1884, 1360], [1081, 1802]]: False", "NOT ALL CONFIRMED"])
    irsi_mut("49a-14", lambda o: None, "IRSI v1.0: claim 1.5617847 nudged to 1.5617848",
             ["NOT ALL CONFIRMED"], patches=[("check_c49_irsi2026.py", '"1.5617847", [[1884',
                                              '"1.5617848", [[1884')])
    d = ctx.copy_data("49a/irsi", "49a-15")
    obj = json.loads(open(os.path.join(irsi, "v12.json")).read())
    obj["bases"]["B"]["sets"] = obj["bases"]["B"]["sets"][:-1]
    open(os.path.join(d, "v12.json"), "w").write(json.dumps(obj))
    T.append(dict(id="49a-15", what="IRSI v1.2 (pinned): last set removed, pin intact",
                  cmd=PY + ["check_c49_irsi2026.py", "--data", d], cwd=ctx.checker_copy("v49a", files, "49a-15"),
                  expect="fail", need=["MISMATCH", "NOT ALL CONFIRMED"]))
    T.append(dict(id="49a-20", what="IRSI v1.1: recorded characteristic polynomial changed (det 1969416 -> 1969417)",
                  cmd=PY + ["check_c49_irsi2026.py", "--data", irsi], expect="fail", need=["NOT ALL CONFIRMED"],
                  cwd=ctx.checker_copy("v49a", files, "49a-20", patches=[(
                      "check_c49_irsi2026.py", '"v11_s17.json": (3710, 1969416)', '"v11_s17.json": (3710, 1969417)')])))
    T.append(dict(id="49a-21", what="IRSI (code mutation): trace and determinant taken with the same-status rule "
                  "(rho rises; the bounds would still pass)",
                  cmd=PY + ["check_c49_irsi2026.py", "--data", irsi], expect="fail", need=["NOT ALL CONFIRMED"],
                  cwd=ctx.checker_copy("v49a", files, "49a-21", patches=[(
                      "check_c49_irsi2026.py",
                      "        tr = N[(0, 1)] + N[(1, 0)]\n        det = N[(0, 1)] * N[(1, 0)] - N[(0, 0)] * N[(1, 1)]",
                      "        tr = N[(0, 0)] + N[(1, 1)]  # MUTATED\n"
                      "        det = N[(0, 0)] * N[(1, 1)] - N[(0, 1)] * N[(1, 0)]  # MUTATED")])))
    d = ctx.copy_data("49a/irsi", "49a-22")
    obj = json.loads(open(os.path.join(irsi, "v10.json")).read())
    p = os.path.join(d, "v10.json")
    open(p, "w").write(json.dumps(obj, indent=2))   # same sets, different bytes
    assert sha_file(p) != sha_file(os.path.join(irsi, "v10.json"))
    T.append(dict(id="49a-22", what="IRSI v1.0 re-serialised (same content, different bytes), pin intact: "
                  "the replay must check the bytes it cites",
                  cmd=PY + ["check_c49_irsi2026.py", "--data", d], cwd=ctx.checker_copy("v49a", files, "49a-22"),
                  expect="fail", need=["MISMATCH", "NOT ALL CONFIRMED"]))
    T.append(dict(id="49a-23", what="python-flint and numpy unavailable (python3 -I -S): Syl2026 must stop",
                  cmd=PY_NOSITE + ["check_c49_syl2026.py", "--data", syl],
                  cwd=ctx.checker_copy("v49a", files, "49a-23"), expect="fail",
                  need=["ModuleNotFoundError"], nosite=True))
    return T


def evaluate(t):
    if t.get("na"):
        return dict(t, code="-", secs=0.0, ok=False, markers=False,
                    note=t["na"], tail="(not run: %s)" % t["na"])
    code, out, dt = run(t["cmd"], t["cwd"])
    failed = code != 0
    markers = all((re.search(s[3:], out) is not None) if s.startswith("re:") else (s in out)
                  for s in t["need"])
    if t["expect"] == "fail":
        ok = failed and markers and (t.get("exit_expected") is None or code == t["exit_expected"])
    else:
        ok = (not failed) and markers
    return dict(t, code=code, secs=round(dt, 1), ok=ok, markers=markers,
                tail="\n".join(out.strip().splitlines()[-4:]))


def main():
    ap = argparse.ArgumentParser()
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--package", help="checkout of replay/package (code under test)")
    src.add_argument("--clean", help="dir with v1d v1c v70a v16a v49a, one tree per constant")
    ap.add_argument("--data", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--only", default="1d,1c,70a,16a,49a")
    ap.add_argument("-j", type=int, default=3)
    ap.add_argument("--json-out")
    args = ap.parse_args()
    ctx = Ctx(os.path.abspath(args.clean) if args.clean else None, os.path.abspath(args.data),
              os.path.abspath(args.work), os.path.abspath(args.package) if args.package else None)
    os.makedirs(ctx.work, exist_ok=True)
    rng = random.Random(2026)
    tests = []
    only = args.only.split(",")
    if "1d" in only:
        tests += tests_1d(ctx)
    if "1c" in only:
        tests += tests_1c(ctx)
    if "70a" in only:
        tests += tests_70a(ctx)
    if "16a" in only:
        tests += tests_16a(ctx)
    if "49a" in only:
        tests += tests_49a(ctx, rng)
    # a missing python-flint can only be simulated if -S really hides it
    hidden = subprocess.run(PY_NOSITE + ["-c", "import flint"], capture_output=True).returncode != 0
    for t in tests:
        if t["cwd"] in ctx.missing:
            t["na"] = "N/A: check absent (patch target not found: %s)" % "; ".join(ctx.missing[t["cwd"]])
        elif t.get("nosite") and not hidden:
            t["na"] = "N/A: python-flint is importable even under python3 -I -S here"
    print("code under test: %s" % (ctx.package or ctx.clean), flush=True)
    print("running %d mutation tests with %d workers" % (len(tests), args.j), flush=True)
    with cf.ThreadPoolExecutor(max_workers=args.j) as ex:
        results = list(ex.map(evaluate, tests))
    print("\n| id | mutation | expected | exit | checker behaved correctly |")
    print("| --- | --- | --- | --- | --- |")
    for r in results:
        verdict = "yes" if r["ok"] else "**NO**"
        if r.get("note"):
            verdict += " (%s)" % r["note"]
        exp = r["expect"] + (" (exit %d)" % r["exit_expected"] if r.get("exit_expected") else "")
        print("| %s | %s | %s | %s | %s |" % (r["id"], r["what"].replace("|", "\\|"), exp, r["code"], verdict))
    bad = [r for r in results if not r["ok"]]
    for r in results:
        print("\n--- %s (exit %s, %.0fs, markers found: %s)\n%s" % (r["id"], r["code"], r["secs"],
                                                                r["markers"], r["tail"]))
    if args.json_out:
        json.dump([{k: v for k, v in r.items() if k != "cmd"} for r in results],
                  open(args.json_out, "w"), indent=1)
    print("\nSUMMARY: %d of %d tests behaved as a correct checker must" % (len(results) - len(bad), len(results)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
