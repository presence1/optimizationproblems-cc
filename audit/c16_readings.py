#!/usr/bin/env python3
"""Auditor's analysis of the two readings of the C_16 (16a) definition.

Page, first sentence: L is the smallest constant such that
  ||u||_inf^2 <= (1/4pi) ||grad u||^2 [ln d + ln(1 + ln d) + L]
holds "for all zero-mean u in H^2(T^2) with sufficiently large frequency
ratio d = d(u)".  Page, "Equivalently": L = max_{d >= 1} F(d) with
  F(d) = 4 pi Theta(d) - ln d - ln(1 + ln d).

Reading (a): the inequality for every zero-mean u (every such u has d >= 1).
             Then L_a = sup_{d >= 1} F(d), the "equivalently" formula.
Reading (b): the inequality only for d(u) >= d0, d0 as large as one likes.
             Then L_b = lim sup_{d -> oo} F(d).

Exact extremal family (Cauchy-Schwarz with weights |k|^2(1 + mu|k|^2), see
AUDIT.md): for mu > 0 put c_k = 1/(|k|^2 (1 + mu|k|^2)) on all k != 0 and
  S0 = sum c_k,  S1 = sum |k|^2 c_k^2,  S2 = sum |k|^4 c_k^2.
Then d(mu) = S2/S1 and 4 pi Theta(d(mu)) = S0^2/(pi S1) EXACTLY, so
F(d(mu)) = S0^2/(pi S1) - ln d - ln(1 + ln d), and d(mu) -> oo as mu -> 0.

Small-mu expansions (Mellin transform; Z(s) = sum_{k != 0} |k|^{-2s}
= 4 zeta(s) L(s, chi_4) has a simple pole pi/(s-1) + beta at s = 1,
Z(0) = -1 and Z(-m) = 0 for m >= 1):
  S0 = pi ln(1/mu) + beta + mu + o(mu^M),  S2 = pi/mu - 1 + o(mu^M),
  S1 = S0 - mu S2 = pi ln(1/mu) + beta - pi + 2 mu + o(mu^M),
with beta = pi(2 gamma + 2 ln 2 + 3 ln pi - 4 ln Gamma(1/4)).  Hence
F -> 1 + beta/pi = (beta + pi)/pi = 1.82282525...: under reading (b) the
constant equals the page's own [BDZ2013] lower bound, and 2.1562247706 is
NOT a lower bound.  This script checks the expansions against direct lattice
sums (with integral tails), checks the Kronecker constant numerically, and
tabulates F along the family.

Usage: python3 -I c16_readings.py [--R 3000]
"""

import argparse
import math
import sys

import mpmath as mp
import numpy as np


def lattice_sums(mu, R):
    """Direct sums over 0 < |k| <= R plus the integral over |x| > R."""
    S0 = S1 = S2 = 0.0
    parts0, parts1, parts2 = [], [], []
    for a in range(-R, R + 1):
        bmax = math.isqrt(R * R - a * a)
        b = np.arange(-bmax, bmax + 1, dtype=np.float64)
        n = a * a + b * b
        n = n[n > 0]
        q = 1.0 + mu * n
        parts0.append(float(np.sum(1.0 / (n * q))))
        parts1.append(float(np.sum(1.0 / (n * q * q))))
        parts2.append(float(np.sum(1.0 / (q * q))))
    S0, S1, S2 = math.fsum(parts0), math.fsum(parts1), math.fsum(parts2)
    X = mu * R * R
    S0 += math.pi * math.log1p(1.0 / X)
    S1 += math.pi * (math.log1p(1.0 / X) - 1.0 / (1.0 + X))
    S2 += math.pi / (mu * (1.0 + X))
    return S0, S1, S2


def beta_const():
    return mp.pi * (2 * mp.euler + 2 * mp.log(2) + 3 * mp.log(mp.pi) - 4 * mp.log(mp.gamma(mp.mpf(1) / 4)))


