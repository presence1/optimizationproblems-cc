#!/usr/bin/env python3
"""Independent check of the [Syl2026] lower bounds on C_49: 1.5675517* and
1.5678015* (constants/49a.md rows 79 and 80).

Uses the families F, H rebuilt from the page by check_c49_cla2026.py (same
directory) and the XOR-gluing lemma proved in README.md.

Row 79 (1.5675517*): pure gluing, so goodness (Sperner + sunflower-free)
follows from the lemma; the checker recomputes the gadget/unit port counts
from F and H alone (counts multiply over glued pendants) and the bound
rho^(1/60).  The 62-point unit (about 1.1e12 sets) is NOT enumerated; its
goodness rests on the lemma alone.

Row 80 (1.5678015*): B' = B + 15 sets, where B = glue(F at edge (0,3),
H at 0).  The checker rebuilds B itself, compares it with data/B.txt, checks
that data/Bprime.txt is B plus 15 sets with no H-point, then checks B'
exhaustively (Sperner, and no 3-sunflower: for every pair A, B there is no
third member C with C n (A u B) = A n B), recomputes the port counts and the
bound rho^(1/17).

Every comparison with the page is ENFORCED: the run fails (exit status 1,
"NOT CONFIRMED") if any of them disagrees.  These are the gadget and unit
counts, point counts, port counts, the closed-form Perron roots (compared in
exact integer arithmetic), and the leading digits the page prints.

Usage: python3 -I check_c49_syl2026.py --data DIR   (DIR has B.txt, Bprime.txt)
"""

import argparse
import hashlib
import os
import sys
import time

sys.dont_write_bytecode = True  # do not leave __pycache__ next to the scripts
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # own helper module
from check_c49_cla2026 import build_F, build_H, is_sperner  # noqa: E402

PINNED = {  # data/ files of xSyllaa/sunflower-pendant-chain @ 8e21d02
    "B.txt": "340cef5e71124ed624425abf81e9621839406cbf44b3fd242594d8edcb7d37af",
    "Bprime.txt": "2a72385704b8203269cda4f4b0dfdabc74d5adb8f4a2bc1dac1f570cb96b5cec",
}


def counts_at(fam, p):
    """(# avoiding p, # containing p)."""
    c = sum((S >> p) & 1 for S in fam)
    return len(fam) - c, c


def w_factor(partner_counts, status):
    """Number of partner members compatible with a member whose glued point
    has the given status under the XOR rule: partner must have 1 - status."""
    avoid, contain = partner_counts
    return avoid if status else contain


def read_family(path):
    fam = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        pts = [int(x) for x in line.split()]
        assert len(set(pts)) == len(pts) and all(0 <= x < 64 for x in pts)
        fam.append(sum(1 << x for x in pts))
    return fam


def sunflower_free_exhaustive(fam, npts):
    """Return None if no 3-sunflower, else a witness (i, j, bitset of k)."""
    m = len(fam)
    ALL = (1 << m) - 1
    CONT = [0] * npts
    for i, S in enumerate(fam):
        for e in range(npts):
            if (S >> e) & 1:
                CONT[e] |= 1 << i
    NOT = [ALL ^ c for c in CONT]
    bitlist = {}

    def bits(x):
        r = bitlist.get(x)
        if r is None:
            r = bitlist[x] = [e for e in range(npts) if (x >> e) & 1]
        return r

    for i in range(m):
        A = fam[i]
        for j in range(i + 1, m):
            B = fam[j]
            cand = ALL
            for e in bits(A ^ B):          # C must avoid the symmetric difference
                cand &= NOT[e]
                if not cand:
                    break
            if not cand:
                continue
            for e in bits(A & B):          # and contain the common part
                cand &= CONT[e]
                if not cand:
                    break
            if cand:
                return (i, j, cand)
    return None


def perron(N):
    from flint import arb
    # T[a][a'] = N_{a, 1-a'}; trace = N01 + N10, det = N01 N10 - N00 N11
    tr = N[(0, 1)] + N[(1, 0)]
    det = N[(0, 1)] * N[(1, 0)] - N[(0, 0)] * N[(1, 1)]
    return (arb(tr) + arb(tr * tr - 4 * det).sqrt()) / 2, tr, det


def closed_form(tr, det):
    """(tr, disc) for rho = (tr + sqrt(disc)) / 2, exact integers."""
    return tr, tr * tr - 4 * det


