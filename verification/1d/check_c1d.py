#!/usr/bin/env python3
"""Independent exact checker for step-function upper bounds on C_1d.

C_1d (signed third autocorrelation constant) is the largest C with

    max_t |(f*f)(t)| >= C (int f)^2

for every real f supported on [-1/4, 1/4].  Any such f with int f != 0
therefore gives the upper bound  C_1d <= R(f) := max_t |(f*f)(t)| / (int f)^2.

This script recomputes R(f) exactly (rational arithmetic, no floating point
in any step that decides the result) for step functions with N equal cells
on [-1/4, 1/4].  It was written from the definition on the constant page and
the published data files only; it does not use or import any code from the
certificate authors.

Method (proof in README.md):
  h = 1/(2N), f = sum_i v_i 1_[-1/4 + i h, -1/4 + (i+1) h).
  f*f(t) = sum_s c_s Lambda(t + 1/2 - s h),  c_s = sum_{i+j=s} v_i v_j,
  where Lambda is the tent of height h on [0, 2h].  Hence f*f is piecewise
  linear with knots at t_m = -1/2 + m h, (f*f)(t_m) = h c_{m-1}, and
        R(f) = 2N max_s |c_s| / (sum_i v_i)^2.

Three independent evaluations are made:
  A. c_s by a direct O(N^2) loop over Python integers;
  B. c_s as the coefficients of P(x)^2 with python-flint's fmpz_poly
     (a different multiplication algorithm), if python-flint is installed;
  C. (f*f)(t) by exact integration of x -> f(x) f(t-x) over its breakpoints,
     at every knot and at sampled non-knot rationals, checking both the knot
     formula and linearity between knots.  This does not use the tent formula.

Usage:
  python3 -I check_c1d.py --data DIR [--quick]
DIR must contain the files fetched by fetch.sh.  Every input file is checked
against its pinned SHA-256 before use.  Input files are parsed as data only
(json, or Python's ast parser for a .py source file, which is never executed).
"""

import argparse
import ast
import hashlib
import json
import math
import os
import random
import sys
import time
from fractions import Fraction

# ---------------------------------------------------------------------------
# Certificates checked.  Claimed values are copied from constants/1d.md at
# commit 87b4ebb of the fork (the bound column and the stated exact fraction).
# ---------------------------------------------------------------------------
CERTS = [
    dict(
        name="STEPS2026 (600 cells)",
        row="constants/1d.md line 20",
        file="steps_construction.json",
        sha256="3dd39fae744555179b0356b84e752db724e892bd23dda51403976edfb5b3a28c",
        fmt="json",
        key="values",
        readings=("binary64", "decimal"),
        primary="binary64",  # the submitter's README: doubles read exactly
        bound="1.460217284022874",
        fraction=(698746209786798359455483373677229695641600,
                  478522078482569620433992386249161163190849),
        cells=600,
    ),
    dict(
        name="AER2026 C'_4 (600 cells)",
        row="constants/1d.md line 21",
        file="problem_4_signed_autoconvolution_bounds.py.txt",
        sha256="1a290ad1074c10a871adaf2bd44402af56be8cf151f1f775a8fc37c7bdff54b2",
        fmt="pyast",
        key="STEP_FUNCTION_C4_PRIME_N600",
        readings=("decimal", "binary64"),
        primary=None,  # the page says either reading works; both are checked
        bound="1.459989046905384",
        fraction=None,  # no exact fraction is recorded on the page
        cells=600,
    ),
    dict(
        name="CERT2026 (300 cells, registry copy)",
        row="constants/1d.md lines 19 and 23",
        file="cert300_construction.json",
        sha256="51f864ee95205f06b98923c382d23cb3dfde5f0d4208a4c591bad015e5908a0e",
        fmt="json",
        key="values",
        readings=("binary64", "decimal"),
        primary="binary64",
        bound="1.4630715826075594",  # row 23 (current, replayed by [T2026])
        # Row 19 still prints the superseded value; row 23 of the same page
        # says that value was rounded the wrong way.  Reported, not required.
        bound_info="1.463071582607559",
        fraction=(2039224160683882663565441886346340189798400,
                  1393796574908163689489385839036226787118881),
        cells=300,
    ),
]


def describe_denominator(D):
    if D & (D - 1) == 0:
        return "2^%d" % (D.bit_length() - 1)
    k, r = 0, D
    while r % 10 == 0:
        r //= 10
        k += 1
    if r == 1:
        return "10^%d" % k
    return "%d-digit integer" % len(str(D))


