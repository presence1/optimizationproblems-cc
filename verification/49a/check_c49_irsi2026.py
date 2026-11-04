#!/usr/bin/env python3
"""Independent check of the [IRSI2026] lower bounds on C_49 (rows 74-76 of
constants/49a.md): 1.5617847*, 1.5621220*, 1.5647730*.

Each certificate is one Sperner 3-sunflower-free base family B on 20 points
(sets as 20-bit masks, bit i = point i) with ports u = 18, v = 19; the chain
of XOR-glued copies (lemma proved in README.md) adds 18 points per copy, so
C_49 >= rho^(1/18), rho the Perron root of the port-count matrix.

Checked here, from the certificate's set list only: distinctness, Sperner
(all pairs), exhaustive 3-sunflower search (all pairs, bitset query for a
third member C with C n (A u B) = A n B), layer sizes, port counts against
the matrix on the page, rho and the bound.  The search routine is validated
against brute force in check_c49_syl2026.py.

Every comparison with the page is ENFORCED (exit status 1 on any mismatch):
the matrix, the layer sizes and ports where the page gives them, the
characteristic polynomial and closed-form Perron root where the page prints
them (exact integer arithmetic), the rounded rho, and the printed digits of
rho^(1/18).

Input bytes: v1.1 and v1.2 are pinned to the SHA-256 values on the page.  The
page records no hash for v1.0, so this replay pins the bytes it checked: the
blob of cert_c49_chain20.json at commit 4d23c9ad391c9a087cad03a3c3346b5f79badae0
(tag v1.0 when this replay was made).  Fetch every file by commit, not by tag
(see README.md).

Usage: python3 -I check_c49_irsi2026.py --data DIR
"""

import argparse
import hashlib
import json
import os
import sys
import time

import numpy as np

sys.dont_write_bytecode = True  # do not leave __pycache__ next to the scripts
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # own helper modules
from check_c49_syl2026 import sunflower_free_exhaustive  # noqa: E402

CERTS = [
    # file, sha256, claim, page matrix rows
    # in the page's convention [[#(v in, u out), #(v in, u in)],
    #                           [#(v out, u out), #(v out, u in)]]
    # v1.0: the page records no hash; this pin is the replay's own (see above)
    ("v10.json", "c30a74fed64616c5c6980fae91f94ae5899fed6a4cb338b537480ee9517d715b",
     "1.5617847", [[1884, 1360], [1081, 1802]], "row 74, tag v1.0"),
    ("v11_s17.json", "c12d0dd62500a97484cb4f72743803ea7b54e74272e2b474cbabeac7b256fc7b",
     "1.5621220", [[1802, 1360], [1080, 1908]], "row 75, tag v1.1"),
    ("v12.json", "7472112ced9d98da8cf7b6a3d586b93ea66750e39989e7a6d6d5f52ffeb4e82e",
     "1.5647730", [[1993, 1360], [1080, 1908]], "row 76, tag v1.2"),
]
PIN_SOURCE = {"v10.json": "this replay's pin (the page records none)",
              "v11_s17.json": "the page", "v12.json": "the page"}
PAGE_LAYERS = {"v11_s17.json": {7: 2, 10: 360, 11: 1108, 12: 3600, 13: 1080},
               "v12.json": {7: 2, 10: 551, 11: 1108, 12: 3600, 13: 1080}}
PAGE_PORTS = {"v11_s17.json": (18, 19), "v12.json": (18, 19)}
# characteristic polynomial x^2 - tr x + det, as printed: (tr, det)
PAGE_POLY = {"v11_s17.json": (3710, 1969416), "v12.json": (3901, 2333844)}
# closed-form Perron root as printed, as (tr, disc) with rho = (tr + sqrt(disc))/2:
#   v1.1: 1855 + sqrt(1471609) = (3710 + sqrt(4 * 1471609)) / 2
#   v1.2: (3901 + sqrt(5882425)) / 2
PAGE_CLOSED = {"v11_s17.json": (3710, 4 * 1471609), "v12.json": (3901, 5882425)}
# rho as printed, rounded to 4 decimals (in units of 10^-4)
PAGE_RHO_4DP = {"v10.json": 30561945, "v11_s17.json": 30680989, "v12.json": 31631856}
# leading digits of rho^(1/18) as printed (10 decimals)
PAGE_DIGITS = {"v11_s17.json": 15621220560, "v12.json": 15647730960}


