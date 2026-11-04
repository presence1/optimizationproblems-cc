#!/usr/bin/env python3
"""Independent rigorous check of the finite lower bound C_70 > 1.20194336.

C_70 (reverse Brunn-Minkowski constant) is the least C such that for all n
and all centrally symmetric convex bodies B1, B2 in R^n there is a linear u,
|det u| = 1, with |u(B1) + B2|^{1/n} <= C (|B1|^{1/n} + |B2|^{1/n}).

Patankar's cube-ball criterion (proof re-derived in README.md): for the cube
B1 = [-a/2, a/2]^n and the unit ball B2 = B_2^n, every u with |det u| = 1 has
    |u(B1) + B2| >= sum_{k=0}^n C(n,k) a^(n-k) kappa_k,
kappa_k = pi^(k/2) / Gamma(1 + k/2), hence for every a > 0, n >= 1, and in
particular for any single retained term k,
    C_70 >= R := (C(n,k) a^(n-k) kappa_k)^(1/n) / (a + kappa_n^(1/n)).

The row [Pin2026] of constants/70a.md takes n = 10^12, k = 367879441172 and
a / kappa_n^(1/n) = (n-k)/k, and claims R > 1.20194336.  This script encloses
R rigorously in two independent ways:

  1. Arb ball arithmetic (python-flint), evaluating the criterion's expression
     literally: log Gamma for the binomial and the ball volumes, a from its
     definition, then the ratio.  No algebraic simplification.
  2. mpmath interval arithmetic (mpmath.iv), on the simplified closed form
         log R = log C(n,k)/n + (1-t) log(1-t) + t log t
                 + (log((n/2)!) t - log((k/2)!)) / n,       t = k/n,
     (k, n even), with every factorial enclosed by Robbins' bounds
         (m+1/2) log m - m + log(2 pi)/2 + 1/(12m+1) < log m!
                                       < (m+1/2) log m - m + log(2 pi)/2 + 1/(12m).
     No log-gamma routine is used here.

Calibrations: the full Steiner sum (method 1) reproduces Patankar's earlier
witness 1.201927... (n = 300000, a = 13/1000) and the closed form
sqrt(1/2 + 1/sqrt(pi)) for n = 2, a = sqrt(pi).

Written from the constant page and the paper's statement only; the
certificate authors' checkers were not opened or run.
Usage: python3 -I check_c70.py [--json certificates/c70_candidate.json]
"""

import argparse
import hashlib
import json
import sys
import time
from fractions import Fraction

N = 10**12
K = 367879441172
CLAIM = Fraction("1.20194336")           # = 3756073/3125000
LIMIT_CLAIM = Fraction("1.20194336847")  # for exp(1/(2e)), info only


# ----------------------------------------------------------------- method 1
def method1_arb(n, k, prec=256):
    import flint
    from flint import arb, ctx
    old = ctx.prec
    ctx.prec = prec
    try:
        def lgamma(x):
            return arb(x).lgamma()

        def log_kappa(m):  # log(pi^(m/2) / Gamma(1 + m/2))
            return arb(m) / 2 * arb.pi().log() - lgamma(arb(m) / 2 + 1)

        log_binom = lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1)
        log_kn_root = log_kappa(n) / n                 # log kappa_n^(1/n)
        log_a = (arb(n - k) / k).log() + log_kn_root   # a = ((n-k)/k) kappa_n^(1/n)
        log_term = log_binom + (n - k) * log_a + log_kappa(k)
        denom = log_a.exp() + log_kn_root.exp()        # a + kappa_n^(1/n)
        R = (log_term / n).exp() / denom
        return R
    finally:
        ctx.prec = old


