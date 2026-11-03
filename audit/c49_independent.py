#!/usr/bin/env python3
"""Auditor's independent re-check of the C_49 rows confirmed on verify/49a.

Written for AUDIT.md without reusing any code from verify/49a or from the
certificate authors.  Algorithms are deliberately different from the ones on
verify/49a:

  * sunflower search: "kernel buckets" -- for each pivot A, the other members
    are grouped by their trace B & A; a 3-sunflower through A exists iff some
    bucket holds two members whose parts outside A are disjoint (numpy,
    all within-bucket pairs at once);
  * Sperner: zeta transform (subset-sum over the Boolean lattice), not pairs;
  * F is rebuilt by classifying all 2^10 graphs on K_5 by invariants
    (degree sequence, connectivity), not by constructing the three types;
  * bounds are decided exactly in integer/rational arithmetic (no floats,
    no Arb): c < rho^(1/p)  <=>  c^p < (tr + sqrt(disc))/2.

Parts:
  1. XOR-gluing lemma: EXHAUSTIVE check over all good (Sperner + 3-sunflower-
     free) families on ground sets of size <= 4, every port choice, for both
     claims (i) injectivity and (ii) goodness; plus random tests up to 7
     points; plus demonstrations that the Sperner hypothesis and the XOR rule
     are load-bearing (counterexamples are found when they are dropped).
  2. F and H from the constant page text; goodness; port counts.
  3. Explicit XOR chains F-F, H-H, F-H, H-F: sizes equal the transfer-matrix
     prediction and the chains are good (exhaustive).
  4. Rows 74-80 decided exactly; row 81 (Kos2026) arithmetic only.

Usage:
  python3 -I c49_independent.py [--irsi DIR] [--syl DIR] [--quick]
  DIR for --irsi holds v10.json, v11_s17.json, v12.json (IRSI tags v1.0-1.2);
  DIR for --syl holds B.txt, Bprime.txt (xSyllaa @ 8e21d02).
"""

import argparse
import hashlib
import itertools
import json
import os
import random
import sys
import time
from fractions import Fraction
from math import comb, isqrt

import numpy as np


# --------------------------------------------------------------------------
# basic predicates
# --------------------------------------------------------------------------
def brute_sunflower(fam):
    """True iff some 3 distinct members have equal pairwise intersections."""
    for A, B, C in itertools.combinations(fam, 3):
        k = A & B
        if A & C == k and B & C == k:
            return True
    return False


def brute_sperner(fam):
    return not any(a != b and a & b == a for a in fam for b in fam)


def zeta_sperner(fam, npts):
    """Sperner check via the zeta transform on the Boolean lattice 2^[npts]:
    cnt[m] = #members that are subsets of m; Sperner iff cnt[S] == 1 for all
    members S (only S itself).  Members must be distinct."""
    cnt = np.zeros(1 << npts, dtype=np.int32)
    idx = np.array(fam, dtype=np.int64)
    np.add.at(cnt, idx, 1)
    if cnt[idx].max() != 1:
        return False                       # duplicate member
    for b in range(npts):
        step = 1 << b
        v = cnt.reshape(-1, 2 * step)
        v[:, step:] += v[:, :step]
    return bool((cnt[idx] == 1).all())


def bucket_sunflower(fam, npts, pivots=None):
    """Kernel-bucket search.  Returns None or a witness (i, j, k) of member
    indices forming a 3-sunflower.  Exact for any family of distinct sets."""
    arr = np.array(fam, dtype=np.int64)
    m = len(arr)
    full = (1 << npts) - 1
    rng_piv = range(m) if pivots is None else pivots
    for i in rng_piv:
        A = int(arr[i])
        T = arr & A
        O = arr & (full ^ A)
        T = T.copy()
        T[i] = -1                          # A itself is never B or C
        order = np.argsort(T, kind="stable")
        Ts, Os = T[order], O[order]
        # group boundaries
        cut = np.flatnonzero(Ts[1:] != Ts[:-1]) + 1
        starts = np.concatenate(([0], cut))
        ends = np.concatenate((cut, [m]))
        # for each position p, number of later positions in the same group
        grp_end = np.repeat(ends, ends - starts)
        cnt = grp_end - np.arange(m) - 1
        tot = int(cnt.sum())
        if tot == 0:
            continue
        left = np.repeat(np.arange(m), cnt)
        offs = np.arange(tot) - np.repeat(np.cumsum(cnt) - cnt, cnt) + 1
        right = left + offs
        hit = np.flatnonzero((Os[left] & Os[right]) == 0)
        if hit.size:
            p, q = int(order[left[hit[0]]]), int(order[right[hit[0]]])
            return (i, p, q)
    return None


