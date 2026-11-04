# Independent check of the asterisked lower bound on C_16

Constant: [C_16 = L, the Brezis–Gallouët–Wainger remainder constant on the 2D torus](../../constants/16a.md).
I use the page's "equivalently" formulation:
L = max_{δ≥1} [4πΘ(δ) − ln δ − ln(1+ln δ)], where
Θ(δ) = sup{|u(0)|² : ‖∇u‖² = 1, ‖Δu‖² = δ} over zero-mean u on
𝕋² = [0, 2π]² with Lebesgue measure.

## Verdict

| Row of `constants/16a.md` | Claimed | Result |
| --- | --- | --- |
| line 38, lower bound (maximusrufus certificate) | L ≥ 2.1562247706* | **Confirmed for the constant as the page's "Equivalently" sentence and the source [BDZ2013] define it. Under the literal reading of the page's first sentence the bound would be false** (see the caveat below). The trial function's value is L_trial = 2.15622477064423579… (Arb, 128 bit), which exceeds 2.1562247706 by 4.42·10⁻¹¹. A second, independent float64 + `fsum` enclosure gives 2.1562247706442 ± 4.6·10⁻¹⁴, which agrees |
| line 37, [Pat2026] (calibration only, not asterisked) | L ≥ 2.156224 | Reproduced: 2.15622475379391…, with δ = 3.931809…, matching the page's "δ(u) ≈ 3.93181" and "2.1562247…" |
| line 30, upper bound 2.1562256466* | — | **Not checked.** It needs a rigorous tail bound for an infinite lattice sum and a branch-and-bound over δ ∈ [1, ∞), including an asymptotic regime. This is a separate and larger job |

**Caveat on the definition: under the literal reading of the page's first
sentence, this bound would be false.** The page defines L twice, and the two
definitions give different constants. Write F(δ) = 4πΘ(δ) − ln δ − ln(1 + ln δ).

- **The first sentence, read literally.** It requires the inequality only for
  u "with sufficiently large frequency ratio δ(u)", that is, only for
  δ(u) ≥ δ₀ with δ₀ as large as one likes. The best constant is then governed
  by the limit of F(δ) as δ → ∞, which is (β+π)/π ≈ 1.82283, the source's
  L_∞ (AUDIT.md §3.4). Every L > 1.82283 would be admissible, so there would
  be no smallest constant and the infimum would be 1.82283. **Under this
  reading the claimed lower bound 2.1562247706\* would be false**, and so
  would [Pat2026]'s 2.156224. Even with a fixed threshold δ₀ = 5, the
  supremum of F over δ ≥ δ₀ is numerically about 2.1547, below the claim.
- **The "Equivalently" sentence.** It defines L as the maximum of F over all
  δ ≥ 1. Every zero-mean u has δ(u) ≥ 1, because |k|⁴ ≥ |k|² on ℤ²∖{0}, so
  this is the inequality for every zero-mean u. Under this reading the bound
  holds, and that is what this checker verifies.

The source takes the second reading. [BDZ2013] (arXiv 1012.2061v1, supplied by
the fork owner; the 2013 journal version was not seen) states the inequality
in Theorem 3.8 "for all 2π × 2π-periodic functions u with zero mean", and
defines L := max_{δ≥1} {4πΘ(δ) − (log δ + log(1 + log δ))} in (3.20). The
phrase "with sufficiently large frequency ratio" is not in the source. The
page's [Pat2026] row (a trial function at δ ≈ 3.93), BDZ2013's maximiser
δ* ≈ 3.93 in the upper-bound table, and the upper-bound certificate (a
branch-and-bound over δ ∈ [1, ∞)) all presuppose the second reading as well. So the bound stands for the constant as the source defines
it, and the page's first sentence needs correcting. Which reading the
maintainer intends is for the maintainer to say; this replay has not asked
(see `SUBMISSION_NOTES.md`).

An earlier version of this README said that under the literal reading a trial
function with δ ≈ 3.93 "would then say nothing". That understated the problem
(AUDIT.md §5, item 1): under that reading the bound is false.

## The reduction

The trial function is u(x) = Σ_{0<|k|≤4000} c(|k|²) e^{ik·x}, with
c(n) = 1/(n(1+μn)) and μ = 1221/10000. These are the parameters on the page
and in the certificate's README; the JSON certificate (R = 4000,
μ = [1221, 10000]) agrees. Parseval on [0, 2π]² (area 4π²) gives

