#!/usr/bin/env python3
"""Independent rigorous check of the trial-function lower bound on C_16.

C_16 = L = max_{delta >= 1} [4 pi Theta(delta) - ln delta - ln(1 + ln delta)],
Theta(delta) = sup{|u(0)|^2 : ||grad u||^2 = 1, ||Lap u||^2 = delta},
for zero-mean u on T^2 = [0, 2 pi]^2 (Lebesgue measure), as on the page.

Trial function (README of the certificate, row of constants/16a.md):
    u(x) = sum_{0 < |k| <= R} c(|k|^2) e^{i k.x},  c(n) = 1/(n (1 + mu n)),
with R = 4000, mu = 1221/10000.  By Parseval on [0,2pi]^2,
    ||grad u||^2 = 4 pi^2 S1,  ||Lap u||^2 = 4 pi^2 S2,  u(0) = S0, where
    S0 = sum_n r2(n) c(n),  S1 = sum_n r2(n) n c(n)^2,  S2 = sum_n r2(n) n^2 c(n)^2
(n = |k|^2 runs over 1..R^2, r2(n) = #{k in Z^2 : |k|^2 = n}).  Normalising
u by ||grad u|| shows 4 pi Theta(delta_u) >= S0^2 / (pi S1) with
delta_u = S2/S1, hence
    L >= S0^2/(pi S1) - ln(delta_u) - ln(1 + ln delta_u).

The three sums are enclosed by two independent methods:
  A. Arb ball arithmetic (python-flint), one ball operation per term;
  B. IEEE binary64 terms from exact integers (k = 2 or 3 correctly rounded
     operations each, some of them in a denominator, so a term's relative
     error is at most (1+u)^k/(1-u)^k - 1, u = 2^-53), summed by math.fsum,
     which returns the correctly rounded exact sum of its float inputs (one
     more factor 1 +- u).  Each sum is a sum of positive terms, so its
     relative error is at most (1+u)^(k+1)/(1-u)^k - 1, which is at most
     (1+u)^4/(1-u)^3 - 1 ~ 7.8e-16.  The bound is computed exactly with
     Fraction and rounded up (see sums_float).
The final formula is evaluated in Arb from either set of enclosures.
r2(n) is counted directly from the lattice and cross-checked against the
Gauss circle count and Jacobi's formula r2(n) = 4(d1(n) - d3(n)).

Written from the constant page and the certificate README only; the
submitter's checker and certifier were not opened.
Usage: python3 -I check_c16_lower.py [--json lower_certificate.json]
"""

import argparse
import hashlib
import json
import math
import sys
import time
from fractions import Fraction
from math import isqrt

import numpy as np

CLAIM = Fraction("2.1562247706")
R_DEFAULT = 4000
MU = (1221, 10000)


def r2_table(R):
    """r2[n] = #{(a,b) in Z^2 : a^2 + b^2 = n} for 0 <= n <= R^2."""
    N = R * R
    r = np.zeros(N + 1, dtype=np.int64)
    for a in range(-R, R + 1):
        bmax = isqrt(N - a * a)
        r[a * a] += 1                                    # b = 0
        if bmax >= 1:
            b = np.arange(1, bmax + 1, dtype=np.int64)
            r[a * a + b * b] += 2                        # b and -b; distinct n
    return r


def check_r2(r, R):
    N = R * R
    # Gauss circle count, computed independently with integer square roots
    gauss = sum(2 * isqrt(N - a * a) + 1 for a in range(-R, R + 1))
    ok1 = int(r.sum()) == gauss
    # Jacobi: r2(n) = 4 (d_1(n) - d_3(n)) for every 1 <= n <= R^2, where
    # d_j(n) counts the divisors of n that are = j mod 4.
    M = N
    d = np.zeros(M + 1, dtype=np.int64)
    for q in range(1, M + 1, 2):
        d[q::q] += 1 if q % 4 == 1 else -1
    ok2 = bool(np.array_equal(r[1:M + 1], 4 * d[1:M + 1]))
    return ok1, ok2, gauss


def sums_arb(r, mu, prec=128):
    from flint import arb, ctx
    ctx.prec = prec
    p, q = mu
    S0 = arb(0)
    S1 = arb(0)
    S2 = arb(0)
    nz = np.nonzero(r)[0]
    for n in nz.tolist():
        if n == 0:
            continue
        rn = int(r[n])
        den = n * (q + p * n)               # c(n) = q / den, exact integers
        c = arb(q) / den
        S0 += rn * c
        c2n = c * c * n
        S1 += rn * c2n
        S2 += (rn * n) * c2n
    return S0, S1, S2


