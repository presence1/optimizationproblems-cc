#!/usr/bin/env python3
"""Independent check of the [Cla2026] lower bounds on C_49 (3-sunflower-free
capacity): 1.5664286* and 1.5666969*.

Everything is rebuilt from the description on constants/49a.md; no file or
code from the certificate repositories is used.

  F: 75 subsets of E(K_5) (10 points): the 5 stars K_{1,4}, the 10 complete
     bipartite K_{2,3}, and the 60 complements of chairs (the tree with
     degree sequence 3,2,1,1,1).
  H: 121 subsets of Z_11: images of {0..6}, {0,1,2,3,4,6,7}, {0,1,2,6,9}
     under x -> a x + b, a a nonzero square mod 11.

Checked exhaustively: sizes, Sperner, 3-sunflower-free, port counts
N_ab = #{S : [u in S] = a, [v in S] = b} for every choice of ports.  Then the
chain bound: XOR-gluing (see README.md for the proof) gives chain families of
size ~ c rho^k on (points added per period) * k + O(1) points, where rho is
the Perron root of the transfer matrix T[a][a'] = N_{a, 1-a'}.  So
C_49 >= rho^(1/8) (F alone) and C_49 >= rho^(1/17) (F, H alternating).
A randomised self-test checks the XOR-gluing lemma by brute force on small
families, and confirms that same-status gluing would not work.

Usage: python3 -I check_c49_cla2026.py [--selftest]
"""

import argparse
import random
import sys
from fractions import Fraction
from itertools import combinations, permutations


# ------------------------------------------------------------ families
def build_F():
    V = range(5)
    E = list(combinations(V, 2))
    idx = {e: i for i, e in enumerate(E)}

    def m(edges):
        s = 0
        for e in edges:
            s |= 1 << idx[tuple(sorted(e))]
        return s

    stars = {m([(v, w) for w in V if w != v]) for v in V}
    k23 = {m([(a, b) for a in S for b in V if b not in S]) for S in combinations(V, 2)}
    chairs = set()
    for c, mid, leaf in permutations(V, 3):       # center, degree-2 vertex, its leaf
        others = [x for x in V if x not in (c, mid, leaf)]
        edges = [(c, mid), (mid, leaf)] + [(c, o) for o in others]
        deg = [sum(1 for e in edges if x in e) for x in V]
        assert sorted(deg) == [1, 1, 1, 2, 3]
        chairs.add(m(edges))
    full = (1 << 10) - 1
    comps = {full ^ ch for ch in chairs}
    assert len(stars) == 5 and len(k23) == 10 and len(chairs) == 60
    F = stars | k23 | comps
    return sorted(F), 10, dict(stars=5, k23=10, chair_complements=len(comps))


def build_H():
    squares = sorted({(x * x) % 11 for x in range(1, 11)})
    assert squares == [1, 3, 4, 5, 9]
    bases = [{0, 1, 2, 3, 4, 5, 6}, {0, 1, 2, 3, 4, 6, 7}, {0, 1, 2, 6, 9}]
    H = set()
    orbit_sizes = []
    for B in bases:
        orb = set()
        for a in squares:
            for b in range(11):
                orb.add(sum(1 << ((a * x + b) % 11) for x in B))
        orbit_sizes.append(len(orb))
        H |= orb
    return sorted(H), 11, dict(orbits=orbit_sizes)


# ------------------------------------------------------------ properties
def is_sperner(fam):
    s = set(fam)
    assert len(s) == len(fam)
    for A in fam:
        for B in fam:
            if A != B and A & B == A:
                return False
    return True


def sunflower_triples(fam):
    """Number of 3-sunflowers (unordered triples of distinct members)."""
    cnt = 0
    for A, B, C in combinations(fam, 3):
        k = A & B
        if A & C == k and B & C == k:
            cnt += 1
    return cnt


def port_counts(fam, u, v):
    N = {(a, b): 0 for a in (0, 1) for b in (0, 1)}
    for S in fam:
        N[((S >> u) & 1, (S >> v) & 1)] += 1
    return N


def all_port_counts(fam, npts):
    seen = set()
    for u in range(npts):
        for v in range(npts):
            if u != v:
                N = port_counts(fam, u, v)
                seen.add(tuple(N[k] for k in ((0, 0), (0, 1), (1, 0), (1, 1))))
    return seen


def transfer(N):
    """T[a][a'] = N_{a, 1-a'}: u-status a of one copy -> u-status a' of the
    next copy, under the XOR rule [v in A_i] + [u in A_{i+1}] = 1."""
    return [[N[(a, 1 - ap)] for ap in (0, 1)] for a in (0, 1)]


def matmul(X, Y):
    return [[sum(X[i][k] * Y[k][j] for k in range(2)) for j in range(2)] for i in range(2)]


def perron_root_arb(T):
    from flint import arb
    tr = T[0][0] + T[1][1]
    det = T[0][0] * T[1][1] - T[0][1] * T[1][0]
    disc = tr * tr - 4 * det
    assert disc > 0 and all(x > 0 for row in T for x in row)
    return (arb(tr) + arb(disc).sqrt()) / 2, tr, det, disc


