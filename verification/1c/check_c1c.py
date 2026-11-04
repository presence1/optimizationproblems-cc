#!/usr/bin/env python3
"""Independent exact checker for step-function lower bounds on C_1c.

C_1c (Barnard-Steinerberger autocorrelation constant) is the least C with

    min_{0 <= t <= 1} int f(x) f(x+t) dx  <=  C (int f)^2

for all non-negative f in L^1(R).  Any such f with int f > 0 therefore gives
the lower bound  C_1c >= L(f) := min_{t in [0,1]} g(t) / (int f)^2, where
g(t) = int f(x) f(x+t) dx.

For f = sum_{i<n} w_i 1_[i/K, (i+1)/K) with integer weights w_i >= 0:
    g(t) = sum_d A_d * max(0, 1/K - |t - d/K|),   A_d = sum_i w_i w_{i+d},
so g is piecewise linear with knots at the multiples of 1/K, g(k/K) = A_k / K,
and (proof in README.md)
    L(f) = K * min_{0 <= k <= K} A_k / S^2,   S = sum_i w_i.

Written from the definition on the constant page and the certificate's data
format (FORMAT.md of the certificate repository) only; no code from the
certificate authors is used.

Evaluations:
  A. A_k for every 0 <= k <= K by direct summation over Python integers;
  B. A_k as coefficients of P(x) * P_rev(x) with python-flint's fmpz_poly;
  C. g(t) by brute-force exact integration of u -> G(u) G(u + tau) over its
     breakpoints (integer arithmetic, no use of the tent formula) at sampled
     knots, including the minimising knot and its neighbours, and at random
     rational points strictly between knots (checking linearity).

Usage:  python3 -I check_c1c.py --data DIR [--knots N] [--interior N]
"""

import argparse
import hashlib
import json
import operator
import os
import random
import sys
import time
from fractions import Fraction

CERTS = [
    dict(
        name="Kos2026 (K = 24576)",
        row="constants/1c.md line 28 (asterisked)",
        file="K24576_0.4103333.json",
        sha256="963cb7273062e7360fdfa460bb19c1cf37729364b8f708b09580b6655b783c9e",
        bound="0.4103333",
        fraction=(134648548624804778248790016, 328144294688458468928334649),
        argmin=21264,
        K=24576, n=24592, trailing_zeros=8,
    ),
    dict(
        name="R2026 (K = 6144), calibration",
        row="constants/1c.md line 27 (not asterisked; replayed by [T2026])",
        file="certificate.json",
        sha256="62ac49ddbbfc9aa1053406363d9df9c912022ab85b72a447cf73c94bb9c1fd0e",
        bound="0.4103287",
        fraction=(21072342208353792, 51354782902387969),
        argmin=None,
        K=6144, n=6148, trailing_zeros=None,
    ),
]