def sums_float(r, mu):
    """Return (value, relative error bound) for each sum, method B."""
    p, q = mu
    n = np.nonzero(r)[0]
    n = n[n > 0]
    rn = r[n]
    nf = n.astype(np.float64)              # exact: n < 2^53
    D = (q + p * n).astype(np.float64)     # exact integer < 2^53
    num0 = (rn * q).astype(np.float64)     # exact integer
    num1 = (rn * q * q).astype(np.float64) # exact integer < 2^53
    # S0 terms: num0 / (n * D): 2 roundings
    t0 = num0 / (nf * D)
    # S1 terms: r n c^2 = r q^2 / (n D^2): 3 roundings (D*D, *n, /)
    t1 = num1 / (nf * (D * D))
    # S2 terms: r n^2 c^2 = r q^2 / D^2: 2 roundings
    t2 = num1 / (D * D)
    for arr in (t0, t1, t2):
        assert np.all(np.isfinite(arr)) and np.all(arr > 0)
    # all intermediate values are normal (no underflow): smallest term > 1e-30
    assert min(t0.min(), t1.min(), t2.min()) > 1e-300
    u = Fraction(1, 2**53)
    out = []
    for arr, k in ((t0, 2), (t1, 3), (t2, 2)):
        s = math.fsum(arr.tolist())
        # A term computed with k roundings, some of them in the denominator, is
        # exact * prod(1+e_i)^{+-1} with |e_i| <= u, so its relative error is
        # at most (1+u)^k/(1-u)^k - 1; fsum's final rounding adds a factor
        # (1 +- u).  Bound computed exactly, then rounded up to a float.
        rel = (1 + u) ** (k + 1) / (1 - u) ** k - 1
        rel_up = float(rel) * (1 + 1e-12)
        assert Fraction(rel_up) >= rel
        out.append((s, rel_up))
    return out


def L_from(S0, S1, S2):
    from flint import arb
    delta = S2 / S1
    ld = delta.log()
    return S0 * S0 / (arb.pi() * S1) - ld - (1 + ld).log(), delta


def interval(v, rel):
    """Ball containing every x with |x - v| <= rel * |x| (v > 0 float)."""
    from flint import arb
    # |x - v| <= rel x  =>  x <= v / (1 - rel), so radius v*rel/(1-rel)
    rad = arb(v) * rel / (1 - arb(rel))
    return arb(arb(v).mid(), rad.mid() + rad.rad()) * 1  # exact float midpoint


def run(R, mu, label, log):
    t0 = time.perf_counter()
    r = r2_table(R)
    ok1, ok2, gauss = check_r2(r, R)
    log("%s: R = %d, mu = %d/%d; lattice points with 0 < |k|^2 <= R^2: %d; "
        "r2 table: Gauss count %s, Jacobi check %s  [%.1fs]" % (
            label, R, mu[0], mu[1], gauss - 1, ok1, ok2, time.perf_counter() - t0))
    t0 = time.perf_counter()
    A = sums_arb(r, mu)
    LA, dA = L_from(*A)
    tA = time.perf_counter() - t0
    t0 = time.perf_counter()
    B = sums_float(r, mu)
    from flint import arb
    Bs = [interval(v, rel) for v, rel in B]
    LB, dB = L_from(*Bs)
    tB = time.perf_counter() - t0
    log("  A (Arb 128-bit): S0 = %s" % A[0].str(22, radius=True))
    log("                   S1 = %s" % A[1].str(22, radius=True))
    log("                   S2 = %s" % A[2].str(22, radius=True))
    log("                   delta = %s, L >= %s  [%.0fs]" % (
        dA.str(15), LA.str(20, radius=True), tA))
    log("  B (binary64 + fsum, rel. err <= %.2e): L in %s  [%.0fs]" % (
        B[1][1], LB.str(16, radius=True), tB))
    agree = LA.overlaps(LB) and all(x.overlaps(y) for x, y in zip(A, Bs))
    log("  A and B enclosures overlap: %s" % agree)
    return LA, LB, ok1 and ok2 and agree


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="lower_certificate.json (read as data only)")
    ap.add_argument("--R", type=int, default=R_DEFAULT)
    ap.add_argument("--skip-calibration", action="store_true")
    args = ap.parse_args()
    import flint
    from flint import arb

    def log(s):
        print(s, flush=True)

    log("python %s; numpy %s; python-flint %s" % (
        sys.version.split()[0], np.__version__, flint.__version__))
    ok = True
    if args.json:
        raw = open(args.json, "rb").read()
        log("certificate sha256 %s" % hashlib.sha256(raw).hexdigest())
        c = json.loads(raw.decode("utf-8"), parse_float=str)
        same = c["R"] == args.R and tuple(c["mu"]) == MU
        log("certificate R and mu match the page/README: %s" % same)
        ok &= same
        cert_L = Fraction(*c["L_lower_bound_rational"])
    LA, LB, okm = run(args.R, MU, "[certificate] trial function", log)
    claim = arb(CLAIM.numerator) / CLAIM.denominator
    okA = bool(claim < LA)
    okB = bool(claim < LB)
    log("  -> L > %s rigorously: method A %s, method B %s" % (CLAIM, okA, okB))
    log("  -> margin (A, lower end): %s" % (LA - claim).str(5))
    if args.json:
        cl = arb(cert_L.numerator) / cert_L.denominator
        log("  (info) certificate's own rational lower bound %s is <= A's enclosure: %s"
            % (cl.str(16), bool(cl <= LA)))
    ok &= okA and okB and okm
    if not args.skip_calibration:
        # [Pat2026], c_k = 1/(|k|^2(|k|^2 + 41/5)) = (5/41)/(|k|^2 (1 + 5|k|^2/41))
        LA2, LB2, okc = run(4000, (5, 41), "[calibration Pat2026] mu = 5/41", log)
        claim2 = arb(2156224) / 10**6
        okc &= bool(claim2 < LA2) and bool(claim2 < LB2)
        log("  -> > 2.156224 (row [Pat2026]): %s" % okc)
        ok &= okc
    log("RESULT: %s" % ("CONFIRMED: C_16 >= 2.1562247706" if ok else "NOT CONFIRMED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
