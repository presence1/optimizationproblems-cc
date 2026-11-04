# Independent check of the asterisked lower bound on C_1c

Constant: [C_1c, the Barnard–Steinerberger autocorrelation constant](../../constants/1c.md).
It is the least C with min_{0≤t≤1} ∫ f(x) f(x+t) dx ≤ C (∫f)² for all
non-negative f ∈ L¹(ℝ). Any such f with ∫f > 0 gives the lower bound
C_1c ≥ L(f), where L(f) = min_{t∈[0,1]} g(t) / (∫f)² and g(t) = ∫ f(x) f(x+t) dx.

## Verdict

| Row of `constants/1c.md` | Claimed | Artifact | Result |
| --- | --- | --- | --- |
| line 28, [Kos2026] | C_1c ≥ 0.4103333* | `K24576_0.4103333.json` @ `a4ee94e`, K = 24576, 24592 integer weights | **Confirmed.** L(f) = 134648548624804778248790016 / 328144294688458468928334649 = 0.41033335274849333953…, which is exactly the fraction on the page. The minimum is attained only at k = 21264, as the page says. The margin over 0.4103333 is 5.3·10⁻⁸ |
| line 27, [R2026] (calibration only, not asterisked) | C_1c ≥ 0.4103287 | `certificate.json` @ `19f3971`, K = 6144 | Reproduced: 21072342208353792 / 51354782902387969 = 0.41032871754918741449…, the page's fraction, which [T2026] already replayed |

The page's other details also check out. There are 24592 non-negative integer
weights, the last 8 are zero (support [0, 3073/3072)), and 22.08 % of the mass
lies in [1/6144, 2/6144) (the page says "about 22%").

"Confirmed" means: the published weights define a non-negative step function
f, and I computed min_{t∈[0,1]} g(t)/(∫f)² exactly, with no rounding, and found
it at or above 0.4103333. That proves C_1c ≥ 0.4103333 as stated.

## Why a finite computation is enough

Let f = Σ_{i<n} w_i 1_{[i/K,(i+1)/K)} with w_i ≥ 0. For two cells,
|[i/K,(i+1)/K) ∩ ([j/K,(j+1)/K) − t)| = T(t − (j−i)/K), where
T(u) = max(0, 1/K − |u|) is a tent of height 1/K on [−1/K, 1/K]. So

  g(t) = Σ_{i,j} w_i w_j T(t − (j−i)/K) = Σ_d A_d T(t − d/K),  with A_d = Σ_i w_i w_{i+d}  (A_{−d} = A_d).

On [k/K, (k+1)/K] only d = k and d = k+1 contribute, and both tents are linear
there. Hence g(k/K) = A_k/K, g is linear between consecutive multiples of 1/K,
and its minimum over [0, 1] is attained at one of the knots k = 0, …, K. With
∫f = S/K, where S = Σ w_i,

  L(f) = K · min_{0≤k≤K} A_k / S².

I derived this myself. It agrees with the certificate's FORMAT.md and with the
argument the page cites ([K2021], Thm 3.1).

## What the checker does

`check_c1c.py` runs on the standard library plus python-flint, which is
required for check B. If python-flint cannot be imported, the checker stops
with exit status 2 and says why; it never skips check B. (Until
`replay/package` it skipped check B silently in that case, exactly like the
1d checker; AUDIT.md §2 described that trap for 1d only.)

1. It checks SHA-256 against the value on the page, which matches. It then
   parses the JSON and requires `weights_int` to be JSON integers, all ≥ 0 and
   not all zero, and K to be a positive integer. It also checks n, K and the
   number of trailing zeros against the page.
2. **A** computes A_k = Σ_i w_i w_{i+k} for all 24577 lags by direct summation
   over Python integers, about 3·10⁸ exact products.
3. **B** computes the same A_k as the coefficients of P(x) · x^{n−1}P(1/x),
   using FLINT's `fmpz_poly`, a different algorithm. A and B agree exactly.
4. **C** is a brute-force check of the reduction itself, with no tent formula.
   It computes g at a point by integrating u ↦ G(u) G(u+τ) piece by piece
   between the breakpoints of both factors, where G = Σ w_i 1_{[i,i+1)}, using
   integers only (in units of 1/q for τ = k + p/q). In the full run recorded
   in `run_output.txt` this was done at **every** knot, where it must equal
   A_k, and at 2000 random rationals strictly between knots, where it must
   equal the linear interpolation. The points include the minimising knot,
   its neighbours, and t = 0 and t = 1. All agree exactly.
5. L(f) is formed as an exact fraction and compared with the recorded
   fraction, with the recorded minimiser (k = 21264 must be the only
   minimiser), and exactly with 0.4103333. All three comparisons are enforced:
   any mismatch fails the run. All three agree. (Until `replay/package` the
   minimiser comparison was printed but not enforced; AUDIT.md §4,
   mutation 1c-8.)
6. `--selftest` checks hand cases: 1_{[0,1)} gives 0, 1_{[0,2)} gives 1/4, and
   the ruler {0,1,4,6} gives the page's 3/8. It also checks A = B = brute force
   on 30 random small cases.

## Reproduce

```bash
sh verification/1c/fetch.sh /some/empty/dir
```

```bash
python3 -I verification/1c/check_c1c.py --selftest
```

```bash
python3 -I verification/1c/check_c1c.py --data /some/empty/dir --knots 24577 --interior 2000
```

The default `--knots 400 --interior 200` run takes about 17 s. Of that,
check A takes 10 s and FLINT takes 0.03 s. The full run's timing is in
`run_output.txt`, which is the re-run on branch `replay/package`; the
original run of 3 November 2026 is in the git history of this file, with the
same numbers. The first output line must read `python-flint 0.9.0` (or
another installed version). Hardware: one core of an Intel Xeon @ 2.30 GHz,
Python 3.13.18, python-flint 0.9.0.

## Assumptions

- The definition is the one on the constant page at fork commit `87b4ebb`.
  The claimed bound, fraction and minimiser were copied from line 28 of that
  page.
- The input is all integers. No floating point is used anywhere in the
  decision. The printed "margin" is an exact difference converted to a float
  for display.
- The data file at commit `a4ee94e` is the certificate the row refers to. Its
  SHA-256 equals the one on the page.

## Independence

I read the certificate repository's `FORMAT.md` to learn the data layout. I did
not open or run its `verify.py`, `verify_independent.py` or `score_exact.py`, or
the R2026 repository's checkers. I also did not read its `PROOF.md`; I derived
the reduction above myself. The checker was written by an AI agent (Claude)
working for the owner of this fork. The page notes that the certificate itself
was found and checked with Claude agents too, so this replay is independent of
the authors' code but not of the AI tooling. Whether it counts as a second
party is for a maintainer to decide.

## Related upstream work

Upstream pull request
[#292](https://github.com/teorth/optimizationproblems/pull/292) (open, with no
comments, when the audit was written) already posts a replay of this
certificate and keeps the asterisk "pending a second party" (AUDIT.md §6.2).
The verification here does not refer to #292, and nobody here has compared it
with #292's code.

## Corrections made on branch `replay/package` (4 November 2026)

- The recorded minimiser is now enforced, not just printed (AUDIT.md §4,
  mutation 1c-8; §5, item 6). Mutation test 1c-8 now expects failure.
- `check_c1c.py` now requires python-flint and stops with exit status 2
  without it, instead of skipping check B silently. The audit missed this
  (it said the checkers other than 1d fail loudly); a run without
  python-flint showed it. Mutation tests 1c-9 and 1c-10 check it.
- Added the note on upstream #292 (AUDIT.md §5, item 11).