def asym(mu, beta):
    mu = mp.mpf(mu)
    L = mp.log(1 / mu)
    S0 = mp.pi * L + beta + mu
    S2 = mp.pi / mu - 1
    S1 = S0 - mu * S2
    return S0, S1, S2


def F_of(S0, S1, S2):
    d = S2 / S1
    return S0 ** 2 / (mp.pi * S1) - mp.log(d) - mp.log(1 + mp.log(d)), d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--R", type=int, default=3000)
    args = ap.parse_args()
    mp.mp.dps = 40
    ok = True
    beta = beta_const()
    lim = 1 + beta / mp.pi
    print("beta = %s;  (beta + pi)/pi = %s" % (mp.nstr(beta, 15), mp.nstr(lim, 15)))
    # Kronecker limit check: Z(s) - pi/(s-1) -> beta as s -> 1
    chi4 = [0, 1, 0, -1]
    for eps in (mp.mpf("1e-8"), mp.mpf("1e-12")):
        s = 1 + eps
        Z = 4 * mp.zeta(s) * mp.dirichlet(s, chi4)
        print("  Kronecker check: Z(1+%s) - pi/%s = %s" % (mp.nstr(eps, 2), mp.nstr(eps, 2),
                                                         mp.nstr(Z - mp.pi / eps, 15)))
    ok &= abs(4 * mp.zeta(1 + mp.mpf("1e-12")) * mp.dirichlet(1 + mp.mpf("1e-12"), chi4)
              - mp.pi / mp.mpf("1e-12") - beta) < mp.mpf("1e-9")
    print("  Z(0) = %s" % mp.nstr(4 * mp.zeta(0) * mp.dirichlet(0, chi4), 10))

    # corroboration of the certificate's own trial function (truncated at
    # |k| <= 4000, mu = 1221/10000), by an independent float64 lattice sum
    # (row sums in numpy, rows combined with fsum; no tail).  Not rigorous,
    # but float error here is ~1e-13, far below the 4.4e-11 margin.
    def truncated(mu, R):
        p0, p1, p2 = [], [], []
        for a in range(-R, R + 1):
            bmax = math.isqrt(R * R - a * a)
            b = np.arange(-bmax, bmax + 1, dtype=np.float64)
            n = a * a + b * b
            n = n[n > 0]
            q = 1.0 + mu * n
            p0.append(math.fsum((1.0 / (n * q)).tolist()))
            p1.append(math.fsum((1.0 / (n * q * q)).tolist()))
            p2.append(math.fsum((1.0 / (q * q)).tolist()))
        return math.fsum(p0), math.fsum(p1), math.fsum(p2)
    S0, S1, S2 = truncated(0.1221, 4000)
    Ft, dt = F_of(mp.mpf(S0), mp.mpf(S1), mp.mpf(S2))
    print("\nCertificate trial function (|k| <= 4000, mu = 0.1221), independent float64 sums:")
    print("  S0 = %.15f  S1 = %.15f  S2 = %.13f  d = %.12f" % (S0, S1, S2, float(dt)))
    print("  L_trial = %s  (verify/16a: 2.15622477064423579...; claim 2.1562247706)" % mp.nstr(Ft, 15))
    ok &= abs(Ft - mp.mpf("2.15622477064423579")) < mp.mpf("1e-11") and Ft > mp.mpf("2.1562247706")

    print("\nDirect lattice sums (|k| <= %d, plus integral tail) vs the small-mu expansion:" % args.R)
    print("  %-8s %-16s %-16s %-16s %-12s %-12s" % ("mu", "S0 direct", "S0 expansion", "S2 direct",
                                                  "d(mu)", "F(d(mu))"))
    for mu in (0.1221, 0.05, 0.01, 0.003, 0.001):
        S0, S1, S2 = lattice_sums(mu, args.R)
        a0, a1, a2 = asym(mu, beta)
        F, d = F_of(mp.mpf(S0), mp.mpf(S1), mp.mpf(S2))
        print("  %-8g %-16.10f %-16.10f %-16.6f %-12.6f %-12.9f" % (mu, S0, float(a0), S2,
                                                                  float(d), float(F)))
        if mu <= 0.01:
            ok &= abs(S0 - float(a0)) < 1e-6 and abs(S2 - float(a2)) / S2 < 1e-6
        if mu == 0.1221:
            # the page's trial function is the same family truncated at |k| <= 4000
            print("    (the untruncated extremal at mu = 0.1221; the certificate's truncated "
                  "one gives 2.15622477064)")

    print("\nF along the exact extremal family for large d (expansion; exact up to o(mu^M)):")
    print("  %-10s %-14s %-14s" % ("mu", "d(mu)", "F(d(mu))"))
    prev = None
    for e in (3, 4, 6, 8, 12, 20, 40, 100, 1000):
        mu = mp.mpf(10) ** (-e)
        F, d = F_of(*asym(mu, beta))
        print("  1e-%-7d %-14s %-14s" % (e, mp.nstr(d, 6), mp.nstr(F, 10)))
        ok &= F < mp.mpf("2.1562247706")
        if prev is not None:
            ok &= F < prev           # decreasing toward the limit
        prev = F
    print("  limit (beta + pi)/pi = %s" % mp.nstr(lim, 12))
    ok &= lim < mp.mpf("2.1562247706")

    # shape of F over the family (numerical, direct sums): where is the max,
    # and what does a fixed threshold d0 give (reading (b'))?
    print("\nShape of F(d) along the family (direct sums, |k| <= 1500 + tail; numerical):")
    grid = [10 ** (x / 10) for x in range(-30, 6)]          # mu from 1e-3 to ~3.2
    table = []
    for mu in grid:
        S0, S1, S2 = lattice_sums(mu, 1500)
        F, d = F_of(mp.mpf(S0), mp.mpf(S1), mp.mpf(S2))
        table.append((float(d), float(F), mu))
    table.sort()
    for d, F, mu in table[::3]:
        print("  d = %-10.4f F = %.9f   (mu = %.4g)" % (d, F, mu))
    dmax, Fmax, mumax = max(table, key=lambda r: r[1])
    # refine the maximum by golden-section search in log(mu), larger radius
    a, b = math.log(mumax / 1.3), math.log(mumax * 1.3)
    gr = (math.sqrt(5) - 1) / 2

    def negF(lm):
        S0, S1, S2 = lattice_sums(math.exp(lm), args.R)
        return -float(F_of(mp.mpf(S0), mp.mpf(S1), mp.mpf(S2))[0])
    c, e = b - gr * (b - a), a + gr * (b - a)
    fc, fe = negF(c), negF(e)
    for _ in range(18):
        if fc < fe:
            b, e, fe = e, c, fc
            c = b - gr * (b - a)
            fc = negF(c)
        else:
            a, c, fc = c, e, fe
            e = a + gr * (b - a)
            fe = negF(e)
    mu_star = math.exp((a + b) / 2)
    S0, S1, S2 = lattice_sums(mu_star, args.R)
    Fs, ds = F_of(mp.mpf(S0), mp.mpf(S1), mp.mpf(S2))
    print("  max of F over the family (untruncated extremal, numerical): F = %s at d* = %s "
          "(mu = %.5f)" % (mp.nstr(Fs, 10), mp.nstr(ds, 6), mu_star))
    print("  compare: page upper bound 2.1562256466*, BDZ2013 numerical 2.15627 at d* = 3.92888, "
          "certificate trial (truncated) 2.15622477064")
    for d0 in (5, 10, 100):
        sup = max(F for d, F, mu in table if d >= d0)
        print("  reading (b') with threshold d0 = %-3d: sup over the grid of F(d), d >= d0: %.6f"
              % (d0, sup))
        ok &= sup < 2.1562247706
    print("RESULT: %s" % ("ALL CHECKS PASSED" if ok else "SOME CHECK FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
