#!/usr/bin/env python3
"""Auditor's independent checks for the C_70 row [Pin2026] (>= 1.20194336*).

No code is shared with verify/70a or with the certificate authors.

Part A  -- the two classical inputs of Patankar's criterion, tested in low
           dimension (they are theorems; these are sanity checks that the
           formulas are used with the right normalisation):
  A1. Steiner's formula + the zonotope intrinsic-volume formula
      |P + rB| = sum_j V_j(P) kappa_{n-j} r^{n-j},
      V_j(P) = sum_{|S|=j} vol_j(v_S),
      for random parallelotopes P in R^2 and R^3, against a Monte Carlo
      estimate of |P + rB| using an exact point-to-parallelotope distance.
  A2. The Szasz + AM-GM step V_j(uK) >= C(n,j) a^j for random u with
      |det u| = 1 (n = 2..7, including badly conditioned u).
Part B  -- a third enclosure of R_{n,k} at the certificate's parameters,
           using only Python's standard library: decimal.Decimal (whose ln
           and exp are correctly rounded) and Robbins' factorial bounds,
           with pi from Machin's formula.  The literal criterion
           (C(n,k) a^(n-k) kappa_k)^(1/n) / (a + kappa_n^(1/n)) is also
           compared with the closed form at moderate n using exact
           factorials (n = 1000, 10^4).
Part C  -- the page's two side statements: the n = 2 closed form and the
           limit exp(1/(2e)).

Usage: python3 -I c70_independent.py [--mc N]
"""

import argparse
import itertools
import math
import sys
from decimal import Decimal, getcontext, localcontext
from fractions import Fraction

import numpy as np

N_CERT = 10**12
K_CERT = 367879441172
CLAIM = Fraction("1.20194336")


# ------------------------------------------------------------------ Part A
def kappa(m):
    return math.pi ** (m / 2) / math.gamma(1 + m / 2)


def intrinsic_volumes_parallelotope(V):
    """V: n x n matrix whose columns are the generators."""
    n = V.shape[1]
    out = [1.0]
    for j in range(1, n + 1):
        s = 0.0
        for S in itertools.combinations(range(n), j):
            M = V[:, S]
            s += math.sqrt(max(np.linalg.det(M.T @ M), 0.0))
        out.append(s)
    return out


def dist_to_parallelotope(V, pts):
    """Exact Euclidean distance from each row of pts to {V c : c in [0,1]^n}:
    minimise |V c - p| over the box by enumerating, for every coordinate,
    'fixed at 0', 'fixed at 1' or 'free', solving least squares on the free
    ones and keeping feasible candidates (the optimum is among them)."""
    n = V.shape[1]
    best = np.full(len(pts), np.inf)
    for pattern in itertools.product((0, 1, 2), repeat=n):     # 2 = free
        free = [i for i in range(n) if pattern[i] == 2]
        fixed = np.array([pattern[i] if pattern[i] != 2 else 0 for i in range(n)], float)
        base = V @ fixed
        rhs = pts - base
        if free:
            Vf = V[:, free]
            G = Vf.T @ Vf
            coef = np.linalg.solve(G, Vf.T @ rhs.T).T             # (N, |free|)
            feas = np.all((coef >= -1e-12) & (coef <= 1 + 1e-12), axis=1)
            res = rhs - coef @ Vf.T
        else:
            feas = np.ones(len(pts), bool)
            res = rhs
        d = np.sqrt((res * res).sum(axis=1))
        d[~feas] = np.inf
        best = np.minimum(best, d)
    return best