def sperner_numpy(fam):
    a = np.array(fam, dtype=np.int64)
    for A in fam:
        # number of members B with A subset of B (including A itself)
        if int(np.count_nonzero((a & A) == A)) != 1:
            return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    args = ap.parse_args()
    from flint import arb, ctx
    ctx.prec = 200
    ok_all = True
    for fname, sha, claim, M, label in CERTS:
        path = os.path.join(args.data, fname)
        raw = open(path, "rb").read()
        dig = hashlib.sha256(raw).hexdigest()
        print("== %s (%s): sha256 %s %s %s" % (fname, label, dig,
              "matches" if dig == sha else "MISMATCH against", PIN_SOURCE[fname]))
        ok = dig == sha
        d = json.loads(raw.decode("utf-8"), parse_float=str)
        word = d["word"]
        assert len(word) == 1 and word[0]["base"] == "B"
        u, v = word[0]["u"], word[0]["v"]
        B = d["bases"]["B"]
        n, fam = B["n"], B["sets"]
        assert all(type(S) is int and 0 < S < (1 << n) for S in fam)
        distinct = len(set(fam)) == len(fam)
        layers = {}
        for S in fam:
            layers[bin(S).count("1")] = layers.get(bin(S).count("1"), 0) + 1
        print("   %d sets on n = %d points, ports u = %d, v = %d; distinct: %s; layers %s"
              % (len(fam), n, u, v, distinct, dict(sorted(layers.items()))))
        if fname in PAGE_LAYERS:
            print("   layer sizes match the page: %s" % (layers == PAGE_LAYERS[fname]))
            ok &= layers == PAGE_LAYERS[fname]
        t0 = time.perf_counter()
        sp = sperner_numpy(fam)
        t1 = time.perf_counter()
        wit = sunflower_free_exhaustive(fam, n)
        t2 = time.perf_counter()
        print("   Sperner: %s [%.0fs]; exhaustive sunflower search over %d pairs: %s [%.0fs]" % (
            sp, t1 - t0, len(fam) * (len(fam) - 1) // 2,
            "none found" if wit is None else "FOUND %s" % (wit[:2],), t2 - t1))
        ok &= distinct and sp and wit is None and n == 20
        N = {(a, b): 0 for a in (0, 1) for b in (0, 1)}   # (u-status, v-status)
        for S in fam:
            N[((S >> u) & 1, (S >> v) & 1)] += 1
        mine = [[N[(0, 1)], N[(1, 1)]], [N[(0, 0)], N[(1, 0)]]]
        print("   port matrix %s; equals the page's %s: %s" % (mine, M, mine == M))
        ok &= mine == M
        tr = N[(0, 1)] + N[(1, 0)]
        det = N[(0, 1)] * N[(1, 0)] - N[(0, 0)] * N[(1, 1)]
        rho = (arb(tr) + arb(tr * tr - 4 * det).sqrt()) / 2
        bound = rho ** (arb(1) / (n - 2))
        c = bool(arb(int(claim.replace(".", ""))) / 10**7 < bound)
        print("   x^2 - %dx + %d, rho = %s, rho^(1/%d) = %s; > %s: %s" % (
            tr, det, rho.str(15), n - 2, bound.str(18), claim, c))
        ok &= c
        checks = []   # further comparisons with the page; all must hold

        def page_check(desc, cond):
            cond = bool(cond)
            checks.append(cond)
            print("   page check: %-62s %s" % (desc, "OK" if cond else "MISMATCH"))

        page_check("trace and determinant of the page's matrix",
                   (tr, det) == (M[0][0] + M[1][1], M[0][0] * M[1][1] - M[0][1] * M[1][0]))
        page_check("each copy adds n - 2 = 18 points (rho^(1/18))", n - 2 == 18)
        if fname in PAGE_PORTS:
            page_check("ports u = %d, v = %d" % PAGE_PORTS[fname], (u, v) == PAGE_PORTS[fname])
        if fname in PAGE_POLY:
            page_check("characteristic polynomial x^2 - %dx + %d" % PAGE_POLY[fname],
                       (tr, det) == PAGE_POLY[fname])
        if fname in PAGE_CLOSED:
            page_check("closed-form rho = (%d + sqrt(%d))/2, exact" % PAGE_CLOSED[fname],
                       (tr, tr * tr - 4 * det) == PAGE_CLOSED[fname])
        r4 = PAGE_RHO_4DP[fname]
        page_check("rho = %d.%04d to 4 decimals" % divmod(r4, 10**4),
                   arb(2 * r4 - 1) / (2 * 10**4) < rho and rho < arb(2 * r4 + 1) / (2 * 10**4))
        if fname in PAGE_DIGITS:
            dg = PAGE_DIGITS[fname]
            page_check("rho^(1/18) = %d.%010d..." % divmod(dg, 10**10),
                       arb(dg) / 10**10 < bound and bound < arb(dg + 1) / 10**10)
        ok &= all(checks)
        ok_all &= ok
        print("   -> %s" % ("CONFIRMED (given the XOR-gluing lemma)" if ok else "NOT CONFIRMED"))
    print("RESULT: %s" % ("all three rows CONFIRMED" if ok_all else "NOT ALL CONFIRMED"))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
