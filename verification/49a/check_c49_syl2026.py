#!/usr/bin/env python3
"""Independent check of the [Syl2026] lower bounds on C_49: 1.5675517* and
1.5678015* (constants/49a.md rows 79 and 80).

Uses the families F, H rebuilt from the page by check_c49_cla2026.py (same
directory) and the XOR-gluing lemma proved in README.md.

Row 79 (1.5675517*): pure gluing, so goodness (Sperner + sunflower-free)
follows from the lemma; the checker recomputes the gadget/unit port counts
from F and H alone (counts multiply over glued pendants) and the bound
rho^(1/60).

Row 80 (1.5678015*): B' = B + 15 sets, where B = glue(F at edge (0,3),
H at 0).  The checker rebuilds B itself, compares it with data/B.txt, checks
that data/Bprime.txt is B plus 15 sets with no H-point, then checks B'
exhaustively (Sperner, and no 3-sunflower: for every pair A, B there is no
third member C with C n (A u B) = A n B), recomputes the port counts and the
bound rho^(1/17).

Usage: python3 -I check_c49_syl2026.py --data DIR   (DIR has B.txt, Bprime.txt)
"""

import argparse
import hashlib
import os
import sys
import time

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

    # ---------------- row 79: gadget G and the 62-point unit (pure gluing)
    # G = F with H glued at F-points 4 = (1,2) and 6 = (1,4); root F-point 0.
    G = [0, 0]  # (avoiding root, containing root)
    for A in F:
        G[(A >> 0) & 1] += w_factor(hc, (A >> 4) & 1) * w_factor(hc, (A >> 6) & 1)
    G = tuple(G)
    print("row 79: gadget G: %d sets on %d points, (avoid, contain root) = %s; page: "
          "250659, 98308 / 152351: %s" % (sum(G), 10 + 2 * 9, G,
                                          (sum(G), G) == (250659, (98308, 152351))))
    # unit: core F, ports 0 = (0,1) in and 1 = (0,2) out, G glued at core 2 and 3
    N = {(a, b): 0 for a in (0, 1) for b in (0, 1)}
    for A in F:
        N[((A >> 0) & 1, (A >> 1) & 1)] += (w_factor(G, (A >> 2) & 1)
                                            * w_factor(G, (A >> 3) & 1))
    page = {(0, 0): 148811965456, (0, 1): 279351870092, (1, 0): 279351870092,
            (1, 1): 378843386627}
    print("        unit (62 points) port counts %s; equal to the page: %s" % (
        dict(sorted(N.items())), N == page))
    rho, tr, det = perron(N)
    b79 = rho ** (arb(1) / 60)
    # page: rho = N01 + sqrt(N11 N00)
    same_form = bool((rho - (arb(N[(0, 1)]) + arb(N[(1, 1)] * N[(0, 0)]).sqrt())).abs_upper() < arb(10) ** -40)
    print("        rho = %s (= N01 + sqrt(N11 N00): %s); rho^(1/60) = %s" % (
        rho.str(25), same_form, b79.str(20)))
    c79 = bool(arb(15675517) / 10**7 < b79)
    print("        -> C_49 >= 1.5675517: %s" % c79)
    ok &= N == page and c79 and same_form

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
    print("row 80: my rebuild of B has %d sets; equals data/B.txt (%d sets): %s" % (
        len(myB), len(theirB), set(theirB) == myB and len(theirB) == len(myB)))
    ok &= set(theirB) == myB
    Bp = read_family(paths["Bprime.txt"])
    extra = [S for S in Bp if S not in myB]
    Hmask = sum(1 << q for q in range(9, 19))
    print("        data/Bprime.txt: %d sets = B + %d extra; extras avoid all H-points: %s"
          % (len(Bp), len(extra), all(S & Hmask == 0 for S in extra)))
    ok &= len(Bp) == 4364 and len(set(Bp)) == 4364 and len(extra) == 15 \
        and myB <= set(Bp)
    t0 = time.perf_counter()
    sp = is_sperner(Bp)
    t1 = time.perf_counter()
    wit = sunflower_free_exhaustive(Bp, 19)
    t2 = time.perf_counter()
    print("        B' Sperner: %s [%.0fs]; exhaustive sunflower search over all %d pairs: %s [%.0fs]"
          % (sp, t1 - t0, len(Bp) * (len(Bp) - 1) // 2,
             "none found" if wit is None else "FOUND %s" % (wit,), t2 - t1))
    ok &= sp and wit is None
    Np = port_counts(Bp, 0, 1)
    print("        B' port counts at (0, 1): %s; page rows (1127,1488),(622,1127): %s" % (
        dict(sorted(Np.items())),
        (Np[(1, 0)], Np[(1, 1)], Np[(0, 0)], Np[(0, 1)]) == (1127, 1488, 622, 1127)))
    rho, tr, det = perron(Np)
    b80 = rho ** (arb(1) / 17)
    print("        rho = %s = 1127 + sqrt(925536): %s; rho^(1/17) = %s" % (
        rho.str(20), bool((rho - 1127 - arb(925536).sqrt()).abs_upper() < arb(10) ** -40),
        b80.str(20)))
    c80 = bool(arb(15678015) / 10**7 < b80)
    print("        -> C_49 >= 1.5678015: %s" % c80)
    ok &= c80 and (Np[(1, 0)], Np[(1, 1)], Np[(0, 0)], Np[(0, 1)]) == (1127, 1488, 622, 1127)
    print("RESULT: %s" % ("CONFIRMED rows 79 and 80 (given the XOR-gluing lemma)"
                          if ok else "NOT CONFIRMED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