def port_counts(fam, u, v):
    N = {(a, b): 0 for a in (0, 1) for b in (0, 1)}
    for S in fam:
        N[((S >> u) & 1, (S >> v) & 1)] += 1
    return N


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    args = ap.parse_args()
    from flint import arb, ctx
    ctx.prec = 200
    F, _, _ = build_F()   # points 0..9 = K5 edges in lexicographic order
    H, _, _ = build_H()   # points 0..10 = Z_11
    # Validate the bitset search (valid for Sperner families of distinct sets,
    # which is checked separately) against brute force over all triples.
    import random
    from itertools import combinations
    assert sunflower_free_exhaustive(F, 10) is None
    assert sunflower_free_exhaustive(H, 11) is None
    assert sunflower_free_exhaustive([0b000011, 0b001100, 0b110000], 6) is not None
    rng = random.Random(80)
    n_pos = 0
    for _ in range(400):
        n, k = rng.randrange(5, 9), rng.randrange(2, 5)
        layer = [sum(1 << x for x in c) for c in combinations(range(n), k)]
        fam = rng.sample(layer, rng.randrange(3, min(len(layer), 14) + 1))
        brute = any((A & B) == (A & C) == (B & C) for A, B, C in combinations(fam, 3))
        assert (sunflower_free_exhaustive(fam, n) is not None) == brute
        n_pos += brute
    assert 50 < n_pos < 390
    print("bitset sunflower search agrees with brute force on F, H and 400 random "
          "uniform families (%d containing a sunflower)" % n_pos)
    hc = counts_at(H, 0)
    print("H at point 0: (avoid, contain) = %s" % (hc,))
    ok = True
    checks = []   # every comparison with the page; all must hold

    def page_check(desc, cond):
        cond = bool(cond)
        checks.append((desc, cond))
        print("        page check: %-76s %s" % (desc, "OK" if cond else "MISMATCH"))
        return cond

    # ---------------- row 79: gadget G and the 62-point unit (pure gluing)
    # G = F with H glued at F-points 4 = (1,2) and 6 = (1,4); root F-point 0.
    G = [0, 0]  # (avoiding root, containing root)
    for A in F:
        G[(A >> 0) & 1] += w_factor(hc, (A >> 4) & 1) * w_factor(hc, (A >> 6) & 1)
    G = tuple(G)
    g_pts = 10 + 2 * (11 - 2)            # each gluing merges two points and drops them
    unit_pts = 10 + 2 * (g_pts - 2)
    per_unit = unit_pts - 2               # the chain glues the unit's two ports
    print("row 79: gadget G: %d sets on %d points, (avoid, contain root) = %s" % (
        sum(G), g_pts, G))
    page_check("gadget G: 250659 sets, 98308 avoiding and 152351 containing the root",
         (sum(G), G) == (250659, (98308, 152351)))
    page_check("gadget G has 28 points; the unit has 62 points, 60 added per unit",
         (g_pts, unit_pts, per_unit) == (28, 62, 60))
    # unit: core F, ports 0 = (0,1) in and 1 = (0,2) out, G glued at core 2 and 3
    N = {(a, b): 0 for a in (0, 1) for b in (0, 1)}
    for A in F:
        N[((A >> 0) & 1, (A >> 1) & 1)] += (w_factor(G, (A >> 2) & 1)
                                            * w_factor(G, (A >> 3) & 1))
    page = {(0, 0): 148811965456, (0, 1): 279351870092, (1, 0): 279351870092,
            (1, 1): 378843386627}
    print("        unit (62 points) port counts %s" % (dict(sorted(N.items())),))
    page_check("unit port counts N00, N01 = N10, N11 equal the page's", N == page)
    rho, tr, det = perron(N)
    b79 = rho ** (arb(1) / per_unit)
    # page: rho = N01 + sqrt(N11 N00) = (2 N01 + sqrt(4 N11 N00)) / 2
    page_check("rho = N01 + sqrt(N11 N00) (exact: trace 2 N01, discriminant 4 N11 N00)",
               closed_form(tr, det) == (2 * page[(0, 1)], 4 * page[(1, 1)] * page[(0, 0)]))
    print("        rho = %s; rho^(1/60) = %s" % (rho.str(25), b79.str(20)))
    page_check("rho^(1/60) < 1.5675518, as the printed digits 1.5675517... say",
               b79 < arb(15675518) / 10**7)
    c79 = bool(arb(15675517) / 10**7 < b79)
    print("        -> C_49 >= 1.5675517: %s" % c79)
    ok &= c79

    # ---------------- row 80: B and B'
    paths = {k: os.path.join(args.data, k) for k in PINNED}
    for k, p in paths.items():
        dig = hashlib.sha256(open(p, "rb").read()).hexdigest()
        print("%s sha256 %s %s" % (k, dig, "matches" if dig == PINNED[k] else "MISMATCH"))
        ok &= dig == PINNED[k]
    # rebuild B: XOR-glue F at point 2 = edge (0,3) with H at point 0; drop
    # the merged point; F points 0,1,3..9 -> 0..8; H points 1..10 -> 9..18
    fmap = {p: i for i, p in enumerate([0, 1, 3, 4, 5, 6, 7, 8, 9])}
    myB = set()
    for A in F:
        for Bh in H:
            if ((A >> 2) & 1) + (Bh & 1) == 1:
                S = 0
                for p, q in fmap.items():
                    if (A >> p) & 1:
                        S |= 1 << q
                for h in range(1, 11):
                    if (Bh >> h) & 1:
                        S |= 1 << (8 + h)
                myB.add(S)
    theirB = read_family(paths["B.txt"])
    sameB = set(theirB) == myB and len(theirB) == len(myB)
    print("row 80: my rebuild of B has %d sets; equals data/B.txt (%d sets, no duplicates): %s" % (
        len(myB), len(theirB), sameB))
    ok &= sameB
    # the "first step" stated in row 79: B alone, chained at (0,1) -> (0,2)
    NB = port_counts(myB, 0, 1)
    page_check("B: 4349 sets, port counts rows (1123,1481),(622,1123) [row 79, first step]",
               len(myB) == 4349
               and (NB[(1, 0)], NB[(1, 1)], NB[(0, 0)], NB[(0, 1)]) == (1123, 1481, 622, 1123))
    rhoB, trB, detB = perron(NB)
    bB = rhoB ** (arb(1) / 17)
    page_check("rho_B = 1123 + sqrt(921182), exact [row 79, first step]",
               closed_form(trB, detB) == (2 * 1123, 4 * 921182))
    page_check("rho_B^(1/17) = 1.5675245... [row 79, first step]",
               arb(15675245) / 10**7 < bB and bB < arb(15675246) / 10**7)
    Bp = read_family(paths["Bprime.txt"])
    extra = [S for S in Bp if S not in myB]
    Hmask = sum(1 << q for q in range(9, 19))
    print("        data/Bprime.txt: %d sets = B + %d extra" % (len(Bp), len(extra)))
    page_check("B' = B plus 15 sets inside the F-part (no H-point); 4364 distinct sets",
               len(Bp) == 4364 and len(set(Bp)) == 4364 and len(extra) == 15
               and myB <= set(Bp) and all(S & Hmask == 0 for S in extra))
    bp_pts = 19
    per_copy = bp_pts - 2                 # the chain glues the two ports of each copy
    page_check("B' lies on 19 points; each copy adds 17 points",
               all(S >> bp_pts == 0 for S in Bp) and per_copy == 17)
    t0 = time.perf_counter()
    sp = is_sperner(Bp)
    t1 = time.perf_counter()
    wit = sunflower_free_exhaustive(Bp, bp_pts)
    t2 = time.perf_counter()
    print("        B' Sperner: %s [%.0fs]; exhaustive sunflower search over all %d pairs: %s [%.0fs]"
          % (sp, t1 - t0, len(Bp) * (len(Bp) - 1) // 2,
             "none found" if wit is None else "FOUND %s" % (wit,), t2 - t1))
    ok &= sp and wit is None
    Np = port_counts(Bp, 0, 1)
    print("        B' port counts at (0, 1): %s" % (dict(sorted(Np.items())),))
    page_check("B' port counts: rows (1127,1488),(622,1127)",
               (Np[(1, 0)], Np[(1, 1)], Np[(0, 0)], Np[(0, 1)]) == (1127, 1488, 622, 1127))
    rho, tr, det = perron(Np)
    b80 = rho ** (arb(1) / per_copy)
    page_check("rho = 1127 + sqrt(925536) (exact: trace 2254, discriminant 4*925536)",
               closed_form(tr, det) == (2254, 4 * 925536))
    print("        rho = %s; rho^(1/17) = %s" % (rho.str(20), b80.str(20)))
    page_check("rho^(1/17) < 1.5678016, as the printed digits 1.5678015... say",
               b80 < arb(15678016) / 10**7)
    c80 = bool(arb(15678015) / 10**7 < b80)
    print("        -> C_49 >= 1.5678015: %s" % c80)
    ok &= c80
    n_bad = sum(1 for _, c in checks if not c)
    print("page cross-checks: %d of %d agree%s" % (
        len(checks) - n_bad, len(checks), "" if not n_bad else "  -> PAGE MISMATCH"))
    ok &= n_bad == 0
    print("RESULT: %s" % ("CONFIRMED rows 79 and 80 (given the XOR-gluing lemma)"
                          if ok else "NOT CONFIRMED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
