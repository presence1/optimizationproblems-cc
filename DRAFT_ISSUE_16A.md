<!-- Suggested title: C_16 (16a): which reading of the definition is intended? -->

The 16a page states its definition twice, and the two statements seem to define different constants. Which one is intended? The answer decides whether the asterisked lower bound 2.1562247706\* is correct, and also [Pat2026]'s 2.156224.

### The two statements

Both are in "Description of constant" ([lines 5–22](https://github.com/teorth/optimizationproblems/blob/87b4ebbd426ff8db597a2004cc45da17903bdcf2/constants/16a.md?plain=1#L5-L22)):

1. The inequality is required to hold "for all zero-mean functions u ∈ H²(𝕋²) **with sufficiently large frequency ratio** δ(u)".
2. "Equivalently, $L = \max_{\delta \ge 1} \left[ 4\pi\Theta(\delta) - \ln\delta - \ln(1+\ln\delta) \right]$."

Write $F(\delta) = 4\pi\Theta(\delta) - \ln\delta - \ln(1+\ln\delta)$.

### Reading A: every zero-mean u (the maximum over δ ≥ 1)

- Every zero-mean u has δ(u) ≥ 1, because |k|⁴ ≥ |k|² for every nonzero k in ℤ². So under this reading the qualifier "sufficiently large frequency ratio" changes nothing, and statement 1 agrees with statement 2.
- **Then 2.1562247706\* holds.** The certificate's trial function gives 2.15622477064423579…, enclosed rigorously, a margin of 4.4·10⁻¹¹. [Pat2026]'s 2.156224 holds too.
- Numerically, the untruncated maximum is F ≈ 2.156225528 at δ* ≈ 3.9288. That is inside the page's bracket [2.1562247706\*, 2.1562256466\*]. (This is high-precision numerics, not an interval computation.)

### Reading B: only u with δ(u) ≥ δ₀, for δ₀ as large as one likes

- The best constant is then governed by the limit of F(δ) as δ → ∞. That limit is (β+π)/π = 1.8228252497…, the quantity [BDZ2013] calls $L_\infty$.
- Every L > (β+π)/π is admissible. L = (β+π)/π itself is not, because F stays strictly above its limit. So there is no smallest constant, and the infimum is (β+π)/π, which is the page's own [BDZ2013] lower-bound row.
- **Then 2.1562247706\* would be false**, and so would 2.156224. The upper bound 2.1562256466\* would remain true, but far from sharp.
- A moderate fixed threshold does not help either: with δ₀ = 5, the supremum of F over δ ≥ 5 is numerically about 2.1547, below the claim.

### Evidence that reading A is meant

- **The source.** [BDZ2013], arXiv:1012.2061v1; I have not seen the 2013 journal version.
  - Theorem 3.8 states inequality (3.19) "for all 2π × 2π-periodic functions u with zero mean". In (3.20) it defines $L := \max_{\delta \ge 1} \lbrace 4\pi\Theta(\delta) - (\log\delta + \log(1+\log\delta)) \rbrace$, attained at a finite δ*.
  - Neither Theorem 3.8 nor the statement (1.9) in the introduction restricts the inequality to large δ.
  - Page 4: "$L \ge L_\infty := (\beta+\pi)/\pi$ … the numerics shows that $L \ge L_{\mathrm{opt}} > L_\infty$".
- **The page itself** presupposes reading A in several places:
  - the "Equivalently" formula;
  - [BDZ2013]'s maximiser δ* ≈ 3.92888, in the upper-bound table;
  - [Pat2026]'s trial function at δ ≈ 3.93181;
  - the upper-bound certificate's interval branch-and-bound over δ;
  - "The maximum in the variational definition is unique and achieved at finite δ*", under "Additional comments".
- **Numerical values of F** along the exact extremal family (the family [BDZ2013] uses):

  | δ | 3.93 (the maximum) | 148.5 | 1.1·10³ | 7.3·10⁴ | 5.5·10⁶ | 3.6·10¹⁰ | → ∞ |
  | --- | --- | --- | --- | --- | --- | --- | --- |
  | F(δ) | 2.156225528 | 2.0865 | 2.0538 | 2.0074 | 1.9771 | 1.9402 | 1.82283 |

### Suggested fix, if reading A is intended

In the first sentence, replace "with sufficiently large frequency ratio" with something like "for all zero-mean u ≠ 0 (every such u has δ(u) ≥ 1)".

If reading B is intended instead, the lower-bound rows above (β+π)/π would need revisiting.

### A side note

[BDZ2013]'s printed value L ∼ 2.15627 (p. 13) is about 4.5·10⁻⁵ above what its own formulas give at high precision: 2.15622552815 at δ* = 3.92884. The page already notes that the printed value lies above the certified upper bound. This recomputed value lies inside the page's bracket.

### Where this comes from

- This analysis was done by AI (Claude sessions), as part of an audit of an AI replay of the 16a lower bound. See `verification/16a/README.md`, and `audit/c16_readings.py` with its log, at [presence1/optimizationproblems-cc @ `c16fe56`](https://github.com/presence1/optimizationproblems-cc/tree/c16fe56894c5c725faa9acb7c2743db31d25c304).
- I am not a mathematician, and I have not verified the mathematics. I did check that the passages quoted above appear in arXiv:1012.2061v1.
- This issue was drafted with Claude's help.
- A pull request recording the replay of the lower bound will follow. Its 16a sentence depends on the answer here.