# --------------------------------------------------------------------------
# Part 1: the XOR-gluing lemma
# --------------------------------------------------------------------------
def all_good_families(npts):
    """All non-empty families on [npts] that are Sperner and sunflower-free."""
    subsets = list(range(1 << npts))
    out = []
    # enumerate antichains by brute force over subsets of the power set
    for mask in range(1, 1 << (1 << npts)):
        fam = [s for s in subsets if (mask >> s) & 1]
        if brute_sperner(fam) and not brute_sunflower(fam):
            out.append(fam)
    return out


def good_families_bt(npts):
    """Same as all_good_families, by backtracking (needed for 5 points)."""
    res, fam = [], []

    def rec(start):
        if fam:
            res.append(list(fam))
        for S in range(start, 1 << npts):
            if any(S & T == S or S & T == T for T in fam):
                continue
            if any((S & A) == (A & B) == (S & B) for A, B in itertools.combinations(fam, 2)):
                continue
            fam.append(S)
            rec(S + 1)
            fam.pop()
    rec(0)
    return res


def port_classes(npts, fams):
    """Representatives of (family, port) pairs up to relabelling of points.
    Goodness and injectivity of a gluing are invariant under relabelling, and
    the XOR rule is symmetric in its two inputs."""
    # a relabelling p sends old point q to new point p[q]; we keep only those
    # that send the port x to 0, and take the lexicographically least image
    reps = {}
    for F in fams:
        for x in range(npts):
            best = None
            for p in itertools.permutations(range(npts)):
                if p[x] != 0:
                    continue
                img = tuple(sorted(sum(1 << p[q] for q in range(npts) if (S >> q) & 1) for S in F))
                if best is None or img < best:
                    best = img
            reps[best] = (list(best), 0)
    return list(reps.values())


def lemma_deep(log):
    """(family, port) classes on <= 5 points, all pairs of classes."""
    classes = {}
    t0 = time.perf_counter()
    for m in range(1, 6):
        fams = good_families_bt(m)
        classes[m] = port_classes(m, fams)
        log("  good families on %d points: %d; (family, port) classes up to "
            "relabelling: %d" % (m, len(fams), len(classes[m])))
    n = inj = bad = 0
    for m1 in range(1, 6):
        for m2 in range(m1, 6):
            for F1, x in classes[m1]:
                for F2, y in classes[m2]:
                    G = glue_list(F1, m1, x, F2, m2, y)
                    n += 1
                    if len(set(G)) != len(G):
                        inj += 1
                    Gs = sorted(set(G))
                    if not brute_sperner(Gs) or brute_sunflower(Gs):
                        bad += 1
    log("  deep: %d gluings of (family, port) classes on <= 5 points: injectivity "
        "failures %d, goodness failures %d  [%.0fs]" % (n, inj, bad, time.perf_counter() - t0))
    return n > 0 and inj == 0 and bad == 0


def glue_list(F1, n1, x, F2, n2, y, rule="xor"):
    """Return the glued family as a LIST (duplicates kept, to test (i)).
    Ground set: points of F1 except x (kept at their labels), points of F2
    except y (shifted by n1)."""
    out = []
    for A in F1:
        s = (A >> x) & 1
        Ap = A & ~(1 << x)
        for B in F2:
            t = (B >> y) & 1
            Bp = (B & ~(1 << y)) << n1
            if rule == "xor":
                if s + t == 1:
                    out.append(Ap | Bp)
            elif rule == "same-drop":
                if s == t:
                    out.append(Ap | Bp)
            elif rule == "nonsperner-xor":   # same as xor; used on non-Sperner inputs
                if s + t == 1:
                    out.append(Ap | Bp)
    return out