def sha256_of(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def load(path):
    # floats (e.g. in metadata keys) are kept as strings, so a float inside
    # the weights list fails the integer type check below
    obj = json.loads(open(path, encoding="utf-8").read(), parse_float=str)
    K, w = obj["K"], obj["weights_int"]
    if type(K) is not int or K <= 0:
        raise ValueError("bad K")
    if not isinstance(w, list) or not w or any(type(x) is not int for x in w):
        raise ValueError("weights must be a non-empty list of JSON integers")
    if any(x < 0 for x in w):
        raise ValueError("negative weight: f would not be non-negative")
    if sum(w) == 0:
        raise ValueError("all weights zero")
    return K, w


def lags_direct(w, K):
    """A_k = sum_i w_i w_{i+k} for k = 0..K (0 when k >= n)."""
    n = len(w)
    mul = operator.mul
    return [sum(map(mul, w[: n - k], w[k:])) if k < n else 0 for k in range(K + 1)]


def lags_flint(w, K):
    try:
        import flint
    except ImportError:
        return None
    n = len(w)
    P = flint.fmpz_poly(w)
    Q = flint.fmpz_poly(w[::-1])       # x^(n-1) P(1/x)
    c = [int(x) for x in (P * Q).coeffs()]
    c += [0] * (2 * n - 1 - len(c))
    # coefficient of x^(n-1+k) in P*Q is sum_{i-j=k} w_i w_j = A_k
    return [c[n - 1 + k] if k < n else 0 for k in range(K + 1)]


def g_times_q(w, k, p, q):
    """q * I(tau) for tau = k + p/q, with I(tau) = int G(u) G(u+tau) du and
    G = sum_i w_i 1_[i, i+1).  Brute force in units of 1/q: both factors are
    right-continuous step functions whose jumps are all in the breakpoint set,
    so each piece [U0, U1) is evaluated at its left end.  Integer arithmetic.
    (g(t) = I(K t) / K, by the substitution x = u / K.)"""
    n = len(w)
    shift = k * q + p                        # tau in units of 1/q
    pts = set(range(0, n * q + 1, q))        # jumps of G(u)
    pts.update(j * q - shift for j in range(n + 1))  # jumps of G(u + tau)
    pts = sorted(U for U in pts if 0 <= U <= n * q)
    total = 0
    for U0, U1 in zip(pts, pts[1:]):
        i = U0 // q
        j = (U0 + shift) // q
        if i < n and 0 <= j < n:
            total += (U1 - U0) * w[i] * w[j]
    return total  # = q * I(tau)


def check_C(w, A, K, kmin, rng, n_knots, n_interior):
    knots = {0, K, kmin, max(kmin - 1, 0), min(kmin + 1, K)}
    while len(knots) < min(n_knots, K + 1):
        knots.add(rng.randrange(0, K + 1))
    for k in sorted(knots):
        if g_times_q(w, k, 0, 1) != A[k]:
            return False, "knot mismatch at k=%d" % k
    interior = [(kmin, 1, 2), (max(kmin - 1, 0), 1, 3)]
    while len(interior) < n_interior:
        q = rng.randrange(2, 10**6)
        interior.append((rng.randrange(0, K), rng.randrange(1, q), q))
    for k, p, q in interior:
        # linear interpolation between knots k and k+1, times q
        expected = (q - p) * A[k] + p * A[k + 1]
        if g_times_q(w, k, p, q) != expected:
            return False, "non-linearity at tau=%d+%d/%d" % (k, p, q)
    # g(-t) = g(t): spot check symmetry at a non-knot point
    if g_times_q(w, -1, 2, 3) != g_times_q(w, 0, 1, 3):
        return False, "symmetry failure"
    return True, "%d knots (incl. argmin and neighbours) and %d interior points" \
        " agree exactly" % (len(knots), len(interior))


def decimal_digits(q, digits=25):
    ip = q.numerator // q.denominator
    sc = (q - ip) * 10**digits
    return "%d.%s..." % (ip, str(sc.numerator // sc.denominator).rjust(digits, "0"))


def selftest():
    # f = 1_[0,1] (K=1, w=(1)): g(t) = 1 - t on [0,1], min 0 -> L = 0.
    A = lags_direct([1], 1)
    assert A == [1, 0]
    # w = (1,1), K = 1: f = 1 on [0,2); g(t) = 2 - t, min at t=1 is 1; S=2 -> 1/4.
    A = lags_direct([1, 1], 1)
    assert A == [2, 1] and Fraction(1 * min(A), 4) == Fraction(1, 4)
    # the ruler {0,1,4,6}, K = 6 (all differences 1..6 occur once): 3/8,
    # as stated on the constant page.
    w = [1, 1, 0, 0, 1, 0, 1]
    A = lags_direct(w, 6)
    assert Fraction(6 * min(A), sum(w) ** 2) == Fraction(3, 8)
    rng = random.Random(7)
    for _ in range(30):
        n = rng.randrange(1, 10)
        K = rng.randrange(1, 12)
        w = [rng.randrange(0, 6) for _ in range(n)]
        if sum(w) == 0:
            continue
        A = lags_direct(w, K)
        B = lags_flint(w, K)
        assert B is None or A == B
        for k in range(K + 1):
            assert g_times_q(w, k, 0, 1) == A[k]
            if k < K:
                assert g_times_q(w, k, 1, 4) == 3 * A[k] + A[k + 1]
    print("selftest passed")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--knots", type=int, default=400,
                    help="number of knots for check C (default 400)")
    ap.add_argument("--interior", type=int, default=200)
    ap.add_argument("--seed", type=int, default=20261103)
    args = ap.parse_args()
    if args.selftest:
        selftest()
        return 0
    if not args.data:
        ap.error("--data DIR required")
    rng = random.Random(args.seed)
    try:
        import flint
        fv = flint.__version__
    except ImportError:
        fv = "not installed (check B skipped)"
    print("python %s; python-flint %s" % (sys.version.split()[0], fv))
    integrity, claims, t_all = True, [], time.perf_counter()
    for cert in CERTS:
        print("=" * 78)
        print("%s  [%s]" % (cert["name"], cert["row"]))
        path = os.path.join(args.data, cert["file"])
        dig = sha256_of(path)
        if dig != cert["sha256"]:
            print("  sha256 MISMATCH: %s" % dig)
            integrity = False
            continue
        print("  sha256 %s matches pinned value" % dig)
        K, w = load(path)
        n = len(w)
        print("  K = %d, n = %d weights, max weight %d (%d bits), all >= 0, "
              "S = %d" % (K, n, max(w), max(w).bit_length(), sum(w)))
        shape_ok = (K == cert["K"] and n == cert["n"])
        if cert["trailing_zeros"] is not None:
            last_nonzero = max(i for i, x in enumerate(w) if x)
            tz = n - 1 - last_nonzero
            print("  trailing zero weights: %d (page: %d); support [0, %s)" % (
                tz, cert["trailing_zeros"], Fraction(n - tz, K)))
            shape_ok &= tz == cert["trailing_zeros"]
        if not shape_ok:
            print("  SHAPE MISMATCH with the page")
            integrity = False
        t0 = time.perf_counter()
        A = lags_direct(w, K)
        tA = time.perf_counter() - t0
        t0 = time.perf_counter()
        B = lags_flint(w, K)
        tB = time.perf_counter() - t0
        if B is not None and A != B:
            print("  A and B DISAGREE")
            integrity = False
            continue
        print("  A direct (all %d lags): %.1fs   B FLINT: %s   agree: %s" % (
            K + 1, tA, "%.2fs" % tB if B is not None else "skipped",
            "yes" if B is not None else "n/a"))
        S = sum(w)
        m = min(A)
        kmins = [k for k, a in enumerate(A) if a == m]
        L = Fraction(K * m, S * S)
        print("  min_k A_k attained at k = %s (t = k/K)" % kmins)
        print("  L(f) = %d/%d" % (L.numerator, L.denominator))
        print("       = %s" % decimal_digits(L))
        if cert["argmin"] is not None:
            print("  -> argmin matches the page (k = %d): %s" % (
                cert["argmin"], kmins == [cert["argmin"]]))
        eq = L == Fraction(*cert["fraction"])
        print("  -> equals the exact fraction recorded on the page: %s" % eq)
        integrity &= eq
        b = Fraction(cert["bound"])
        ok = L >= b
        print("  -> L(f) >= %s (claimed bound): %s, margin %.3e" % (
            cert["bound"], ok, float(L - b)))
        if cert["K"] == 24576:
            mass = Fraction(sum(w[4:8]), S)
            print("  (info) mass fraction in [1/6144, 2/6144): %.4f" % float(mass))
        t0 = time.perf_counter()
        okC, msg = check_C(w, A, K, kmins[0], rng, args.knots, args.interior)
        print("  C brute-force integration: %s (%.0fs) -> %s" % (
            "PASS" if okC else "FAIL", time.perf_counter() - t0, msg))
        integrity &= okC
        claims.append(("%s: C_1c >= %s" % (cert["name"], cert["bound"]), ok))
    print("=" * 78)
    print("checker integrity (hashes, shape, A == B, check C, fractions): %s" % (
        "OK" if integrity else "PROBLEM"))
    for c, ok in claims:
        print("  %-55s %s" % (c, "CONFIRMED" if ok else "NOT CONFIRMED"))
    print("total runtime %.0fs" % (time.perf_counter() - t_all))
    return 0 if integrity and all(ok for _, ok in claims) else 1


if __name__ == "__main__":
    sys.exit(main())