# ---------------------------------------------------------------------------
# Parsing (data only)
# ---------------------------------------------------------------------------
def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


def literals_from_json(text, key):
    """Return the numeric literals of the JSON array `key`, as source strings."""
    obj = json.loads(text, parse_float=str, parse_int=str)
    arr = obj[key]
    if not isinstance(arr, list) or not all(isinstance(s, str) for s in arr):
        raise ValueError("unexpected JSON structure")
    return arr, obj


def literals_from_python_source(text, varname):
    """Find `VARNAME = [ ... ]` with ast (no execution); return literal strings."""
    tree = ast.parse(text)
    found = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name) \
                and node.targets[0].id == varname:
            if found is not None:
                raise ValueError("variable assigned twice at top level")
            found = node.value
    if found is None or not isinstance(found, ast.List):
        raise ValueError("list literal not found")
    out = []
    for elt in found.elts:
        sign = ""
        if isinstance(elt, ast.UnaryOp) and isinstance(elt.op, ast.USub):
            sign, elt = "-", elt.operand
        if not (isinstance(elt, ast.Constant) and type(elt.value) in (int, float)):
            raise ValueError("non-numeric element in list")
        seg = ast.get_source_segment(text, elt)
        out.append(sign + seg.strip())
    return out


def to_exact(literals, reading):
    """Exact rationals from literal strings.

    reading == "decimal":  the decimal string itself, exactly.
    reading == "binary64": the IEEE double nearest the string (Python's
                           correctly rounded float()), then exactly.
    """
    if reading == "decimal":
        return [Fraction(s) for s in literals]
    if reading == "binary64":
        vals = []
        for s in literals:
            x = float(s)
            if not math.isfinite(x):
                raise ValueError("non-finite value")
            vals.append(Fraction(x))  # Fraction(float) is exact
        return vals
    raise ValueError(reading)