def lemma_exhaustive(max_pts, log):
    goods = {m: all_good_families(m) for m in range(1, max_pts + 1)}
    for m, g in goods.items():
        log("  good families on %d points: %d" % (m, len(g)))
    n_glue = n_inj_fail = n_good_fail = 0
    t0 = time.perf_counter()
    for m1 in range(1, max_pts + 1):
        for m2 in range(1, max_pts + 1):
            for F1 in goods[m1]:
                for F2 in goods[m2]:
                    for x in range(m1):
                        for y in range(m2):
                            G = glue_list(F1, m1, x, F2, m2, y)
                            n_glue += 1
                            if len(set(G)) != len(G):
                                n_inj_fail += 1
                            Gs = sorted(set(G))
                            if not brute_sperner(Gs) or brute_sunflower(Gs):
                                n_good_fail += 1
    log("  exhaustive: %d gluings (all ordered pairs of good families on <= %d "
        "points, all ports): injectivity failures %d, goodness failures %d  [%.0fs]"
        % (n_glue, max_pts, n_inj_fail, n_good_fail, time.perf_counter() - t0))
    return n_inj_fail == 0 and n_good_fail == 0 and n_glue > 0, goods


def random_good_family(n, rng, uniform=None, tries=200):
    cand = list(range(1 << n))
    if uniform is not None:
        cand = [s for s in cand if bin(s).count("1") == uniform]
    rng.shuffle(cand)
    fam = []
    for S in cand[:tries]:
        if any(S & T == S or S & T == T for T in fam):
            continue
        if any((S & A) == (A & B) == (S & B) for A, B in itertools.combinations(fam, 2)):
            continue
        fam.append(S)
    return fam


def lemma_random(trials, rng, log):
    fails = 0
    done = 0
    for _ in range(trials):
        n1, n2 = rng.randrange(4, 8), rng.randrange(4, 8)
        F1 = random_good_family(n1, rng, None if rng.random() < 0.5 else rng.randrange(1, n1))
        F2 = random_good_family(n2, rng, None if rng.random() < 0.5 else rng.randrange(1, n2))
        if not F1 or not F2:
            continue
        x, y = rng.randrange(n1), rng.randrange(n2)
        G = glue_list(F1, n1, x, F2, n2, y)
        done += 1
        if len(set(G)) != len(G) or not brute_sperner(G) or brute_sunflower(G):
            fails += 1
    log("  random: %d gluings of good families on 4..7 points (uniform and "
        "non-uniform): failures %d" % (done, fails))
    return fails == 0


def hypotheses_are_needed(log):
    """Show the test can find counterexamples: (a) drop Sperner, (b) use the
    same-status rule while dropping the merged point."""
    # (a) sunflower-free but NOT Sperner families on <= 3 points
    found_a = None
    for m1 in (2, 3):
        fams = []
        for mask in range(1, 1 << (1 << m1)):
            fam = [s for s in range(1 << m1) if (mask >> s) & 1]
            if not brute_sperner(fam) and not brute_sunflower(fam):
                fams.append(fam)
        for F1 in fams:
            for F2 in fams:
                for x in range(m1):
                    for y in range(m1):
                        G = glue_list(F1, m1, x, F2, m1, y)
                        if len(set(G)) != len(G) or brute_sunflower(sorted(set(G))):
                            found_a = (F1, F2, x, y, len(G), len(set(G)))
                            break
                    if found_a: break
                if found_a: break
            if found_a: break
        if found_a: break
    log("  (a) without Sperner the lemma fails, e.g. F1=%s F2=%s ports x=%d y=%d "
        "(list size %d, distinct %d)" % found_a if found_a else "  (a) NO counterexample found")
    # (b) same-status, merged point dropped, on good families
    found_b = None
    goods3 = all_good_families(3)
    for F1 in goods3:
        for F2 in goods3:
            for x in range(3):
                for y in range(3):
                    G = glue_list(F1, 3, x, F2, 3, y, rule="same-drop")
                    Gs = sorted(set(G))
                    if len(Gs) != len(G) or not brute_sperner(Gs) or brute_sunflower(Gs):
                        found_b = (F1, F2, x, y)
                        break
                if found_b: break
            if found_b: break
        if found_b: break
    log("  (b) same-status rule with the merged point dropped fails, e.g. "
        "F1=%s F2=%s x=%d y=%d" % found_b if found_b else "  (b) NO counterexample found")
    return found_a is not None and found_b is not None


# --------------------------------------------------------------------------
# Part 2: F and H from the page text
# --------------------------------------------------------------------------
K5_EDGES = list(itertools.combinations(range(5), 2))      # lexicographic