def check_steiner_mc(n, r, Nmc, rng):
    V = rng.normal(size=(n, n))
    corners = np.array([V @ np.array(c, float) for c in itertools.product((0, 1), repeat=n)])
    lo, hi = corners.min(axis=0) - r, corners.max(axis=0) + r
    box = float(np.prod(hi - lo))
    hits = 0
    done = 0
    while done < Nmc:
        m = min(200000, Nmc - done)
        pts = lo + (hi - lo) * rng.random((m, n))
        hits += int((dist_to_parallelotope(V, pts) <= r).sum())
        done += m
    p = hits / Nmc
    est = box * p
    se = box * math.sqrt(p * (1 - p) / Nmc)
    Vj = intrinsic_volumes_parallelotope(V)
    pred = sum(Vj[j] * kappa(n - j) * r ** (n - j) for j in range(n + 1))
    # a plausible wrong normalisation, to show the test can tell: V_j halved for 0<j<n
    wrong = sum((Vj[j] / (2 if 0 < j < n else 1)) * kappa(n - j) * r ** (n - j) for j in range(n + 1))
    return est, se, pred, wrong


def int_det(M):
    """Exact determinant of a square integer matrix (fraction-free Bareiss)."""
    M = [list(r) for r in M]
    n = len(M)
    sign, prev = 1, 1
    for k in range(n - 1):
        if M[k][k] == 0:
            sw = next((i for i in range(k + 1, n) if M[i][k] != 0), None)
            if sw is None:
                return 0
            M[k], M[sw] = M[sw], M[k]
            sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                M[i][j] = (M[i][j] * M[k][k] - M[i][k] * M[k][j]) // prev
        prev = M[k][k]
    return sign * M[n - 1][n - 1]


def random_unimodular(n, rng):
    U = [[int(i == j) for j in range(n)] for i in range(n)]
    for _ in range(4 * n):
        i, j = rng.choice(n, 2, replace=False)
        c = int(rng.integers(-2, 3))
        U[i] = [U[i][q] + c * U[j][q] for q in range(n)]
        if rng.random() < 0.2:
            U[i], U[j] = U[j], U[i]
    return U


def check_szasz(rng, trials=300):
    """V_j(uK)/(C(n,j) a^j) >= 1 for |det u| = 1.  The ratio does not depend
    on a, so a = 1.  Exact part: random unimodular INTEGER u (det = +-1
    exactly, Gram determinants exact, square roots summed in 50-digit
    Decimal).  Float part: well-conditioned real u, volumes from QR."""
    worst_exact = Decimal("Infinity")
    with localcontext() as ctx:
        ctx.prec = 50
        for _ in range(trials):
            n = int(rng.integers(2, 8))
            U = random_unimodular(n, rng)
            assert abs(int_det(U)) == 1
            cols = [[U[r][c] for r in range(n)] for c in range(n)]
            for j in range(1, n + 1):
                s = Decimal(0)
                for S in itertools.combinations(range(n), j):
                    G = [[sum(x * y for x, y in zip(cols[p], cols[q])) for q in S] for p in S]
                    g = int_det(G)
                    assert g > 0
                    s += Decimal(g).sqrt()
                worst_exact = min(worst_exact, s / math.comb(n, j))
    worst_float = math.inf
    for _ in range(trials):
        n = int(rng.integers(2, 8))
        Q, _ = np.linalg.qr(rng.normal(size=(n, n)))
        D = np.diag(np.exp(rng.uniform(-1, 1, size=n)))
        U = Q @ D @ np.linalg.qr(rng.normal(size=(n, n)))[0]        # cond <= e^2
        U /= abs(np.linalg.det(U)) ** (1.0 / n)
        for j in range(1, n + 1):
            s = 0.0
            for S in itertools.combinations(range(n), j):
                R = np.linalg.qr(U[:, S], mode="r")
                s += abs(float(np.prod(np.diag(R))))
            worst_float = min(worst_float, s / math.comb(n, j))
    eq = intrinsic_volumes_parallelotope(1.7 * np.eye(4))
    eq_ok = all(abs(eq[j] - math.comb(4, j) * 1.7 ** j) < 1e-9 for j in range(5))
    return worst_exact, worst_float, eq_ok


# ------------------------------------------------------------------ Part B
def pi_machin(prec):
    with localcontext() as ctx:
        ctx.prec = prec + 10

        def arctan_inv(x):
            x = Decimal(x)
            term = 1 / x
            s, k, x2 = term, 1, x * x
            eps = Decimal(10) ** (-(prec + 5))
            while True:
                term /= -x2
                t = term / (2 * k + 1)
                if abs(t) < eps:
                    break
                s += t
                k += 1
            return s
        return +(16 * arctan_inv(5) - 4 * arctan_inv(239))


