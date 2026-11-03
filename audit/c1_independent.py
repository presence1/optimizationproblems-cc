#!/usr/bin/env python3
"""Auditor's independent recomputation for C_1d (STEPS2026, AER2026, CERT2026)
and C_1c (Kos2026, R2026), sharing no code with verify/1d, verify/1c or the
certificate authors.

Algorithm: Kronecker substitution.  All lag sums are read off from ONE big
integer product (Python's built-in multiplication), with balanced-digit
extraction for signed coefficients.  This differs from the direct O(N^2)
loops and the FLINT polynomial products used on the verify branches.

  C_1d:  R(f) = 2N max_s |c_s| / (sum v)^2,  c_s = sum_{i+j=s} v_i v_j
  C_1c:  L(f) = K min_{0<=k<=K} A_k / (sum w)^2,  A_k = sum_i w_i w_{i+k}

(Reductions re-derived in AUDIT.md.)  The AER2026 .py file is NOT parsed
with ast and never executed: the list literal is located by text search and
each token is matched against a strict numeric regular expression.

Usage: python3 -I c1_independent.py --d1 DIR_1d --c1 DIR_1c
"""

import argparse
import hashlib
import json
import math
import re
import sys
from fractions import Fraction

NUM = re.compile(r"^[+-]?(\d+\.\d*|\.\d+|\d+)([eE][+-]?\d+)?$")


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def json_number_strings(path, key):
    # keep the literal text of each number
    obj = json.loads(open(path, encoding="utf-8").read(),
                     parse_float=lambda s: s, parse_int=lambda s: s)
    vals = obj[key]
    assert all(isinstance(v, str) and NUM.match(v) for v in vals)
    return vals


def py_list_strings(path, name):
    text = open(path, encoding="utf-8").read()
    hits = [m.start() for m in re.finditer(r"^%s\s*=\s*\[" % re.escape(name), text, re.M)]
    assert len(hits) == 1, "expected exactly one top-level assignment"
    start = text.index("[", hits[0]) + 1
    end = text.index("]", start)
    body = text[start:end]
    body = re.sub(r"#[^\n]*", "", body)              # strip comments
    toks = [t.strip() for t in body.replace("\n", " ").split(",")]
    toks = [t for t in toks if t]
    assert all(NUM.match(t) for t in toks), "non-numeric token"
    return toks


def exact(strings, reading):
    if reading == "decimal":
        return [Fraction(s) for s in strings]
    return [Fraction(float(s)) for s in strings]       # binary64 reading


def to_ints(fr):
    D = 1
    for q in fr:
        D = D * q.denominator // math.gcd(D, q.denominator)
    return [int(q * D) for q in fr]


def kronecker_square_signed(a):
    """c_s = sum_{i+j=s} a_i a_j from one big-integer square."""
    bound = len(a) * max(abs(x) for x in a) ** 2           # |c_s| <= this
    B = bound.bit_length() + 2
    X = 0
    for x in reversed(a):
        X = (X << B) + x
    Y = X * X
    out, base, half = [], 1 << B, 1 << (B - 1)
    for _ in range(2 * len(a) - 1):
        r = Y & (base - 1)
        if r >= half:
            r -= base
        out.append(r)
        Y = (Y - r) >> B
    assert Y == 0
    return out


def kronecker_lags(w, K):
    """A_k = sum_i w_i w_{i+k} for k = 0..K (w_i >= 0)."""
    n = len(w)
    bound = n * max(w) ** 2
    B = bound.bit_length() + 1
    P = 0
    for x in reversed(w):
        P = (P << B) + x
    Q = 0
    for x in w:                       # reversed polynomial
        Q = (Q << B) + x
    # coefficient of z^(n-1+k) in P(z) Q(z) is A_k; Q was built with w_0 as
    # the top coefficient, i.e. Q(z) = sum_i w_i z^(n-1-i)
    Y = P * Q
    mask = (1 << B) - 1
    Y >>= B * (n - 1)
    out = []
    for k in range(K + 1):
        out.append(Y & mask if k < n else 0)
        Y >>= B
    return out