def full_sum_arb(n, a, prec=192):
    """(sum_k C(n,k) a^(n-k) kappa_k)^(1/n) / (a + kappa_n^(1/n)), all terms."""
    from flint import arb, ctx
    old = ctx.prec
    ctx.prec = prec
    try:
        a = arb(a)
        loga = a.log()
        logpi = arb.pi().log()
        lg_n1 = arb(n + 1).lgamma()
        logs = []
        for k in range(n + 1):
            lt = (lg_n1 - arb(k + 1).lgamma() - arb(n - k + 1).lgamma()
                  + (n - k) * loga
                  + arb(k) / 2 * logpi - (arb(k) / 2 + 1).lgamma())
            logs.append(lt)
        M = max(float(x.mid()) for x in logs)
        s = arb(0)
        for x in logs:
            s += (x - M).exp()
        log_sum = s.log() + M
        log_kn = (arb(n) / 2 * logpi - (arb(n) / 2 + 1).lgamma()) / n
        return (log_sum / n).exp() / (a + log_kn.exp())
    finally:
        ctx.prec = old


# ----------------------------------------------------------------- method 2
def method2_iv(n, k, dps=60):
    import mpmath
    iv = mpmath.iv
    iv.dps = dps
    two_pi = 2 * iv.pi

    def log_fact(m):  # Robbins' enclosure of log(m!), m >= 1
        m_iv = iv.mpf(m)
        base = (m_iv + iv.mpf(0.5)) * iv.log(m_iv) - m_iv + iv.log(two_pi) / 2
        lo = base + iv.mpf(1) / (12 * m_iv + 1)
        hi = base + iv.mpf(1) / (12 * m_iv)
        return iv.mpf([lo.a, hi.b])

    assert n % 2 == 0 and k % 2 == 0 and 0 < k < n
    t = iv.mpf(k) / n
    log_binom = log_fact(n) - log_fact(k) - log_fact(n - k)
    log_R = (log_binom / n + (1 - t) * iv.log(1 - t) + t * iv.log(t)
             + (t * log_fact(n // 2) - log_fact(k // 2)) / n)
    return iv.exp(log_R), log_R


def frac_lt_arb(q, x):
    """Rigorous q < x for a rational q and an arb ball x."""
    from flint import arb
    return bool(arb(q.numerator) / q.denominator < x)


def arb_to_iv(x, dps=80):
    """Outward mpmath interval containing the arb ball x."""
    import mpmath
    mpmath.iv.dps = dps
    mid = mpmath.iv.mpf(x.mid().str(dps, radius=False))
    rad = mpmath.iv.mpf(x.rad().str(dps, radius=False))
    pad = mpmath.iv.mpf(10) ** (-dps + 10) * (abs(mid) + 1)  # string rounding
    lo, hi = mid - rad - pad, mid + rad + pad
    return mpmath.iv.mpf([lo.a, hi.b])


def overlap(x_iv, y_iv):
    return x_iv.a <= y_iv.b and y_iv.a <= x_iv.b


def selftest():
    from flint import arb, ctx
    ctx.prec = 192
    # n = 2, a = sqrt(pi): R^2 = 1/2 + 1/sqrt(pi) (closed form, see README)
    R2 = full_sum_arb(2, arb.pi().sqrt())
    target = (arb(1) / 2 + 1 / arb.pi().sqrt()).sqrt()
    assert R2.overlaps(target) and R2.rad() < arb(10) ** -40
    # methods 1 and 2 agree on small even cases (independent formulas)
    for n, k in ((1000, 368), (10**6, 367880), (2 * 10**8, 73575888)):
        R1 = arb_to_iv(method1_arb(n, k))
        R2iv, _ = method2_iv(n, k)
        assert overlap(R1, R2iv), (n, k)
    # a single term never exceeds the full sum at the same a (n = 40)
    for k in (4, 14, 30):
        kn_root = ((arb(40) / 2 * arb.pi().log() - (arb(20) + 1).lgamma()) / 40).exp()
        a = arb(40 - k) / k * kn_root
        Rs = method1_arb(40, k)
        Rf = full_sum_arb(40, a)
        assert Rs < Rf, k
    print("selftest passed")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="certificate JSON (read as data only)")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--skip-baseline", action="store_true")
    args = ap.parse_args()
    import flint
    import mpmath
    mpmath.mp.dps = 80  # for printing interval endpoints (default is 15)
    print("python %s; python-flint %s; mpmath %s" % (
        sys.version.split()[0], flint.__version__, mpmath.__version__))
    if args.selftest:
        selftest()
        return 0
    ok = True
    if args.json:
        raw = open(args.json, "rb").read()
        print("certificate %s sha256 %s" % (args.json, hashlib.sha256(raw).hexdigest()))
        c = json.loads(raw.decode("utf-8"), parse_float=str)
        same = (c["n"] == N and c["k"] == K
                and Fraction(c["normalized_side"]) == Fraction(N - K, K)
                and Fraction(c["claim"]) == CLAIM)
        print("certificate parameters match the constant page: %s" % same)
        ok &= same
    print("n = %d, k = %d, t = k/n = %s, a/kappa_n^(1/n) = (n-k)/k = %d/%d" % (
        N, K, Fraction(K, N), N - K, K))
    print("claim: R > %s = %s" % (CLAIM, CLAIM))

    t0 = time.perf_counter()
    R1 = method1_arb(N, K)
    t1 = time.perf_counter() - t0
    print("method 1 (Arb, 256 bits, literal criterion): R in %s  [%.2fs]" % (R1.str(35, radius=True), t1))
    ok1 = frac_lt_arb(CLAIM, R1)
    print("  -> %s < R rigorously: %s" % (CLAIM, ok1))

    t0 = time.perf_counter()
    Riv, logR = method2_iv(N, K)
    t2 = time.perf_counter() - t0
    print("method 2 (mpmath.iv, 60 digits, Robbins bounds): R in [%s, %s]  [%.2fs]" % (
        mpmath.nstr(mpmath.mpf(Riv.a), 40), mpmath.nstr(mpmath.mpf(Riv.b), 40), t2))
    # mpmath raises ValueError for an undecidable interval comparison, so a
    # True here is a certain inequality
    try:
        ok2 = bool(mpmath.iv.mpf(CLAIM.numerator) / CLAIM.denominator < Riv)
    except ValueError:
        ok2 = False
    print("  -> %s < R rigorously: %s" % (CLAIM, ok2))
    # the two enclosures must overlap
    ov = overlap(arb_to_iv(R1), Riv)
    width2 = mpmath.mpf(Riv.b) - mpmath.mpf(Riv.a)
    print("  methods 1 and 2 enclosures overlap: %s (method 2 width %s)" % (
        ov, mpmath.nstr(width2, 3)))
    ok &= ok1 and ok2 and ov

    # info: neighbouring even k, and the analytic limit
    for kk in (K - 2, K + 2):
        Rk = method1_arb(N, kk)
        print("  (info) k = %d: R = %s" % (kk, Rk.str(22)))
    from flint import arb, ctx
    ctx.prec = 256
    lim = (1 / (2 * arb(1).exp())).exp()
    print("  (info) exp(1/(2e)) = %s; > %s: %s" % (
        lim.str(30), LIMIT_CLAIM, frac_lt_arb(LIMIT_CLAIM, lim)))

    if not args.skip_baseline:
        t0 = time.perf_counter()
        Rb = full_sum_arb(300000, arb(13) / 1000)
        print("calibration: full Steiner sum, n = 300000, a = 13/1000: R = %s  [%.1fs]" % (
            Rb.str(25, radius=True), time.perf_counter() - t0))
        okb = frac_lt_arb(Fraction("1.201927"), Rb)
        print("  -> > 1.201927 (Patankar's row [Pat2026]): %s" % okb)
        ok &= okb
    print("RESULT: %s" % ("CONFIRMED: C_70 > 1.20194336 (given the criterion)"
                          if ok else "NOT CONFIRMED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