def graph_degrees(mask):
    deg = [0] * 5
    for i, (a, b) in enumerate(K5_EDGES):
        if (mask >> i) & 1:
            deg[a] += 1
            deg[b] += 1
    return deg


def is_connected_on(mask, verts):
    verts = list(verts)
    if not verts:
        return True
    adj = {v: set() for v in verts}
    for i, (a, b) in enumerate(K5_EDGES):
        if (mask >> i) & 1:
            adj[a].add(b)
            adj[b].add(a)
    seen, stack = {verts[0]}, [verts[0]]
    while stack:
        v = stack.pop()
        for w in adj[v]:
            if w not in seen:
                seen.add(w)
                stack.append(w)
    return seen == set(verts)


def classify(mask):
    deg = graph_degrees(mask)
    ne = bin(mask).count("1")
    sdeg = sorted(deg, reverse=True)
    if ne == 4 and sdeg == [4, 1, 1, 1, 1]:
        return "star"
    # complete bipartite K_{2,3}: 6 edges, every edge joins the two parts
    if ne == 6 and sdeg == [3, 3, 2, 2, 2]:
        big = [v for v in range(5) if deg[v] == 3]
        small = [v for v in range(5) if deg[v] == 2]
        want = 0
        for i, (a, b) in enumerate(K5_EDGES):
            if (a in big) != (b in big):
                want |= 1 << i
        if mask == want:
            return "K23"
    comp = ((1 << 10) - 1) ^ mask
    cdeg = sorted(graph_degrees(comp), reverse=True)
    if bin(comp).count("1") == 4 and cdeg == [3, 2, 1, 1, 1] and is_connected_on(comp, range(5)):
        return "chaircomp"
    return None


def build_F():
    F, kinds = [], {}
    for mask in range(1 << 10):
        c = classify(mask)
        if c:
            F.append(mask)
            kinds[c] = kinds.get(c, 0) + 1
    return F, kinds


def build_H():
    sq = sorted({(x * x) % 11 for x in range(1, 11)})
    bases = [(0, 1, 2, 3, 4, 5, 6), (0, 1, 2, 3, 4, 6, 7), (0, 1, 2, 6, 9)]
    H, orbits = set(), []
    for base in bases:
        orb = {sum(1 << ((a * x + b) % 11) for x in base) for a in sq for b in range(11)}
        orbits.append(len(orb))
        H |= orb
    return sorted(H), sq, orbits


def port_counts(fam, u, v):
    N = {(a, b): 0 for a in (0, 1) for b in (0, 1)}
    for S in fam:
        N[((S >> u) & 1, (S >> v) & 1)] += 1
    return N


# --------------------------------------------------------------------------
# exact bound decision
# --------------------------------------------------------------------------
def T_of(N):
    """XOR chain transfer matrix on the u-status: T[a][a'] = N[a, 1-a']."""
    return [[N[(a, 1 - ap)] for ap in (0, 1)] for a in (0, 1)]


def mat2(X, Y):
    return [[X[i][0] * Y[0][j] + X[i][1] * Y[1][j] for j in (0, 1)] for i in (0, 1)]


def exact_claim_ok(T, p, claim):
    """Exact test of claim < rho(T)^(1/p) for a positive 2x2 integer T."""
    assert all(x > 0 for r in T for x in r)
    tr = T[0][0] + T[1][1]
    det = T[0][0] * T[1][1] - T[0][1] * T[1][0]
    disc = tr * tr - 4 * det
    y = Fraction(claim) ** p          # need rho > y, rho = (tr + sqrt(disc))/2
    lhs = 2 * y - tr                  # need sqrt(disc) > lhs
    if lhs < 0:
        return True, tr, det, disc
    return disc > lhs * lhs, tr, det, disc


def rho_float(tr, disc):
    return (tr + disc ** 0.5) / 2


def chain_size(fams_ports, k_pattern):
    """|G| for an XOR chain following k_pattern (list of (N) dicts), by
    explicit state vector over the v-status of the last copy."""
    N0 = k_pattern[0]
    x = [N0[(0, 0)] + N0[(1, 0)], N0[(0, 1)] + N0[(1, 1)]]   # indexed by v-status
    for N in k_pattern[1:]:
        # next copy's u-status must be 1 - previous v-status
        x = [x[0] * N[(1, 0)] + x[1] * N[(0, 0)], x[0] * N[(1, 1)] + x[1] * N[(0, 1)]]
    return x[0] + x[1]


