# Independent check of the asterisked lower bound on C_70

Constant: [C_70, the reverse Brunn–Minkowski constant](../../constants/70a.md).
It is the infimum of the C such that for every n and every pair of centrally
symmetric convex bodies B₁, B₂ ⊂ ℝⁿ there is a linear u with |det u| = 1 and
|u(B₁) + B₂|^{1/n} ≤ C (|B₁|^{1/n} + |B₂|^{1/n}).

## Verdict

| Row of `constants/70a.md` | Claimed | Artifact | Result |
| --- | --- | --- | --- |
| line 55, [Pin2026] | C_70 ≥ 1.20194336* | `certificates/c70_candidate.json` @ `680e074` (n = 10¹², k = 367879441172, a/κ_n^{1/n} = (n−k)/k) | **Confirmed, given Patankar's cube–ball criterion** (re-derived below). Two independent rigorous enclosures give R_{n,k} = 1.20194336844315056699480277973552413…, so R_{n,k} > 1.20194336 = 3756073/3125000 with margin 8.4·10⁻⁹ |
| line 54, [Pat2026] (calibration only, not asterisked) | C_70 ≥ 1.201927 | n = 300000, a/r = 13/1000, full Steiner sum | Reproduced: R = 1.201927142572502844960989 ± 3·10⁻²⁶. This matches the value the [Pin2026] paper reports for its replay of this witness |

The page also mentions the limit exp(1/(2e)) > 1.20194336847, which the
paper proves analytically. That is not the number in the bound column, and I
did not verify the limiting argument rigorously. I did check two things about
it. Numerically, exp(1/(2e)) = 1.20194336847031446719… > 1.20194336847. And my
own Stirling heuristic (below) gives the same limit −(θ/2) log θ.

## The reduction (re-derived)

Take B₁ = [−a/2, a/2]ⁿ and B₂ = the unit ball. Let κ_m = π^{m/2}/Γ(1+m/2) be
the volume of the unit m-ball. Let u be any linear map with |det u| = 1, and
let v_1, …, v_n be the edge vectors of the parallelotope P = u(B₁), so that
vol P = aⁿ.

1. **Intrinsic volumes of a parallelotope** (classical zonotope formula):
   V_j(P) = Σ_{|S|=j} vol_j(v_i : i ∈ S).
2. **Szász-type bound.** Let δ_i be the squared distance from v_i to
   span(v_1, …, v_{i−1}), so that Π_i δ_i = (vol P)² = a^{2n}. For
   S = {i_1 < … < i_j}, vol_j(v_S) is the product of the distances from each
   v_{i_l} to the span of the earlier members of S. Each such distance is at
   least √δ_{i_l}, because that span lies inside span(v_1, …, v_{i_l−1}). So
   vol_j(v_S)² ≥ Π_{i∈S} δ_i. Taking the product over all C(n,j) subsets gives
   Π_S vol_j(v_S)² ≥ (a^{2n})^{C(n−1,j−1)}.
3. **AM–GM** over the C(n,j) subsets then gives
   V_j(P) ≥ C(n,j) · a^{2n·C(n−1,j−1)/(2C(n,j))} = C(n,j) a^j.
4. **Steiner's formula** gives |P + B₂| = Σ_j V_j(P) κ_{n−j} ≥ Σ_k C(n,k) a^{n−k} κ_k.
   Every term is positive, so in particular |P + B₂| ≥ C(n,k) a^{n−k} κ_k for
   each k.

This holds for **every** admissible u, and |B₁|^{1/n} = a, |B₂|^{1/n} = κ_n^{1/n}.
So any constant C that works for this pair, for some u, satisfies

  C ≥ R_{n,k} := (C(n,k) a^{n−k} κ_k)^{1/n} / (a + κ_n^{1/n}).

The certificate takes a = ((n−k)/k) κ_n^{1/n}. Simplifying, with t = k/n,
gives the closed form

  log R_{n,k} = log C(n,k)/n + (1−t) log(1−t) + t log t + (t·log((n/2)!) − log((k/2)!))/n,

where k and n are even, so the powers of π cancel. This agrees with the
paper's eq. (factorial). Stirling's formula gives log R_{n,k} → −(t/2) log t,
which is maximised at t = 1/e with value 1/(2e).