def digits(q, d=22):
    ip = q.numerator // q.denominator
    fr = (q - ip) * 10**d
    return "%d.%s" % (ip, str(fr.numerator // fr.denominator).rjust(d, "0"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--d1")
    ap.add_argument("--c1")
    args = ap.parse_args()
    ok = True

    # self-tests of the Kronecker routines against definitions
    import random
    rng = random.Random(11)
    for _ in range(200):
        n = rng.randrange(1, 12)
        a = [rng.randrange(-9, 10) for _ in range(n)]
        if not any(a):
            continue
        direct = [sum(a[i] * a[s - i] for i in range(n) if 0 <= s - i < n)
                  for s in range(2 * n - 1)]
        assert kronecker_square_signed(a) == direct
        w = [rng.randrange(0, 9) for _ in range(n)]
        if not any(w):
            continue
        K = rng.randrange(0, 15)
        assert kronecker_lags(w, K) == [sum(w[i] * w[i + k] for i in range(n - k)) if k < n else 0
                                        for k in range(K + 1)]
    print("self-test: Kronecker routines agree with the definitions on random data")

    if args.d1:
        page = {  # copied from constants/1d.md at 87b4ebb
            "STEPS2026": ("steps_construction.json", "3dd39fae744555179b0356b84e752db724e892bd23dda51403976edfb5b3a28c",
                          "json", "values", "1.460217284022874",
                          Fraction(698746209786798359455483373677229695641600,
                                   478522078482569620433992386249161163190849)),
            "AER2026": ("problem_4_signed_autoconvolution_bounds.py.txt",
                        "1a290ad1074c10a871adaf2bd44402af56be8cf151f1f775a8fc37c7bdff54b2",
                        "py", "STEP_FUNCTION_C4_PRIME_N600", "1.459989046905384", None),
            "CERT2026": ("cert300_construction.json", "51f864ee95205f06b98923c382d23cb3dfde5f0d4208a4c591bad015e5908a0e",
                         "json", "values", "1.4630715826075594",
                         Fraction(2039224160683882663565441886346340189798400,
                                  1393796574908163689489385839036226787118881)),
        }
        for name, (fn, h, fmt, key, bound, frac) in page.items():
            path = "%s/%s" % (args.d1, fn)
            hs = sha(path)
            strs = json_number_strings(path, key) if fmt == "json" else py_list_strings(path, key)
            print("1d %-9s sha256 ok: %s; %d cells" % (name, hs == h, len(strs)))
            ok &= hs == h
            for reading in ("binary64", "decimal"):
                a = to_ints(exact(strs, reading))
                c = kronecker_square_signed(a)
                S = sum(a)
                R = Fraction(2 * len(a) * max(abs(x) for x in c), S * S)
                le = R <= Fraction(bound)
                eq = "" if frac is None or reading != "binary64" else (
                    ", equals page fraction: %s" % (R == frac))
                print("   %-8s R = %s...  <= %s: %s%s" % (reading, digits(R), bound, le, eq))
                ok &= le and (frac is None or reading != "binary64" or R == frac)
                if name == "CERT2026":
                    print("            vs the starred print 1.463071582607559: R <= it is %s "
                          "(R - it = %.3e)" % (R <= Fraction("1.463071582607559"),
                                              float(R - Fraction("1.463071582607559"))))

    if args.c1:
        rows = {
            "Kos2026": ("K24576_0.4103333.json", "963cb7273062e7360fdfa460bb19c1cf37729364b8f708b09580b6655b783c9e",
                        "0.4103333", Fraction(134648548624804778248790016, 328144294688458468928334649), 21264),
            "R2026": ("certificate.json", "62ac49ddbbfc9aa1053406363d9df9c912022ab85b72a447cf73c94bb9c1fd0e",
                      "0.4103287", Fraction(21072342208353792, 51354782902387969), None),
        }
        for name, (fn, h, bound, frac, kpage) in rows.items():
            path = "%s/%s" % (args.c1, fn)
            hs = sha(path)
            obj = json.loads(open(path, encoding="utf-8").read())
            K, w = obj["K"], obj["weights_int"]
            assert isinstance(K, int) and all(isinstance(x, int) and x >= 0 for x in w)
            A = kronecker_lags(w, K)
            S = sum(w)
            m = min(A)
            arg = [k for k, x in enumerate(A) if x == m]
            L = Fraction(K * m, S * S)
            tz = len(w) - 1 - max(i for i, x in enumerate(w) if x)
            print("1c %-8s sha256 ok: %s; K=%d n=%d trailing zeros %d; L = %s... argmin %s; "
                  ">= %s: %s; equals page fraction: %s"
                  % (name, hs == h, K, len(w), tz, digits(L), arg, bound, L >= Fraction(bound), L == frac))
            ok &= hs == h and L >= Fraction(bound) and L == frac and (kpage is None or arg == [kpage])
            if name == "Kos2026":
                ok &= (K, len(w), tz) == (24576, 24592, 8)
                # page: "about 22% of the mass in [1/6144, 2/6144)" = cells 4..7 at K = 24576
                frac_mass = Fraction(sum(w[4:8]), S)
                print("   mass in [1/6144, 2/6144): %.4f; support [0, %s)" % (
                    float(frac_mass), Fraction(len(w) - tz, K)))
    print("RESULT: %s" % ("ALL CHECKS PASSED" if ok else "SOME CHECK FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