def explicit_chain(parts):
    """parts: list of (family, npts, u, v).  Glue left to right, XOR rule,
    returning (family_list, npts, current v label)."""
    fam, n, _, v = parts[0][0], parts[0][1], parts[0][2], parts[0][3]
    cur_fam, cur_n, cur_v = list(fam), n, v
    for F2, n2, u2, v2 in parts[1:]:
        G = glue_list(cur_fam, cur_n, cur_v, F2, n2, u2)
        # relabel: remove the hole at cur_v and at (cur_n + u2) to keep it compact
        holes = sorted([cur_v, cur_n + u2])
        def compact(S):
            out, j = 0, 0
            for q in range(cur_n + n2):
                if q in holes:
                    continue
                if (S >> q) & 1:
                    out |= 1 << j
                j += 1
            return out
        newv = cur_n + v2
        newv_c = newv - sum(1 for h in holes if h < newv)
        cur_fam = [compact(S) for S in G]
        cur_n, cur_v = cur_n + n2 - 2, newv_c
    return cur_fam, cur_n, cur_v


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--irsi")
    ap.add_argument("--syl")
    ap.add_argument("--quick", action="store_true", help="lemma exhaustive only up to 3 points")
    ap.add_argument("--deep", action="store_true",
                    help="also all (family, port) classes on <= 5 points")
    args = ap.parse_args()
    ok = True

    def log(s):
        print(s, flush=True)

    log("== Part 1: the XOR-gluing lemma")
    # self-test of the sunflower/Sperner routines against brute force
    rng = random.Random(4949)
    for _ in range(300):
        n = rng.randrange(3, 8)
        fam = rng.sample(range(1, 1 << n), rng.randrange(3, min(25, (1 << n) - 1)))
        b1 = brute_sunflower(fam)
        b2 = bucket_sunflower(fam, n) is not None
        assert b1 == b2, (fam, n)
        assert brute_sperner(fam) == zeta_sperner(fam, n)
    log("  bucket search and zeta Sperner agree with brute force on 300 random families")
    lem_ok, goods = lemma_exhaustive(3 if args.quick else 4, log)
    ok &= lem_ok
    for m in range(1, 5 if not args.quick else 4):
        assert len(good_families_bt(m)) == len(goods[m])   # two enumerations agree
    if args.deep:
        ok &= lemma_deep(log)
    ok &= lemma_random(400, random.Random(7), log)
    need_ok = hypotheses_are_needed(log)
    ok &= need_ok

    log("== Part 2: F and H rebuilt from the page text")
    F, kinds = build_F()
    H, sq, orbits = build_H()
    log("  F: %d sets, kinds %s; H: %d sets, squares %s, orbit sizes %s"
        % (len(F), kinds, len(H), sq, orbits))
    ok &= len(F) == 75 and kinds == {"star": 5, "K23": 10, "chaircomp": 60}
    ok &= len(H) == 121 and orbits == [55, 55, 11]
    for name, fam, n in (("F", F, 10), ("H", H, 11)):
        sp = zeta_sperner(fam, n)
        sf = bucket_sunflower(fam, n)
        pcs = {tuple(port_counts(fam, u, v)[k] for k in ((0, 0), (0, 1), (1, 0), (1, 1)))
               for u in range(n) for v in range(n) if u != v}
        log("  %s: Sperner %s, sunflower %s, port counts (N00,N01,N10,N11) over all "
            "ordered pairs %s" % (name, sp, "none" if sf is None else sf, sorted(pcs)))
        ok &= sp and sf is None and len(pcs) == 1
    NF = port_counts(F, 0, 1)
    NH = port_counts(H, 0, 1)
    ok &= [NF[k] for k in ((0, 0), (0, 1), (1, 0), (1, 1))] == [11, 20, 20, 24]
    ok &= [NH[k] for k in ((0, 0), (0, 1), (1, 0), (1, 1))] == [15, 31, 31, 44]
    # link of a point of H is a copy of F (page remark) -- informational
    link0 = sorted(S & ~1 for S in H if S & 1)
    log("  (info) link of 0 in H has %d sets" % len(link0))

    log("== Part 3: explicit XOR chains vs transfer-matrix counts")
    cases = [("F-F", [(F, 10, 0, 1), (F, 10, 0, 1)], [NF, NF]),
             ("H-H", [(H, 11, 0, 1), (H, 11, 0, 1)], [NH, NH]),
             ("F-H", [(F, 10, 0, 1), (H, 11, 0, 1)], [NF, NH]),
             ("H-F", [(H, 11, 0, 1), (F, 10, 0, 1)], [NH, NF])]
    if not args.quick:
        cases.append(("F-F-F (pivot sample)", [(F, 10, 0, 1)] * 3, [NF, NF, NF]))
    for name, parts, Ns in cases:
        t0 = time.perf_counter()
        G, n, _ = explicit_chain(parts)
        pred = chain_size(None, Ns)
        distinct = len(set(G)) == len(G)
        sp = zeta_sperner(G, n)
        if len(G) > 20000:
            piv = random.Random(1).sample(range(len(G)), 300)
            sf = bucket_sunflower(G, n, pivots=piv)
            what = "300 random pivots"
        else:
            sf = bucket_sunflower(G, n)
            what = "all pivots"
        log("  %-22s %6d sets on %d points (predicted %d), distinct %s, Sperner %s, "
            "sunflower search (%s): %s  [%.0fs]" % (name, len(G), n, pred, distinct, sp,
                                                  what, "none" if sf is None else sf,
                                                  time.perf_counter() - t0))
        ok &= len(G) == pred and distinct and sp and sf is None

    log("== Part 4: the rows, decided exactly")
    TF, TH = T_of(NF), T_of(NH)
    rows = []
    rows.append(("77 Cla2026", TF, 8, "1.5664286"))
    rows.append(("78 Cla2026", mat2(TF, TH), 17, "1.5666969"))
    # row 79: gadget G = F + H at edges (1,2), (1,4); root (0,1).  Build G
    # explicitly (250659 sets) and read its root statuses directly.
    e = {ed: i for i, ed in enumerate(K5_EDGES)}
    t0 = time.perf_counter()
    G1, n1, _ = None, None, None
    # glue H (port 0) at F-point (1,2), then a second H at F-point (1,4)
    G = glue_list(F, 10, e[(1, 2)], H, 11, 0)
    # after the first gluing, F-point (1,4) is still at label e[(1,4)] (only
    # e[(1,2)] was removed, labels kept); H points occupy 11..21 except 10+0
    G = glue_list(G, 21, e[(1, 4)], H, 11, 0)
    root = e[(0, 1)]
    Gav = sum(1 for S in G if not (S >> root) & 1)
    Gin = len(G) - Gav
    log("  row 79 gadget built explicitly: %d sets (distinct %s), avoid/contain root "
        "%d/%d; page 250659 = 98308 + 152351: %s  [%.0fs]"
        % (len(G), len(set(G)) == len(G), Gav, Gin,
           (len(G), Gav, Gin) == (250659, 98308, 152351), time.perf_counter() - t0))
    ok &= (len(G), Gav, Gin) == (250659, 98308, 152351) and len(set(G)) == len(G)
    N79 = {(a, b): 0 for a in (0, 1) for b in (0, 1)}
    for A in F:
        f3 = Gav if (A >> e[(0, 3)]) & 1 else Gin       # XOR: partner root status opposite
        f4 = Gav if (A >> e[(0, 4)]) & 1 else Gin
        N79[((A >> e[(0, 1)]) & 1, (A >> e[(0, 2)]) & 1)] += f3 * f4
    page79 = {(0, 0): 148811965456, (0, 1): 279351870092, (1, 0): 279351870092,
              (1, 1): 378843386627}
    log("  row 79 unit port counts %s equal page: %s" % (
        [N79[k] for k in ((0, 0), (0, 1), (1, 0), (1, 1))], N79 == page79))
    ok &= N79 == page79
    rows.append(("79 Syl2026", T_of(N79), 60, "1.5675517"))

    if args.syl:
        def readfam(p):
            out = []
            for line in open(p, encoding="utf-8"):
                line = line.strip()
                if line and not line.startswith("#"):
                    out.append(sum(1 << int(t) for t in line.split()))
            return out
        Bp = readfam(os.path.join(args.syl, "Bprime.txt"))
        Bt = readfam(os.path.join(args.syl, "B.txt"))
        t0 = time.perf_counter()
        sp = zeta_sperner(Bp, 19)
        sf = bucket_sunflower(Bp, 19)
        NB = port_counts(Bp, 0, 1)
        # B itself is F (edge (0,3)) XOR-glued to H (point 0); my own relabelling
        Bmine = glue_list(F, 10, e[(0, 3)], H, 11, 0)
        def relabel(S):   # F labels 0..9 minus 2 -> 0..8 ; H labels 11..20 -> 9..18
            out = 0
            for q, newq in zip([0, 1, 3, 4, 5, 6, 7, 8, 9] + list(range(11, 21)), range(19)):
                if (S >> q) & 1:
                    out |= 1 << newq
            return out
        Bmine = {relabel(S) for S in Bmine}
        log("  row 80: B rebuilt = data B.txt: %s; B' %d sets, distinct %s, B subset of B': %s, "
            "Sperner (zeta) %s, sunflower (buckets, all pivots) %s; ports (0,1) %s  [%.0fs]"
            % (Bmine == set(Bt), len(Bp), len(set(Bp)) == len(Bp), Bmine <= set(Bp), sp,
               "none" if sf is None else sf,
               [NB[k] for k in ((0, 0), (0, 1), (1, 0), (1, 1))], time.perf_counter() - t0))
        ok &= Bmine == set(Bt) and len(Bp) == 4364 and sp and sf is None
        ok &= [NB[k] for k in ((0, 0), (0, 1), (1, 0), (1, 1))] == [622, 1127, 1127, 1488]
        rows.append(("80 Syl2026", T_of(NB), 17, "1.5678015"))

    if args.irsi:
        for fname, claim, sha in (("v10.json", "1.5617847", None),
                                  ("v11_s17.json", "1.5621220", "c12d0dd6"),
                                  ("v12.json", "1.5647730", "7472112c")):
            raw = open(os.path.join(args.irsi, fname), "rb").read()
            dig = hashlib.sha256(raw).hexdigest()
            d = json.loads(raw)
            n = int(d["bases"]["B"]["n"])
            fam = [int(s) for s in d["bases"]["B"]["sets"]]
            u, v = int(d["word"][0]["u"]), int(d["word"][0]["v"])
            t0 = time.perf_counter()
            sp = zeta_sperner(fam, n)
            sf = bucket_sunflower(fam, n)
            N = port_counts(fam, u, v)
            log("  %s sha256 %s... (page prefix %s): %d sets on %d points, distinct %s, "
                "Sperner %s, sunflower %s, ports u=%d v=%d -> %s  [%.0fs]"
                % (fname, dig[:8], sha, len(fam), n, len(set(fam)) == len(fam), sp,
                   "none" if sf is None else sf, u, v,
                   [N[k] for k in ((0, 0), (0, 1), (1, 0), (1, 1))], time.perf_counter() - t0))
            ok &= (sha is None or dig.startswith(sha)) and sp and sf is None and n == 20
            rows.append(("%s IRSI2026 %s" % ({"v10.json": 74, "v11_s17.json": 75,
                                              "v12.json": 76}[fname], fname), T_of(N), 18, claim))

    # row 81 (Kos2026): arithmetic only, from the page's port counts
    N81 = {(0, 0): 33969, (0, 1): 64728, (1, 0): 64728, (1, 1): 88867}
    rows.append(("81 Kos2026 (page counts only; family NOT checked)", T_of(N81), 26, "1.5678599"))

    for name, T, p, claim in rows:
        good, tr, det, disc = exact_claim_ok(T, p, claim)
        log("  row %-50s T=%s p=%d: x^2-%dx+%d, rho~%.6f, claim %s < rho^(1/p) exactly: %s"
            % (name, T, p, tr, det, rho_float(tr, disc), claim, good))
        if not name.startswith("81"):
            ok &= good
        # nudged claim must fail: next 7-decimal value above rho^(1/p)
        r = rho_float(tr, disc) ** (1.0 / p)
        up = Fraction(int(r * 10**7) + 1, 10**7)
        bad, *_ = exact_claim_ok(T, p, up)
        ok &= not bad

    log("RESULT: %s" % ("ALL CHECKS PASSED" if ok else "SOME CHECK FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