Steps 2–4 are elementary and I checked them line by line. Step 1 and Steiner's
formula are classical results that I used without re-proving. The audit
(AUDIT.md §3.3, another Claude session) later re-derived step 1 from the
external-angle formula and tested steps 1–4 numerically; no human has
reviewed the argument.

## What the checker does

`check_c70.py` uses python-flint (Arb) and mpmath.

- **Method 1** (Arb ball arithmetic, 256 bits) evaluates the criterion's
  expression *literally*: log C(n,k) and log κ_m via Arb's `lgamma`, a from its
  definition, then the ratio. It uses none of the simplification above.
  Result: [1.2019433684431505669948027797355241 ± 3.8·10⁻³⁵].
- **Method 2** (mpmath interval arithmetic, 60 digits) evaluates the
  simplified closed form. Every log m! is enclosed by Robbins' inequality
  (m+½)log m − m + ½log 2π + 1/(12m+1) < log m! < … + 1/(12m), and no
  log-gamma routine is used. Result:
  [1.201943368443150566994802779735524137829, …524138179], width 3.5·10⁻³⁷.
  mpmath raises an exception for an undecidable interval comparison, so the
  reported "True" for 3756073/3125000 < R is a certain inequality.
- The two enclosures overlap, and both exceed 3756073/3125000.
- **Calibrations.** The full Steiner sum at n = 2, a = √π equals the closed
  form √(1/2 + 1/√π) quoted on the page. The full sum at Patankar's
  n = 300000, a = 13/1000 reproduces 1.2019271425725028449609…. The
  self-test also checks method 1 against method 2 at (n, k) = (10³, 368),
  (10⁶, 367880) and (2·10⁸, 73575888), and checks that a single term never
  exceeds the full sum (n = 40).
- For information, it reports R at k ± 2, which is equal to 22 digits since
  the optimum is flat, and exp(1/(2e)).

## Reproduce

```bash
git clone https://github.com/rpinho/c70-certificate && git -C c70-certificate checkout 680e074bb50929734bfd76484d716cd3e85827f0
```

```bash
python3 -I verification/70a/check_c70.py --selftest
```

```bash
python3 -I verification/70a/check_c70.py --json c70-certificate/certificates/c70_candidate.json
```

The certificate file's SHA-256 is
`03ff0d6df3dfa6ea06f901a9319c968eb7c013f5d0cc3f1f00cfa58e9490c0cc`, which
equals the entry in that repository's `SHA256SUMS`. The constant page records
no file hash, only the commit. The checker only reads the four parameters and
compares them with the page. Runtime is under 0.1 s for the bound itself and
3.6 s including the n = 300000 calibration sum, on Python 3.13.18,
python-flint 0.9.0 and mpmath 1.4.1. The run is in
[`run_output.txt`](run_output.txt); it is the re-run on branch
`replay/package` (the checker itself is unchanged there; the original run of
3 November 2026 is in the git history of this file, with the same numbers).
Without python-flint or mpmath the checker stops with an import error; it
never skips a check.

## Assumptions

- The definition is the one on the constant page at fork commit `87b4ebb`.
- The criterion depends on the classical zonotope intrinsic-volume formula
  (step 1) and Steiner's formula. I did not re-prove either.
- Arb's `lgamma` and its elementary functions, and mpmath's interval `log`
  and `exp`, return rigorous enclosures. Robbins' factorial bounds (1955) hold.
  The two methods share neither the gamma-function code nor the formula they
  evaluate, so a single library bug would have to affect both in the same way.

## Independence

I read the constant page, the certificate repository's README and JSON, and
the statements in its paper (Lemma 1 and eqs. (ratio)–(factorial)). I did not
open or run `verify_c70_arb.py` or `independent/verify_c70_rational.py`.

To be precise about what was re-derived: before reading the paper, I worked
out from the page's description that the retained term must be
C(n,k) a^{n−k} κ_k, and I derived its limit. The Gram–Schmidt proof of the
Szász-type step (step 2) is the paper's argument, which I read and then
checked line by line. It also follows from Szász's inequality in its standard
form. Like the submitter's checkers, this checker was written by an AI agent
(Claude). It is independent of their code, but it is not a human review.