- ‖∇u‖² = 4π² S₁, ‖Δu‖² = 4π² S₂, and u(0) = S₀,
- where S₀ = Σ_n r₂(n) c(n), S₁ = Σ_n r₂(n) n c(n)², S₂ = Σ_n r₂(n) n² c(n)²,
  and r₂(n) = #{k ∈ ℤ² : |k|² = n} for 1 ≤ n ≤ 4000².

Let v = u/‖∇u‖. Then ‖∇v‖² = 1 and ‖Δv‖² = δ_u := S₂/S₁, so
4πΘ(δ_u) ≥ 4π|v(0)|² = S₀²/(πS₁). Since δ_u ≈ 3.929 ≥ 1, this gives

  L ≥ S₀²/(πS₁) − ln δ_u − ln(1 + ln δ_u).

The normalisation matters. With [0, 2π]² and Lebesgue measure, the leading
coefficient 1/(4π) on the page is the right one: for c_k = |k|⁻², both
S₀²/(πS₁) and ln δ grow like 2 ln M.

## What the checker does

`check_c16_lower.py` uses numpy and python-flint; without either it stops
with an import error (it never skips a check).

1. **r₂ table.** The checker counts r₂(n) for all n ≤ 1.6·10⁷ directly from
   the lattice. It then checks the table two ways: the total must equal the
   Gauss circle count Σ_a (2⌊√(R²−a²)⌋+1), which gives 50265328 nonzero
   lattice points, and **every** entry must equal Jacobi's
   4(d₁(n) − d₃(n)). Both hold.
2. **Method A.** Each of the about 3·10⁶ nonzero-n terms is a 128-bit Arb
   ball (c(n) = 10000/(n(10000+1221n)), all exact integers before the
   division), summed in ball arithmetic.
3. **Method B.** Each term is computed in IEEE binary64 from exact integers,
   using at most 3 correctly rounded operations, so its relative error is at
   most (1+u)³/(1−u)³ − 1. The terms are summed with `math.fsum`, which
   returns the correctly rounded value of the exact sum. All terms are
   positive, so each sum has relative error ≤ (1+u)⁴/(1−u)³ − 1 ≈ 7.8·10⁻¹⁶.
   This bound is computed exactly with `Fraction` and rounded up. An earlier
   draft computed it as `(1+u)**4 - 1` in floating point, which evaluates to
   0. The A/B overlap test caught that bug before any result was recorded.
4. L is formed from each set of enclosures in Arb and compared with
   2.1562247706. A and B must overlap, and they do.
5. For information, the certificate's own rational lower bound
   (≈ 2.156224770644234) is checked to lie below enclosure A. It does.

## Reproduce

```bash
git clone https://github.com/maximusrufus/c16-bgw-certificates && git -C c16-bgw-certificates checkout 0c570700f080ca23549e10380901addfc8b7b8ae
```

```bash
python3 -I verification/16a/check_c16_lower.py --json c16-bgw-certificates/lower_certificate.json
```

The JSON is read as data only, for R and μ and the optional comparison. Its
SHA-256 is `de314c10bd4a63d35604d28c0d0556b8b5ae67ab1840c06628039d8fd64b6991`.
The constant page pins no commit for this certificate, so I used the
repository HEAD at the time, `0c57070`. The check does not actually need the
JSON: R and μ are stated on the page. The run took 27 s in total (two
trial functions), using about 400 MB of memory, on Python 3.13.18,
numpy 2.5.3 and python-flint 0.9.0. The log is in
[`run_output.txt`](run_output.txt); it is the re-run on branch
`replay/package` (the original run of 3 November 2026 is in the git history
of this file, and the numbers are identical).

## Assumptions

- The definition is the "equivalently" form above, on [0, 2π]² with Lebesgue
  measure, as on the page at fork commit `87b4ebb`.
- Arb ball arithmetic is rigorous. numpy float64 `+ × ÷` are correctly
  rounded IEEE operations (no fused operations in these element-wise ufuncs).
  `math.fsum` returns the correctly rounded sum. These are the standard
  guarantees of the libraries. A/B agreement to 13 digits is consistent with
  them.

## Independence

I read the constant page and the certificate repository's README. I did not
open `verify_c16_lower.py`, `certify_c16_lower.py` or the upper-bound scripts.
The checker was written by an AI agent (Claude) working for the owner of this
fork, and is not a human review.

## Corrections made on branch `replay/package` (4 November 2026)

- The caveat on the definition now says plainly that the bound would be false
  under the literal reading of the page's first sentence, and cites the source's
  definition (AUDIT.md §5, item 1).
- The docstring of `check_c16_lower.py` described method B's error bound
  incorrectly ("at most 4 correctly rounded operations … < 6u"); it now
  matches the code and this README (AUDIT.md §5, item 8). The code was
  already right.