# ------------------------------------------------------------ gluing lemma test
def glue(F1, n1, u1, v1, F2, n2, u2, rule):
    """Glue F1's port v1 to F2's port u2.  Points of F2 are shifted by n1.
    rule 'xor': exactly one of the two ports present (the merged point then
    lies in every member and is dropped).  rule 'same-keep': both present or
    both absent, merged into one kept point (also valid, but adds one more
    point per copy).  rule 'same-drop': both present or both absent, merged
    point dropped (NOT valid in general; used as a control).
    Returns the family on n1 + n2 points."""
    out = set()
    for A in F1:
        for B in F2:
            a = (A >> v1) & 1
            b = (B >> u2) & 1
            S = (A & ~(1 << v1)) | ((B & ~(1 << u2)) << n1)
            if rule == "xor" and a + b == 1:
                out.add(S)
            elif rule == "same-keep" and a == b:
                out.add(S | (a << v1))
            elif rule == "same-drop" and a == b:
                out.add(S)
    return sorted(out)


def random_sf_sperner(n, tries, rng):
    """Greedy random maximal-ish Sperner sunflower-free family on n points."""
    cand = list(range(1, 1 << n))
    rng.shuffle(cand)
    fam = []
    for S in cand[:tries]:
        ok = all(not (S & T == S or S & T == T) for T in fam)
        if not ok:
            continue
        bad = False
        for A, B in combinations(fam, 2):
            k = A & B
            if S & A == k and S & B == k:
                bad = True
                break
        if not bad:
            fam.append(S)
    return fam


def selftest():
    rng = random.Random(49)
    bad = {"xor": 0, "same-keep": 0, "same-drop": 0}
    trials = 0
    for _ in range(600):
        n1, n2 = rng.randrange(3, 7), rng.randrange(3, 7)
        F1 = random_sf_sperner(n1, 60, rng)
        F2 = random_sf_sperner(n2, 60, rng)
        if len(F1) < 3 or len(F2) < 3:
            continue
        trials += 1
        u1, v1 = rng.sample(range(n1), 2)
        u2 = rng.randrange(n2)
        for rule in bad:
            G = glue(F1, n1, u1, v1, F2, n2, u2, rule)
            if sunflower_triples(G) or not is_sperner(G):
                bad[rule] += 1
    print("selftest: %d random gluings of Sperner sunflower-free families; "
          "failures by rule: %s (control 'same-drop' is expected to fail)" % (trials, bad))
    assert trials > 200 and bad["xor"] == 0 and bad["same-keep"] == 0
    assert bad["same-drop"] > 0
    # sanity of the sunflower test itself
    assert sunflower_triples([0b011, 0b101, 0b110]) == 0         # pairwise {1 elt}, not equal
    assert sunflower_triples([0b001, 0b010, 0b100]) == 1         # disjoint: kernel empty
    print("selftest passed")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        selftest()
        return 0
    from flint import arb, ctx
    ctx.prec = 200
    ok = True
    fams = {}
    for name, builder, expect in (("F", build_F, 75), ("H", build_H, 121)):
        fam, npts, info = builder()
        sp = is_sperner(fam)
        sf = sunflower_triples(fam)
        pcs = all_port_counts(fam, npts)
        sizes = sorted({bin(S).count("1") for S in fam})
        print("%s: %d sets on %d points %s, set sizes %s" % (name, len(fam), npts, info, sizes))
        print("   Sperner: %s; 3-sunflowers among all %d triples: %d" % (
            sp, len(fam) * (len(fam) - 1) * (len(fam) - 2) // 6, sf))
        print("   port counts (N00, N01, N10, N11) over all ordered port pairs: %s" % sorted(pcs))
        ok &= len(fam) == expect and sp and sf == 0 and len(pcs) == 1
        fams[name] = dict(zip(((0, 0), (0, 1), (1, 0), (1, 1)), next(iter(pcs))))
    NF, NH = fams["F"], fams["H"]
    ok &= (NF[(1, 0)], NF[(1, 1)], NF[(0, 0)], NF[(0, 1)]) == (20, 24, 11, 20)
    ok &= (NH[(1, 0)], NH[(1, 1)], NH[(0, 0)], NH[(0, 1)]) == (31, 44, 15, 31)
    print("port counts match the page's rows (20,24),(11,20) and (31,44),(15,31): %s" % ok)

    TF, TH = transfer(NF), transfer(NH)
    rhoF, tr, det, disc = perron_root_arb(TF)
    bF = rhoF ** (arb(1) / 8)
    print("F chain: T = %s, x^2 - %dx + %d, rho = (%d + sqrt(%d))/2 = 20 + 2 sqrt(66): %s" % (
        TF, tr, det, tr, disc, disc == 4 * 264))
    print("   rho^(1/8) = %s" % bF.str(20))
    c1 = bool(arb(15664286) / 10**7 < bF)
    print("   -> C_49 >= 1.5664286 (row 77): %s" % c1)
    TP = matmul(TF, TH)
    rhoP, tr, det, disc = perron_root_arb(TP)
    bP = rhoP ** (arb(1) / 17)
    print("F,H alternating: T_F T_H = %s, x^2 - %dx + %d; page's matrix rows "
          "(980,1624),(641,1104) has the same trace/det: %s" % (
              TP, tr, det, (tr, det) == (980 + 1104, 980 * 1104 - 1624 * 641)))
    print("   rho = (%d + sqrt(%d))/2 = 1042 + 2 sqrt(261207): %s" % (
        tr, disc, (tr, disc) == (2084, 16 * 261207)))
    print("   rho^(1/17) = %s" % bP.str(20))
    c2 = bool(arb(15666969) / 10**7 < bP)
    print("   -> C_49 >= 1.5666969 (row 78): %s" % c2)
    ok &= c1 and c2
    print("RESULT: %s" % ("CONFIRMED (given the XOR-gluing chain lemma, proved in README)"
                          if ok else "NOT CONFIRMED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
