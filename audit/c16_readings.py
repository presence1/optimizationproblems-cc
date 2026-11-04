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
             Then L is admissible iff F(d) <= L for all large d.
[BDZ2013] (arXiv:1012.2061v1), Theorem 3.8, uses reading (a): inequality
(3.19) for all zero-mean 2pi-periodic u, L := max_{d>=1}[...] as in (3.20).

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
F -> 1 + beta/pi = (beta + pi)/pi = 1.82282525... from above (BDZ's L_inf):
under reading (b) every L > (beta+pi)/pi is admissible and none smaller, so
the best constant is the infimum (beta+pi)/pi (not attained), the page's own
[BDZ2013] lower bound, and 2.1562247706 is NOT a lower bound.  This script
checks the expansions against direct lattice sums (with integral tails),
checks the Kronecker constant numerically, tabulates F along the family, and
compares with BDZ's own formulas and numbers (bdz_comparison below).

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
    ok &= bdz_comparison(beta)
    print("RESULT: %s" % ("ALL CHECKS PASSED" if ok else "SOME CHECK FAILED"))
    return 0 if ok else 1


# --------------------------------------------------------------------------
# Comparison with [BDZ2013] (Bartuccelli-Deane-Zelik, arXiv:1012.2061v1):
# their Theorem 3.8 defines L = max_{d>=1} [4 pi Theta(d) - ln d - ln(1+ln d)]
# for ALL zero-mean 2pi-periodic u, and reports (p. 13, numerically)
# d* ~ 3.92888 (mu ~ 0.12211) and L ~ 2.15627; Theta(1), Theta(2), Theta(4)
# = 0.10134, 0.26651, 0.35112 and Theta_0 = 0.17797, 0.26660, 0.35112 (p. 4).
# Here the lattice sums are evaluated by Poisson summation (their Lemma 3.1
# and Remark 3.6), which converges exponentially:
#   h = S2 = pi/mu - 1 + 2 pi^2 mu^(-3/2) sum' |m| K1(2 pi |m| / sqrt(mu))
#   f = S0 = pi ln(1/mu) + beta + mu - 2 pi sum' K0(2 pi |m| / sqrt(mu))
#   g = S1 = f - mu h.
# (Remark 3.6 prints the coefficient of the K0 series as 8 pi; 2 pi is what
# integrating the h series gives, matches their (3.7), and matches the direct
# lattice sums -- checked below.)
# --------------------------------------------------------------------------
_R2 = {}


def r2_upto(N):
    """r2[n] = #{m in Z^2 : |m|^2 = n}, 1 <= n <= N (cached)."""
    if N not in _R2:
        r = {}
        q = math.isqrt(N)
        for m1 in range(-q, q + 1):
            for m2 in range(-q, q + 1):
                n = m1 * m1 + m2 * m2
                if 0 < n <= N:
                    r[n] = r.get(n, 0) + 1
        _R2[N] = sorted(r.items())
    return _R2[N]


def bessel_sums(mu, beta, c0=2):
    """S0, S1, S2 by the exponentially convergent Bessel series; the lattice
    sum over m != 0 is grouped by n = |m|^2 with multiplicity r2(n)."""
    mu = mp.mpf(mu)
    a = 2 * mp.pi / mp.sqrt(mu)
    M = int(mp.ceil(mp.mpf(mp.mp.dps) * 2.4 / a)) + 2       # K(a M) < 10^-dps
    sK0 = sK1 = mp.mpf(0)
    for n, mult in r2_upto(M * M):
        r = mp.sqrt(n)
        sK0 += mult * mp.besselk(0, a * r)
        sK1 += mult * r * mp.besselk(1, a * r)
    h = mp.pi / mu - 1 + 2 * mp.pi ** 2 * mu ** mp.mpf(-1.5) * sK1
    f = mp.pi * mp.log(1 / mu) + beta + mu - c0 * mp.pi * sK0
    g = f - mu * h
    return f, g, h


def bisect_mu(target_d, beta, lo=mp.mpf("0.02"), hi=mp.mpf("2.5"), it=60):
    """mu > 0 with d(mu) = S2/S1 = target_d (d decreases in mu), by bisection in log mu."""
    a, b = mp.log(lo), mp.log(hi)
    for _ in range(it):
        m = (a + b) / 2
        f, g, h = bessel_sums(mp.exp(m), beta)
        if h / g > target_d:
            a = m
        else:
            b = m
    return mp.exp((a + b) / 2)


def bdz_comparison(beta):
    ok = True
    mp.mp.dps = 30
    print("\nComparison with [BDZ2013], arXiv:1012.2061v1 (lattice sums by Poisson/Bessel series):")
    # (1) the Bessel series against the direct lattice sums, and the 8 pi question
    S0d, S1d, S2d = lattice_sums(0.1221, 3000)
    f2, g2, h2 = bessel_sums(mp.mpf("0.1221"), beta, c0=2)
    f8, _, _ = bessel_sums(mp.mpf("0.1221"), beta, c0=8)
    print("  mu = 0.1221: S0 direct %.10f | series with 2 pi: %s | with 8 pi (as printed in "
          "Remark 3.6): %s" % (S0d, mp.nstr(f2, 11), mp.nstr(f8, 11)))
    print("               S2 direct %.7f | series: %s" % (S2d, mp.nstr(h2, 11)))
    ok &= abs(f2 - S0d) < 2e-9 and abs(f8 - S0d) > 1e-7 and abs(h2 - S2d) / h2 < 1e-8

    def Fmu(lm):
        f, g, h = bessel_sums(mp.exp(lm), beta)
        d = h / g
        return f * f / (mp.pi * g) - mp.log(d) - mp.log(1 + mp.log(d)), d, f, g
    # (2) the maximum, by golden-section search in log(mu)
    a, b = mp.log(mp.mpf("0.10")), mp.log(mp.mpf("0.15"))
    gr = (mp.sqrt(5) - 1) / 2
    c, e = b - gr * (b - a), a + gr * (b - a)
    fc, fe = Fmu(c)[0], Fmu(e)[0]
    for _ in range(45):
        if fc > fe:
            b, e, fe = e, c, fc
            c = b - gr * (b - a)
            fc = Fmu(c)[0]
        else:
            a, c, fc = c, e, fe
            e = a + gr * (b - a)
            fe = Fmu(e)[0]
    lm = (a + b) / 2
    Lopt, dstar, _, _ = Fmu(lm)
    print("  L = max F = %s at d* = %s, mu* = %s" % (mp.nstr(Lopt, 15), mp.nstr(dstar, 8),
                                                     mp.nstr(mp.exp(lm), 8)))
    print("  BDZ (p. 13): L ~ 2.15627 at d* ~ 3.92888 (mu ~ 0.12211).  Difference in L: %s"
          % mp.nstr(mp.mpf("2.15627") - Lopt, 3))
    print("  page: certificate lower bound 2.1562247706 < L: %s;  upper bound 2.1562256466 > L: %s"
          % (Lopt > mp.mpf("2.1562247706"), Lopt < mp.mpf("2.1562256466")))
    ok &= mp.mpf("2.1562247706") < Lopt < mp.mpf("2.1562256466")
    ok &= abs(dstar - mp.mpf("3.92888")) < mp.mpf("1e-4")
    # (3) BDZ's table of Theta and Theta_0 at d = 1, 2, 4
    print("  Theta(d) and Theta_0(d) (BDZ p. 4 values in brackets):")
    print("    d = 1: Theta = 1/pi^2 = %s exactly (only |k| = 1 modes)  [BDZ 0.10134]"
          % mp.nstr(1 / mp.pi ** 2, 8))
    for dt, bdz_t, bdz_t0 in ((2, "0.26651", "0.26660"), (4, "0.35112", "0.35112")):
        mu = bisect_mu(dt, beta)
        f, g, h = bessel_sums(mu, beta)
        th = f * f / (4 * mp.pi ** 2 * g)
        # Theta_0 at the same d: bisection on the asymptotic family (1.14)
        a0, b0 = mp.log(mp.mpf("0.02")), mp.log(mp.mpf("2.5"))
        for _ in range(60):
            x = (a0 + b0) / 2
            d0 = (mp.pi / mp.exp(x) - 1) / (mp.pi * (-x) + beta - mp.pi + 2 * mp.exp(x))
            if d0 > dt:
                a0 = x
            else:
                b0 = x
        lm0 = (a0 + b0) / 2
        mu0 = mp.exp(lm0)
        th0 = (mp.pi * (-lm0) + beta + mu0) ** 2 / (4 * mp.pi ** 2 * (mp.pi * (-lm0) + beta - mp.pi + 2 * mu0))
        print("    d = %d: Theta = %s [BDZ %s], Theta_0 = %s [BDZ %s], mu = %s"
              % (dt, mp.nstr(th, 8), bdz_t, mp.nstr(th0, 8), bdz_t0, mp.nstr(mu, 6)))
        ok &= abs(th - mp.mpf(bdz_t)) < mp.mpf("1e-4") and th <= th0
    return ok


if __name__ == "__main__":
    sys.exit(main())