def robbins(m, half_ln_2pi):
    """(lower, upper) for ln(m!), m >= 1, Decimal."""
    m = Decimal(m)
    base = (m + Decimal("0.5")) * m.ln() - m + half_ln_2pi
    return base + 1 / (12 * m + 1), base + 1 / (12 * m)


def enclose_R(n, k, prec=80):
    """[lo, hi] for R_{n,k} = exp(log R), log R by the closed form with
    Robbins bounds; every Decimal ln/exp/division is correctly rounded to
    `prec` digits, and a margin far larger than the accumulated rounding is
    added to each end."""
    with localcontext() as ctx:
        ctx.prec = prec
        PI = pi_machin(prec)
        h = (2 * PI).ln() / 2
        lf = {m: robbins(m, h) for m in (n, k, n - k, n // 2, k // 2)}
        t = Decimal(k) / Decimal(n)
        nn = Decimal(n)
        common = (1 - t) * (1 - t).ln() + t * t.ln()
        # coefficients: +1/n ln n!, -1/n ln k!, -1/n ln (n-k)!, +t/n ln (n/2)!, -1/n ln (k/2)!
        lo = common + (lf[n][0] - lf[k][1] - lf[n - k][1] + t * lf[n // 2][0] - lf[k // 2][1]) / nn
        hi = common + (lf[n][1] - lf[k][0] - lf[n - k][0] + t * lf[n // 2][1] - lf[k // 2][0]) / nn
        margin = Decimal(10) ** (-(prec - 30))
        return (lo - margin).exp() * (1 - margin), (hi + margin).exp() * (1 + margin)


def literal_vs_closed(n, k, prec=60):
    """Exact-factorial evaluation of the literal criterion and of the closed
    form at moderate even n, k; returns both (Decimal)."""
    with localcontext() as ctx:
        ctx.prec = prec
        PI = pi_machin(prec)

        def ln_kappa(m):     # m even: kappa_m = pi^(m/2) / (m/2)!
            return Decimal(m) / 2 * PI.ln() - Decimal(math.factorial(m // 2)).ln()
        lkn = ln_kappa(n) / n
        ln_a = (Decimal(n - k) / Decimal(k)).ln() + lkn
        ln_term = Decimal(math.comb(n, k)).ln() + (n - k) * ln_a + ln_kappa(k)
        lit = ln_term / n - (ln_a.exp() + lkn.exp()).ln()
        t = Decimal(k) / Decimal(n)
        closed = ((Decimal(math.factorial(n)).ln() - Decimal(math.factorial(k)).ln()
                   - Decimal(math.factorial(n - k)).ln() - Decimal(math.factorial(k // 2)).ln()
                   + t * Decimal(math.factorial(n // 2)).ln()) / n
                  + (1 - t) * (1 - t).ln() + t * t.ln())
        return lit.exp(), closed.exp()


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mc", type=int, default=2_000_000)
    ap.add_argument("--mc-repeats", type=int, default=0,
                    help="extra seeded MC runs (e.g. 16) to check the z-score distribution")
    args = ap.parse_args()
    ok = True
    rng = np.random.default_rng(70)
    print("== Part A: Steiner + zonotope formula (Monte Carlo), Szasz + AM-GM")
    for n in (2, 3):
        for r in (0.3, 1.0):
            est, se, pred, wrong = check_steiner_mc(n, r, args.mc, rng)
            z = (est - pred) / se
            zw = (est - wrong) / se
            print("  n=%d r=%.1f: MC |P+rB| = %.5f +/- %.5f; Steiner+zonotope %.5f (z = %+.2f); "
                  "a wrong normalisation gives %.5f (z = %+.1f)" % (n, r, est, se, pred, z, wrong, zw))
            ok &= abs(z) < 4.5 and abs(zw) > 6
    if args.mc_repeats:
        zs = []
        for seed in range(1, args.mc_repeats // 2 + 1):
            rr = np.random.default_rng(1000 + seed)
            for n in (2, 3):
                est, se, pred, wrong = check_steiner_mc(n, 0.7, args.mc, rr)
                zs.append((est - pred) / se)
        print("  %d further independent MC runs (r = 0.7, n = 2, 3): z-scores mean %+.2f, sd %.2f, "
              "max |z| %.2f" % (len(zs), float(np.mean(zs)), float(np.std(zs)), max(map(abs, zs))))
        ok &= abs(float(np.mean(zs))) < 1.0 and max(map(abs, zs)) < 4.5
    worst_exact, worst_float, eq_ok = check_szasz(rng)
    print("  Szasz+AM-GM: min of V_j(uK)/(C(n,j) a^j) over 300 random unimodular integer u "
          "(exact Gram determinants) = %s; over 300 well-conditioned real u (QR) = %.15f; "
          "must be >= 1; equality at u = I: %s" % (str(worst_exact)[:12], worst_float, eq_ok))
    ok &= worst_exact >= 1 and worst_float >= 1 - 1e-12 and eq_ok

    print("== Part B: third enclosure (stdlib decimal + Robbins), literal vs closed form")
    getcontext().prec = 80
    PI = pi_machin(60)
    ok &= str(PI).startswith("3.14159265358979323846264338327950288419716939937510")
    for n, k in ((1000, 368), (10000, 3678)):
        lit, clo = literal_vs_closed(n, k)
        print("  n=%d k=%d: literal %s, closed form %s, |diff| = %.1e"
              % (n, k, str(lit)[:30], str(clo)[:30], float(abs(lit - clo))))
        ok &= abs(lit - clo) < Decimal(10) ** -45
    lo, hi = enclose_R(N_CERT, K_CERT)
    c = Decimal(CLAIM.numerator) / Decimal(CLAIM.denominator)
    print("  R(10^12, 367879441172) in [%s, %s]" % (str(lo)[:42], str(hi)[:42]))
    print("  width %.2e; claim 1.20194336 < lower end: %s (margin %.3e)"
          % (float(hi - lo), lo > c, float(lo - c)))
    ok &= lo > c and hi - lo < Decimal(10) ** -30
    # the same machinery must REJECT a claim just above R and the limit value
    for bad in ("1.2019433685", "1.20194336847"):
        rejected = not (lo > Decimal(bad))
        print("  control: claim %s is rejected: %s" % (bad, rejected))
        ok &= rejected
    for kk in (K_CERT - 2, K_CERT + 2, 300000000000, 450000000000):
        l2, h2 = enclose_R(N_CERT, kk, prec=60)
        print("  (info) k = %d: R in [%s, %s]" % (kk, str(l2)[:24], str(h2)[:24]))

    print("== Part C: side statements on the page")
    with localcontext() as ctx:
        ctx.prec = 50
        PI = pi_machin(50)
        r2 = (Decimal("0.5") + 1 / PI.sqrt()).sqrt()
        # n = 2: maximise (a^2 + 4a + pi)/(a + sqrt(pi))^2 over a > 0: at a = sqrt(pi)
        grid = max(((Decimal(s) / 100) ** 2 * PI + 4 * (Decimal(s) / 100) * PI.sqrt() + PI)
                   / (PI * (Decimal(s) / 100 + 1) ** 2) for s in range(1, 1000))
        print("  n=2: sqrt(1/2 + 1/sqrt(pi)) = %s; grid max of the n=2 ratio^2 = %s (= %s)"
              % (str(r2)[:12], str(grid.sqrt())[:12], str(r2)[:12]))
        ok &= abs(grid.sqrt() - r2) < Decimal("1e-12")
        lim = (1 / (2 * Decimal(1).exp())).exp()
        print("  exp(1/(2e)) = %s > 1.20194336847: %s" % (str(lim)[:24], lim > Decimal("1.20194336847")))
        ok &= lim > Decimal("1.20194336847")
    print("RESULT: %s" % ("ALL CHECKS PASSED" if ok else "SOME CHECK FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