def integerize(fracs):
    """Scale by the lcm of denominators: returns (ints, D) with v_i = ints_i / D."""
    D = 1
    for q in fracs:
        D = D * q.denominator // math.gcd(D, q.denominator)
    ints = [q.numerator * (D // q.denominator) for q in fracs]
    assert all(Fraction(a, D) == q for a, q in zip(ints, fracs))
    return ints, D


# ---------------------------------------------------------------------------
# Autoconvolution coefficients
# ---------------------------------------------------------------------------
def autoconv_direct(a):
    """c_s = sum_{i+j=s} a_i a_j, s = 0..2n-2, by the direct double loop."""
    n = len(a)
    c = [0] * (2 * n - 1)
    for i in range(n):
        ai = a[i]
        if ai == 0:
            continue
        for j in range(n):
            c[i + j] += ai * a[j]
    return c


def autoconv_flint(a):
    try:
        import flint  # python-flint
    except ImportError:
        return None
    p = flint.fmpz_poly(a)
    q = p * p
    coeffs = [int(x) for x in q.coeffs()]
    coeffs += [0] * (2 * len(a) - 1 - len(coeffs))  # pad trailing zeros
    return coeffs


# ---------------------------------------------------------------------------
# Check C: direct exact integration of (f*f)(t) = int f(x) f(t - x) dx
# ---------------------------------------------------------------------------
def conv_by_integration(a, tau):
    """I(tau) = int g(u) g(tau - u) du for g = sum_i a_i 1_[i, i+1), exactly.

    Change of variables x = -1/4 + u h, t = -1/2 + tau h turns
    (f*f)(t) = int f(x) f(t - x) dx into (h / D^2) I(tau) when v_i = a_i / D
    (because t - x = -1/4 + (tau - u) h).  I(tau) is computed by brute force:
    u -> g(u) g(tau - u) is constant between consecutive points of
    {0..N} U {tau - j : j = 0..N}; it is evaluated at each midpoint.
    No use is made of the tent-function formula.
    """
    N = len(a)
    tau = Fraction(tau)
    pts = set(Fraction(i) for i in range(N + 1))
    pts |= set(tau - j for j in range(N + 1))
    pts = sorted(p for p in pts if 0 <= p <= N)
    total = Fraction(0)
    for u0, u1 in zip(pts, pts[1:]):
        mid = (u0 + u1) / 2
        i = math.floor(mid)
        j = math.floor(tau - mid)
        if 0 <= i < N and 0 <= j < N:
            total += (u1 - u0) * (a[i] * a[j])
    return total


def check_C(a, c, rng, n_random, quick):
    """Compare brute-force integration with the knot formula and linearity."""
    N = len(a)
    knot = lambda m: c[m - 1] if 1 <= m <= 2 * N - 1 else 0
    ms = list(range(0, 2 * N + 1))
    if quick:
        ms = sorted(set(rng.sample(ms, 60) + [0, 1, 2 * N - 1, 2 * N]))
    n_knots = 0
    for m in ms:
        if conv_by_integration(a, m) != knot(m):
            return False, "knot mismatch at m=%d" % m
        n_knots += 1
    n_lin = 0
    for _ in range(n_random):
        m = rng.randrange(0, 2 * N)
        theta = Fraction(rng.randrange(1, 10**6), 10**6)  # strictly inside
        expected = (1 - theta) * knot(m) + theta * knot(m + 1)
        if conv_by_integration(a, m + theta) != expected:
            return False, "non-linearity at m=%d theta=%s" % (m, theta)
        n_lin += 1
    for tau in (Fraction(-1, 3), Fraction(2 * N) + Fraction(1, 7)):  # outside
        if conv_by_integration(a, tau) != 0:
            return False, "nonzero outside [-1/2,1/2]"
    return True, "%d knots and %d interior points agree exactly" % (n_knots, n_lin)


# ---------------------------------------------------------------------------
# Reporting helpers
# ---------------------------------------------------------------------------
def decimal_digits(q, digits=25):
    """Truncated decimal expansion of a positive rational, exactly."""
    ip = q.numerator // q.denominator
    frac = q - ip
    s = str(ip) + "."
    scaled = frac * 10**digits
    s += str(scaled.numerator // scaled.denominator).rjust(digits, "0")
    return s + "..."


def evaluate(literals, reading, rng, n_random, quick, log):
    vals = to_exact(literals, reading)
    N = len(vals)
    a, D = integerize(vals)
    t0 = time.perf_counter()
    cA = autoconv_direct(a)
    tA = time.perf_counter() - t0
    t0 = time.perf_counter()
    cB = autoconv_flint(a)
    tB = time.perf_counter() - t0
    if cB is not None and cB != cA:
        raise AssertionError("direct and FLINT autoconvolutions differ")
    S = sum(a)
    if S == 0:
        raise AssertionError("int f = 0: certificate gives no bound")
    M = max(abs(x) for x in cA)
    argmax = [s for s, x in enumerate(cA) if abs(x) == M]
    R = Fraction(2 * N * M, S * S)  # D^2 cancels
    # how many knots are within relative 1e-9 of the max (equioscillation)
    near = sum(1 for x in cA if Fraction(abs(x), M) >= 1 - Fraction(1, 10**9))
    t0 = time.perf_counter()
    okC, msgC = check_C(a, cA, rng, n_random, quick)
    tC = time.perf_counter() - t0
    log("    reading=%s  N=%d  common denominator D=%s" % (
        reading, N, describe_denominator(D)))
    log("    A direct loop: %.2fs   B FLINT: %s   agree: %s" % (
        tA, "%.3fs" % tB if cB is not None else "not run",
        "yes" if cB is not None else "n/a"))
    log("    C direct integration: %s (%.1fs) -> %s" % (
        "PASS" if okC else "FAIL", tC, msgC))
    s0 = argmax[0]
    log("    max |c_s| at s=%s (knot t=-1/2+%d/%d), sign of f*f there: %s; "
        "%d knots within 1e-9 of the max" % (
            argmax, s0 + 1, 2 * N, "+" if cA[s0] > 0 else "-", near))
    log("    R(f) = %d/%d" % (R.numerator, R.denominator))
    log("         = %s" % decimal_digits(R, 25))
    return R, okC


def ratio_from_values(vals):
    a, _ = integerize([Fraction(v) for v in vals])
    c = autoconv_direct(a)
    S = sum(a)
    return Fraction(2 * len(a) * max(abs(x) for x in c), S * S)


def selftest():
    """Hand-checkable cases, then brute force vs formula on random data."""
    # f = 1 on [-1/4,1/4]: f*f is the tent of height 1/2, (int f)^2 = 1/4.
    assert ratio_from_values([1]) == 2
    assert ratio_from_values([1, 1]) == 2 and ratio_from_values([3] * 7) == 2
    # f = 2 on [-1/4,0), 1 on [0,1/4): (f*f)(0) = 1, int f = 3/4 -> 16/9.
    assert ratio_from_values([2, 1]) == Fraction(16, 9)
    # f = 1, -1/2: c = (1, -1, 1/4), max|c| = 1, S = 1/2 -> 2*2*1/(1/4) = 16.
    assert ratio_from_values([1, Fraction(-1, 2)]) == 16
    rng = random.Random(1)
    for _ in range(40):
        n = rng.randrange(1, 9)
        a = [rng.randrange(-5, 6) for _ in range(n)]
        if sum(a) == 0:
            continue
        c = autoconv_direct(a)
        cf = autoconv_flint(a)
        assert cf is None or cf == c
        # brute-force sup over a fine rational grid never exceeds knot max
        M = max(abs(x) for x in c)
        for k in range(0, 8 * 2 * n + 1):
            v = conv_by_integration(a, Fraction(k, 8))
            assert abs(v) <= M
            if k % 8 == 0:
                m = k // 8
                assert v == (c[m - 1] if 1 <= m <= 2 * n - 1 else 0)
    print("selftest passed")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--data")
    ap.add_argument("--quick", action="store_true",
                    help="sample 60 knots instead of all in check C")
    ap.add_argument("--random-points", type=int, default=200)
    ap.add_argument("--seed", type=int, default=20261103)
    args = ap.parse_args()
    if args.selftest:
        selftest()
        return 0
    if not args.data:
        ap.error("--data DIR is required")
    out = []

    def log(s=""):
        print(s)
        out.append(s)

    rng = random.Random(args.seed)
    all_ok = True      # integrity: hashes, A == B, check C, recorded fraction
    claims = []        # (claim, confirmed?)
    t_all = time.perf_counter()
    try:
        import flint
        flint_version = flint.__version__
    except ImportError:
        flint_version = "not installed (check B skipped)"
    log("python %s; python-flint %s" % (sys.version.split()[0], flint_version))
    for cert in CERTS:
        log("=" * 78)
        log("%s  [%s]" % (cert["name"], cert["row"]))
        path = os.path.join(args.data, cert["file"])
        digest = sha256_of(path)
        okhash = digest == cert["sha256"]
        log("  sha256 %s %s" % (digest, "matches pinned value" if okhash
                                 else "MISMATCH (expected %s)" % cert["sha256"]))
        if not okhash:
            all_ok = False
            continue
        text = open(path, encoding="utf-8").read()
        if cert["fmt"] == "json":
            lits, obj = literals_from_json(text, cert["key"])
            if "cells" in obj and int(obj["cells"]) != len(lits):
                log("  declared cell count disagrees with data"); all_ok = False
        else:
            lits = literals_from_python_source(text, cert["key"])
        log("  %d values parsed (%d negative)" % (
            len(lits), sum(1 for s in lits if s.startswith("-"))))
        if len(lits) != cert["cells"]:
            log("  CELL COUNT MISMATCH"); all_ok = False; continue
        bound = Fraction(cert["bound"])
        confirmed_by = []
        for reading in cert["readings"]:
            R, okC = evaluate(lits, reading, rng, args.random_points, args.quick, log)
            all_ok &= okC
            if cert["fraction"] is not None and reading == cert["primary"]:
                eq = R == Fraction(*cert["fraction"])
                log("    -> equals the exact fraction recorded on the page: %s" % eq)
                all_ok &= eq
            le = R <= bound
            log("    -> R(f) <= %s (claimed bound): %s, margin %.3e" % (
                cert["bound"], le, float(bound - R)))
            if le:
                confirmed_by.append(reading)
            if "bound_info" in cert:
                bi = Fraction(cert["bound_info"])
                log("    -> R(f) <= %s (superseded print, info only): %s, "
                    "margin %.3e" % (cert["bound_info"], R <= bi, float(bi - R)))
        claims.append(("%s: C_1d <= %s" % (cert["name"], cert["bound"]),
                       bool(confirmed_by), confirmed_by))
    log("=" * 78)
    log("checker integrity (hashes, A == B, check C, recorded fractions): %s"
        % ("OK" if all_ok else "PROBLEM"))
    for claim, ok, rd in claims:
        log("  %-62s %s" % (claim, "CONFIRMED (reading: %s)" % ", ".join(rd)
                            if ok else "NOT CONFIRMED"))
    log("total runtime %.1fs" % (time.perf_counter() - t_all))
    return 0 if all_ok and all(ok for _, ok, _ in claims) else 1


if __name__ == "__main__":
    sys.exit(main())
