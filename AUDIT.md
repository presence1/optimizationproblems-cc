# Audit of the `verify/*` branches (C_1d, C_1c, C_70, C_16, C_49)

Audit date: 3 November 2026. §3.4 was updated the same day, after the fork owner
supplied the 16a source paper [BDZ2013]. Auditor: an AI agent (Claude, Anthropic),
working for the owner of this fork. **This is not a human review**, so the same caution
applies to it as to the work it audits.

The `verify/*` branches were not modified. Everything here is in this file and in
[`audit/`](audit/) on branch `audit/review`.

| Branch | Tip audited | Adds |
| --- | --- | --- |
| `verify/1d` | `04247b2` | `verification/1d/` (checker, README, `fetch.sh`, run log), `VERIFY_LOG.md` |
| `verify/1c` | `1bcd744` | `verification/1c/` (same layout), `VERIFY_LOG.md` |
| `verify/70a` | `e957bb5` | `verification/70a/`, `VERIFY_LOG.md` |
| `verify/16a` | `4659ded` | `verification/16a/`, `VERIFY_LOG.md` |
| `verify/49a` | `150f084` | `verification/49a/` (three checkers, three run logs), `VERIFY_LOG.md` |

Pull-request numbers, for example [#292](https://github.com/teorth/optimizationproblems/pull/292),
refer to upstream `teorth/optimizationproblems` and link there.

All five branches start from fork commit `87b4ebb`. That commit is also the
current head of upstream `teorth/optimizationproblems`, so the constant pages
audited here are the live ones. `VERIFY_LOG.md` is byte-identical on all five
branches.

---

## 1. Verdicts

**How many bounds are claimed?** The task statement says 15. `VERIFY_LOG.md`
marks **13** rows as confirmed:

- 1d: 3 rows (STEPS2026, AER2026, and CERT2026 at 1.4630715826075594);
- 1c, 70a and 16a: 1 row each;
- 49a: 7 rows (74–80).

Of these 13, **12 are asterisked** bounds. The CERT2026 row at
1.4630715826075594 has no asterisk; [T2026] had already replayed it. Nothing in
the branches supports the figure 15.

| Constant / row | Claimed bound | Verdict |
| --- | --- | --- |
| 1d, STEPS2026 | C_1d ≤ 1.460217284022874* | **Stands.** |
| 1d, AER2026 | C_1d ≤ 1.459989046905384* | **Stands.** |
| 1d, CERT2026 (replayed row) | C_1d ≤ 1.4630715826075594 | **Stands.** Not asterisked. On the duplicate row see §5, item 2, and §6.2. |
| 1d, CERT2026 (starred duplicate) | C_1d ≤ 1.463071582607559* | **Problem, already known.** The certificate does not imply this value: its exact R is 3.3·10⁻¹⁶ higher (3.0·10⁻¹⁶ under the decimal reading). The page and upstream already record this, and the branch says so correctly. |
| 1c, Kos2026 | C_1c ≥ 0.4103333* | **Stands.** |
| 70a, Pin2026 | C_70 ≥ 1.20194336* | **Stands with caveats**: (a) it depends on Patankar's cube–ball criterion. I re-derived the criterion (§3.3) and tested it numerically; it rests on Steiner's formula and the parallelotope intrinsic-volume formula, both textbook. (b) No human has reviewed the argument. (c) The finite certificate does not certify the limit exp(1/(2e)). The page keeps the two apart, as it should. |
| 16a, lower bound | L ≥ 2.1562247706* | **Stands, with one caveat about the page's wording.** The bound holds for the constant as the source defines it: [BDZ2013] Theorem 3.8 takes the inequality for every zero-mean u, with L = max over δ ≥ 1, which is the page's "equivalently" formula. The page's first sentence adds "…with sufficiently large frequency ratio". That phrase is not in the source, and read literally it defines a different constant, whose infimum is (β+π)/π ≈ 1.82283 (the paper's L_∞). **For that constant the bound would be false.** The branch says only that it would "say nothing" (§3.4). The page's first sentence should be fixed. |
| 49a, rows 74–80 | 1.5617847*, 1.5621220*, 1.5647730*, 1.5664286*, 1.5666969*, 1.5675517*, 1.5678015* | **Stand with caveats**: (a) they depend on the XOR-gluing lemma. I give a clean proof and found no counterexample in an exhaustive search (§3.5). (b) Nobody here checked the lemma against [DEGKM1997]. (c) Row 79's 62-point family is far too large to enumerate, so its goodness rests on the lemma alone. (d) The page records no hash for IRSI v1.0. (e) Some page cross-checks in the checkers are printed but not enforced (§4). |

Rows that the branches marked "not checked" are still not checked: 1d SCIEL2026
(restricted Zenodo record), the 16a upper bound, and 49a row 81 (Kos2026). I
agree with all three choices. For row 81 I checked only the arithmetic from the
page's port counts (§3.5).

**No claimed bound is wrong.** The problems I found are in how the work is
described (§5), in checks that are printed but not enforced (§4), and in the
16a page's definition (§3.4).

---

## 2. Reproduction

I made a fresh clone of each branch from GitHub into a scratch directory, outside
any third-party repository. I fetched the data into separate empty directories,
exactly as each README says, and passed it to the checker by path. I ran only the
branches' own scripts, always with `python3 -I`.

Environment: Linux 6.18.44, 4 cores, Python 3.13.18, numpy 2.5.3, python-flint
0.9.0 and mpmath 1.4.1. These are the versions in the branches' logs.

| Branch | Commands run | Exit | Compared with the saved run log |
| --- | --- | --- | --- |
| 1d | `fetch.sh`, then `--selftest` and `--data DIR` | 0 | identical except timings |
| 1c | `fetch.sh`, then `--selftest` and `--data DIR --knots 24577 --interior 2000` | 0 | identical except timings |
| 70a | clone `rpinho/c70-certificate` @ `680e074`, then `--selftest` and `--json …` | 0 | identical except timings and the path |
| 16a | clone `maximusrufus/c16-bgw-certificates` @ `0c57070`, then `--json …` | 0 | identical except timings |
| 49a | cla2026 `--selftest` and default run; syl2026 `--data`; irsi2026 `--data` | 0 | all three identical except timings |

Every data hash matched its pin. All the "integrity" lines are OK. The 49a
scripts left no `__pycache__` behind, as commit `a5ab517` intends. My runtimes
were about 1.4 times the logged ones (1c took 288 s against 214 s) on a slower
VM. That is not a discrepancy.

**One environment trap.** `python3 -I` ignores the user site directory. If
python-flint is installed with `pip --user`, `check_c1d.py` silently skips its
FLINT cross-check (check B). The integrity line still reads OK; only the header
line changes, to "python-flint not installed (check B skipped)". The README does
call FLINT optional. Even so, anyone reproducing the run should confirm that the
header shows `python-flint 0.9.0`. The other checkers fail loudly without their
libraries.

`audit/fetch_all.sh` and `audit/run_all.sh` repeat all of the above, plus my own
checks. `fetch_all.sh` pins every input by commit, including the IRSI files,
which the README pins only by mutable tag. It also hash-checks all 12 data files.

---

## 3. Mathematics: independent re-derivations

For each constant I re-derived the reduction myself and then recomputed the
result with my own code. Shared code was ruled out: my code imports nothing from
the branches or from the certificate authors, and it uses different algorithms.

### 3.1 C_1d (upper bounds, step functions)

Let f = Σ_{i<N} v_i·1[−1/4+ih, −1/4+(i+1)h), with h = 1/(2N). Write Λ = 1[0,h) ∗ 1[0,h).
This is the tent of height h on [0, 2h], linear on [0, h] and on [h, 2h]. Then:

- f∗f(t) = Σ_s c_s·Λ(t + 1/2 − sh), where c_s = Σ_{i+j=s} v_i v_j.
- On each interval [−1/2 + mh, −1/2 + (m+1)h] every term is linear. So f∗f is
  piecewise linear, and its knot values are (f∗f)(−1/2 + mh) = h·c_{m−1}.
- The absolute value of a linear function on an interval is largest at an
  endpoint. Hence max_t |f∗f| = h·max_s |c_s|.
- Since ∫f = h·Σv_i, this gives **R(f) = 2N·max_s|c_s| / (Σv_i)²**.

Every f with ∫f ≠ 0 gives C_1d ≤ R(f), and that is exactly what the README
derives. There are two readings of the data:

- the printed decimals taken exactly;
- the binary64 doubles the decimals denote.

Each reading defines a genuine step function, so either one proves a bound.

`audit/c1_independent.py` recomputes every c_s with one big-integer square
(Kronecker substitution, with balanced digits for the signed coefficients). This
algorithm differs from the branch's direct double loop and from FLINT. The script
parses the AER2026 `.py` file with a strict text scanner rather than `ast`, and
never executes it. Results, matching the branch digit for digit:

| Certificate | R, binary64 reading | R, decimal reading | Printed bound | Margin |
| --- | --- | --- | --- | --- |
| STEPS2026 | 1.46021728402287398524… (equals the page's fraction) | 1.46021728402287397507… | 1.460217284022874 | 1.5·10⁻¹⁷ |
| AER2026 | 1.45998904690538324315… | 1.45998904690538314495… | 1.459989046905384 | 7.6·10⁻¹⁶ |
| CERT2026 | 1.46307158260755932746… (equals the page's fraction) | 1.46307158260755929963… | 1.4630715826075594 | 7.3·10⁻¹⁷ |

The page prints each bound rounded up, and the margins are tiny. That is fine:
both the checker and my recomputation compare exact rationals.

Side observation: under the decimal reading even 1.4630715826075593 would be
certified for CERT2026. Under neither reading is the starred 1.463071582607559.

### 3.2 C_1c (lower bound, step function)

Let f = Σ w_i·1[i/K, (i+1)/K) with w_i ≥ 0, and g(t) = ∫ f(x) f(x+t) dx. Then:

- g(t) = Σ_d A_d·T(t − d/K), where A_d = Σ_i w_i w_{i+d} and T is the tent of
  height 1/K on [−1/K, 1/K].
- On [k/K, (k+1)/K] only d = k and d = k+1 contribute, and both terms are linear.
  So the minimum over t ∈ [0, 1] is attained at a knot k = 0, …, K.
- Hence **L(f) = K·min_{0≤k≤K} A_k / (Σw)²**, and C_1c ≥ L(f).

My recomputation reads all the lags from one big-integer product (Kronecker
substitution) and agrees exactly:

- L = 134648548624804778248790016/328144294688458468928334649 = 0.41033335274849…
- The minimum is attained only at k = 21264.
- There are 24592 weights, the last 8 of them zero; the support is [0, 3073/3072).
- 22.08 % of the mass lies in [1/6144, 2/6144).
- The R2026 calibration also reproduces its stated fraction.

### 3.3 C_70 (Pin2026 ≥ 1.20194336*): the reduction and its two classical formulas

Take B₁ = [−a/2, a/2]ⁿ and B₂ = the unit ball Bⁿ, with κ_m = π^{m/2}/Γ(1 + m/2).
Let u be any linear map with |det u| = 1, and let v₁, …, v_n be the edge vectors
of P = u(B₁). Then vol P = aⁿ.

1. **Steiner's formula.** For any convex body K, |K + rBⁿ| = Σ_j V_j(K)·κ_{n−j}·r^{n−j}.
   Here the V_j are the intrinsic volumes, normalised so that V_j of a
   j-dimensional body is its j-volume (Schneider, *Convex Bodies: The Brunn–Minkowski
   Theory*, ch. 4).
2. **Intrinsic volumes of a parallelotope:** V_j(P) = Σ_{|S|=j} vol_j(v_i : i ∈ S).
   *Proof.* For a polytope, V_j(P) = Σ over j-faces F of γ(F,P)·vol_j(F), where
   γ(F,P) is the external angle (same chapter). The j-faces of P parallel to
   span(v_S) are the 2^{n−j} translates of the parallelotope spanned by v_S.
   Let w_i (i ∉ S) be the dual-basis vectors orthogonal to all v_k, k ≠ i. They
   form a basis of span(v_S)^⊥. The normal cones of those 2^{n−j} faces are
   cone{±w_i : i ∉ S}, one for each sign pattern. These cones tile span(v_S)^⊥,
   so their external angles sum to 1, and summing over S gives the formula. ∎
3. **Szász-type product inequality.** Let δ_i be the squared distance from v_i
   to span(v₁, …, v_{i−1}), so that Π δ_i = (vol P)² = a^{2n}.
   - For S = {i₁ < … < i_j}, vol_j(v_S) is the product of the distances from each
     v_{i_l} to the span of the earlier members of S. That span lies inside
     span(v₁, …, v_{i_l −1}), so each distance is at least √δ_{i_l}.
   - Hence vol_j(v_S)² ≥ Π_{i∈S} δ_i. Each i belongs to C(n−1, j−1) of the
     j-subsets, so Π_S vol_j(v_S)² ≥ (a^{2n})^{C(n−1, j−1)}.
4. **AM–GM** over the C(n, j) subsets then gives V_j(P) ≥ C(n, j)·a^{2n·C(n−1,j−1)/(2C(n,j))} = C(n, j)·a^j.
5. Combining 1–4: |u(B₁) + Bⁿ| ≥ Σ_k C(n, k)·a^{n−k}·κ_k ≥ C(n, k)·a^{n−k}·κ_k for
   every u and every single k. The ratio is scale invariant, so
   **C_70 ≥ (C(n, k)·a^{n−k}·κ_k)^{1/n} / (a + κ_n^{1/n})**.
   - With a = ((n−k)/k)·κ_n^{1/n} and t = k/n, the powers of π cancel and
     log R = log C(n,k)/n + (1−t)log(1−t) + t log t + (t·log((n/2)!) − log((k/2)!))/n.
     This matches the README and eq. (factorial) of the Pin2026 paper. I read
     that paper's statement of the lemma; it is the same argument.
   - The cube on the page's Pat2026 row, [0, a]ⁿ, is not origin-symmetric.
     Volume is translation invariant, so this changes nothing, and the branch and
     the paper both use [−a/2, a/2]ⁿ.

Numerical tests (`audit/c70_independent.py`):

- **Steiner plus the parallelotope formula**, in ℝ² and ℝ³ with random
  parallelotopes: I estimated |P + rB| by Monte Carlo, using an exact
  point-to-parallelotope distance.
  - The Monte Carlo values agree with the formula: over 16 further seeded runs
    (`--mc-repeats 16`) the z-scores have mean −0.32 and sd 0.81.
  - A deliberately wrong normalisation (each V_j with 0 < j < n halved) is
    rejected at z > 370.
- **The Szász/AM–GM step** on 300 random unimodular *integer* matrices, with
  exact Gram determinants: the smallest value of V_j/(C(n,j)·a^j) is exactly 1,
  attained by signed permutations, and it never falls below 1. An earlier float
  version of this test reported 0.999985; that was round-off on ill-conditioned
  matrices, which the exact test removes.
- **A third enclosure** of R at n = 10¹², k = 367879441172, using only the
  standard library: `decimal` (correctly rounded ln/exp), Robbins' factorial
  bounds, and π from Machin's formula. Result:
  [1.2019433684431505669948027797355241378286, …1381785].
  - Width 3.5·10⁻³⁷. It lies inside the branch's Arb ball, and overlaps the branch's
    mpmath interval, from which it is offset by 4·10⁻⁴⁰ (far less than either width).
  - The margin over 1.20194336 is 8.443·10⁻⁹.
  - The same code rejects the claims 1.2019433685 and 1.20194336847 (the limit's
    decimal).
  - The literal criterion and the closed form agree to 10⁻⁵⁹ at n = 10³ and 10⁴.
- The page's n = 2 value √(1/2 + 1/√π) ≈ 1.0316 is the true maximum over a for
  n = 2. Also exp(1/(2e)) = 1.20194336847031… > 1.20194336847.

### 3.4 C_16: does "equivalently" match the first sentence?

Write F(δ) = 4πΘ(δ) − ln δ − ln(1 + ln δ). The page's first sentence asks for the
inequality "for all zero-mean u ∈ H²(𝕋²) with sufficiently large frequency ratio
δ(u)". There are two readings:

- **(a) Every zero-mean u.** Every such u has δ(u) ≥ 1, because |k|⁴ ≥ |k|² on
  ℤ²∖{0}, so the qualifier is vacuous. Normalise ‖∇u‖ = 1 and use translation
  invariance (sup|u| equals |u(0)| for a suitable translate). This gives exactly
  L_a = sup_{δ≥1} F(δ), the "equivalently" formula. Under (a) the two sentences
  agree.
- **(b) Only u with δ(u) ≥ δ₀, for δ₀ as large as one likes.** Then L is
  admissible exactly when F(δ) ≤ L for all large δ, so the best constant is
  governed by limsup_{δ→∞} F(δ). This is a different constant.

**The exact extremals.** For μ > 0 put c_k = 1/(|k|²(1 + μ|k|²)) for every k ≠ 0,
and let S₀ = Σc_k, S₁ = Σ|k|²c_k², S₂ = Σ|k|⁴c_k².

- Cauchy–Schwarz with weights |k|² + μ|k|⁴ gives 4πΘ(δ) ≤ S₀(μ)(1 + μδ)/π for every μ.
- Equality holds at u = Σ c_k e^{ik·x} when δ = δ(μ) = S₂/S₁.
- Hence F(δ(μ)) = S₀²/(πS₁) − ln δ − ln(1 + ln δ) **exactly**, and δ(μ) → ∞ as μ → 0.

**The small-μ expansions** come from a Mellin transform. Write
Z(s) = Σ_{k≠0} |k|^{−2s} = 4ζ(s)L(s, χ₄). Then Z(s) = π/(s−1) + β + O(s−1) at
s = 1 (Kronecker's limit formula), Z(0) = −1, and Z(−m) = 0 for m ≥ 1. This gives:

- S₀ = π ln(1/μ) + β + μ + o(μ^M);
- S₂ = π/μ − 1 + o(μ^M);
- S₁ = S₀ − μS₂;

where β = π(2γ + 2 ln 2 + 3 ln π − 4 ln Γ(1/4)). Substituting gives
F → 1 + β/π = (β + π)/π = **1.8228252497…**, approached from above like
(ln ln(1/μ))/ln(1/μ).

`audit/c16_readings.py` checks this numerically:

- The Kronecker constant: Z(1+ε) − π/ε → 2.58498175958 = β.
- Direct lattice sums with integral tails agree with the expansions, to 2·10⁻¹⁰
  at μ = 0.01 and already to 10⁻⁷ at μ = 0.1221.
- F along the exact family:

| δ | 3.93 (the maximum) | 148.5 | 1.1·10³ | 7.3·10⁴ | 5.5·10⁶ | 3.6·10¹⁰ | → ∞ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F(δ) | 2.156225528 | 2.0865 | 2.0538 | 2.0074 | 1.9771 | 1.9402 | 1.82283 |

Conclusions:

- **Under reading (a)** the bound holds.
  - The certificate's truncated trial function gives 2.15622477064424. My own
    float lattice sums reproduce the branch's S₀, S₁, S₂ to about 10⁻¹⁵.
  - The bound in fact follows from the first sentence directly, because
    ‖u‖_∞ ≥ |u(0)|.
  - The untruncated maximum is F = 2.156225528 at δ* = 3.9288. This sits inside
    the page's bracket, below the upper bound 2.1562256466*.
  - It also agrees with the value in pending upstream PR [#319](https://github.com/teorth/optimizationproblems/pull/319). BDZ2013's 2.15627
    lies above it, as the page itself notes.
- **Under reading (b)** every L > (β+π)/π ≈ 1.82283 is admissible. L = (β+π)/π
  itself is not, because F stays strictly above its limit, as BDZ show in the
  proof of their Theorem 3.8. So
  there is no smallest constant, and the infimum is (β+π)/π, which is the page's
  own [BDZ2013] lower bound. Then 2.1562247706*, and Pat2026's 2.156224, would
  be false.
  - Even with a fixed threshold δ₀ = 5, the supremum of F over δ ≥ δ₀ is
    numerically about 2.1547, below the claim.
  - The branch's README says that under the literal reading the trial function
    "would then say nothing". That understates it: under that reading the bound
    is false.
- The page's tables, the upper-bound certificate's branch-and-bound over
  δ ∈ [1, ∞), and BDZ2013's maximiser δ* ≈ 3.93 all presuppose reading (a). The
  source paper defines the constant that way too (below). So the bound stands for
  the constant as defined. **The first sentence of the page should drop "with
  sufficiently large frequency ratio".** It could say "for all zero-mean u ≠ 0
  (every such u has δ(u) ≥ 1)" instead.

**What the source paper says.** The fork owner supplied [BDZ2013] as arXiv
1012.2061v1 (9 December 2010). I have not seen the 2013 journal version, whose
wording or numbers could differ.

- **The definition.** Theorem 3.8 states inequality (3.19) "for all 2π × 2π-periodic
  functions u with zero mean". It defines the constant by
  (3.20) L := max_{δ≥1} {4πΘ(δ) − (log δ + log(1 + log δ))}. That is reading (a),
  and the same formula as the page's "equivalently" definition.
  - The theorem adds that the maximum is attained at a finite δ*, and that the
    extremal u_{μ(δ*)} is exact.
  - Its proof shows L > (β+π)/π ≈ 1.82283.
  - Neither Theorem 3.8 nor the introduction's statement of the inequality,
    (1.9), restricts it to large δ. The phrase "with sufficiently large frequency
    ratio" is the page's own addition. I read §§1–4 and the Appendix; §§5–6 treat
    the separate algebraic case.
- **(β+π)/π is the paper's L_∞,** the limit as δ → ∞ (p. 4: "L ≥ L_∞ := (β+π)/π
  … the numerics shows that L ≥ L_opt > L_∞"). This is precisely the constant
  that reading (b) would produce.
- **The rest of the set-up is the same as above.**
  - Θ (2.3) is defined as on the page.
  - The extremals (1.11)/(2.9) and the parametric formula (2.11) are the family
    I used.
  - The expansions (1.14), (3.7) and (3.8) are mine, with the exponentially small
    terms (of order e^{−2π/√μ}) written out.
  - β is the same constant (Appendix, (7.6)).
- **The numbers.** The paper reports, as numerical results (p. 13), δ* ∼ 3.92888,
  μ ≈ 0.12211 and L ∼ 2.15627. I evaluated its own exponentially convergent
  Bessel-series form of the lattice sums (Lemma 3.1, Remark 3.6) at 30 digits and
  maximised F:
  - **L = 2.15622552815 at δ* = 3.92884, μ* = 0.12211.** δ* and μ agree with the
    paper, but its printed L is 4.45·10⁻⁵ too high.
  - The paper's own table of Θ (p. 4) matches my evaluation to every printed
    digit at δ = 2 and δ = 4: 0.26651 and 0.35112, and Θ₀ = 0.26660 and 0.35112.
    So the table is consistent with L ≈ 2.1562255 and not with 2.15627.
  - The page already notes that the paper's value "lies above the certified upper
    bound". The recomputed L lies inside the page's bracket
    [2.1562247706*, 2.1562256466*], about 1.2·10⁻⁷ below the upper bound. It also
    matches the 2.156225528* of pending PR [#319](https://github.com/teorth/optimizationproblems/pull/319).
  - This maximisation is high-precision numerics, not an interval computation.
- **Minor slips in the paper,** none affecting the page:
  - Remark 3.6 prints the coefficient of the K₀ series for f as 8π. 2π is what
    integrating the h-series gives; it matches (3.7) and reproduces the direct
    lattice sum (8π would shift S₀ by 3.4·10⁻⁷ at μ = 0.1221).
  - Θ(1) is printed as 0.10134; exactly, it is 1/π² = 0.101321.
  - Lemma 3.1 reads "as μ → ∞" where μ → 0 is meant.
  - Theorem 2.3 says "δ > 0" where δ ≥ 1 is needed (Lemma 2.1).
  - The comparison Θ ≤ Θ₀ (1.15) is verified only numerically, as Remark 3.5
    says.

### 3.5 C_49: the XOR-gluing lemma

Call a family *good* if it is Sperner and contains no 3-sunflower.

**Lemma.** Let F₁ be good on X with a point x, and F₂ good on a disjoint Y with a
point y. Put G = {(A∖x) ∪ (B∖y) : A ∈ F₁, B ∈ F₂, exactly one of x ∈ A, y ∈ B}
on (X∖x) ∪ (Y∖y). Then (i) the map (A, B) ↦ member of G is injective, and (ii)
G is good.

*Proof.* Write s = [x ∈ A] and t = [y ∈ B] = 1 − s. A member S determines
A∖x = S ∩ X and B∖y = S ∩ Y.

- **(i) Injectivity.** Suppose two pairs give the same S. If s = ŝ, the pairs are
  equal. Otherwise A and Â differ exactly in x, so one strictly contains the
  other, which Sperner forbids.
- **(ii) Sperner.** Suppose S₁ ⊊ S₂.
  - If s₁ ≤ s₂, then A₁ ⊆ A₂, so A₁ = A₂. Then s₁ = s₂, t₁ = t₂ and B₁ ⊆ B₂,
    so B₁ = B₂ and S₁ = S₂, a contradiction.
  - If s₁ = 1 and s₂ = 0, then B₁ = B₁∖y ⊆ B₂∖y ⊊ B₂, which Sperner forbids.
- **(ii) No sunflower.** Suppose distinct S₁, S₂, S₃ have equal pairwise
  intersections. Intersecting with X∖x and with Y∖y, the A_i∖x have equal
  pairwise intersections, and so do the B_i∖y.
  - A fact about Sperner families: if three members, not necessarily distinct,
    have equal pairwise intersections, then they are all equal or all distinct.
    Indeed, if T₁ = T₂ ≠ T₃, then T₁ = T₁ ∩ T₂ = T₁ ∩ T₃ ⊆ T₃, so T₁ ⊊ T₃, which
    Sperner forbids.
  - *All s_i equal.* Then x lies in all A_i or in none, so the A_i have equal
    pairwise intersections; likewise the B_i. Not both triples can be constant,
    since then S₁ = S₂ = S₃. So one triple is a sunflower in F₁ or in F₂.
  - *Exactly one s_i = 1.* Then x is in no pairwise intersection, so the A_i
    have equal pairwise intersections and are not all equal. By the fact they are
    all distinct, which gives a sunflower in F₁.
  - *Exactly two s_i = 1.* Then exactly one t_i = 1, and the same argument gives
    a sunflower in F₂. ∎

This is the README's proof; I checked every step. Both hypotheses are needed:

- Without Sperner, F₁ = {∅, {x}} glued to itself already breaks injectivity.
- The "same status, drop the merged point" rule fails on good families on 3 points.

My tests found both failures automatically.

**Chains and transfer matrices.** Glue copies of a good family B (ports u ≠ v),
each copy's v to the next copy's u. By induction every chain G_k is good.
Write N_ab = #{S ∈ B : [u ∈ S] = a, [v ∈ S] = b}. By (i), |G_k| counts the tuples
(A₁, …, A_k) with [v ∈ A_i] + [u ∈ A_{i+1}] = 1. That count is a product of the
transfer matrices T[a][a′] = N_{a,1−a′}, indexed by the u-status. For a positive
2×2 matrix T with Perron root ρ, |G_k| ≥ c·ρ^k; take a positive eigenvector.
Each period adds p points, so f(pk + 2) ≥ cρ^k. The page proves that the limit
exists, hence C_49 ≥ ρ^{1/p}.

Tree gluings (the Syl2026 gadget and unit) count the same way. By (i), every
pendant multiplies a member's count by the number of compatible pendant members,
which is 46 or 75 for H at a point.

**Searching for counterexamples** (`audit/c49_independent.py`):

| Test | Result |
| --- | --- |
| Every ordered pair of good families on ≤ 4 points (2, 5, 18 and 129 families), every port: 338,724 gluings | 0 injectivity failures, 0 goodness failures |
| Every pair of (family, port) classes up to relabelling on ≤ 5 points (3,222 good families on 5 points, 266 classes): 90,151 gluings | 0 failures |
| 400 random gluings, uniform and non-uniform families, 4–7 points | 0 failures |
| Explicit XOR chains F–F (2,728 sets), H–H (6,900), F–H and H–F (4,349 each) | sizes equal the transfer-matrix prediction; distinct, Sperner, no sunflower (all pivots) |
| F–F–F (98,920 sets on 26 points) | size equals the prediction; Sperner; no sunflower through 300 random pivots |

The branch's own self-test checks (ii) only. Its `glue()` returns a set, which
hides duplicates, so (i) is proved there but never tested. Yet (i) is what makes
the counts correct. My tests cover (i).

**The rows themselves**, rechecked with different algorithms:

- Sunflowers: a kernel-bucket search. For each pivot A, the other members are
  grouped by trace on A; a bucket must not hold two members whose parts outside A
  are disjoint.
- Sperner: a zeta transform over the Boolean lattice.
- Bounds: decided in exact integer arithmetic, c < ρ^{1/p} ⟺ c^p < (tr + √disc)/2, with no floating point.

What these checks confirm:

- F (rebuilt by classifying all 2¹⁰ graphs on K₅ by their invariants) and H are
  good. Every ordered port pair gives (11, 20, 20, 24) and (15, 31, 31, 44).
- The row-79 gadget, built explicitly, has 250,659 = 98,308 + 152,351 sets, and
  the unit's port counts equal the page's.
- B rebuilt equals `data/B.txt`. B′ (4,364 sets) and IRSI v1.0, v1.1 and v1.2
  are good, and their port matrices equal the page's.
- Rows 74–80 all hold exactly. Row 81's arithmetic is also consistent with the
  page's port counts, but the 252,292-set family was not checked by anyone here.

---

## 4. Mutation tests: can the checkers fail?

`audit/mutation_tests.py` runs 38 perturbations. Each one copies the data, or
patches a copy of the checker, in a scratch directory; the branches are never
touched. Each copy is then run with `python3 -I`. Where a file is hash-pinned,
the data was mutated twice: once with the pin intact, where the checker must stop
at the hash, and once with the pin updated, which exercises the mathematics.
Two tests (16a-3 and 49a-4) instead change a line of a checker's own logic, to
see whether its internal cross-checks can fail.

**Result: 37 of the 38 behaved as a correct checker must.** Full table:
[`audit/logs/mutation_tests.txt`](audit/logs/mutation_tests.txt).

| Group | Perturbations that made the checker fail, as required |
| --- | --- |
| 1d (6) | one value changed (pin intact; pin updated: R rises above the bound and the fraction no longer matches); an AER2026 literal changed (no recorded fraction, so the bound test alone must catch it); all three bounds nudged below the exact R under *both* readings; the page fraction's numerator +1; one cell dropped |
| 1c (7) | w₄ += 1 (pin intact; pin updated); 10¹² of mass added where lag 21264 cannot see it (L falls below the claim); bound nudged to 0.41033336; a negative weight; a non-integer weight; K changed |
| 70a (5) | claim raised to 1.2019433685; claim set to the limit's 1.20194336847; k = 3·10¹¹; JSON n changed; JSON side changed |
| 16a (4) | claim raised to 2.1562247707 (the margin is 4.4·10⁻¹¹); cutoff 1000 instead of 4000; lattice points (±7, 0) dropped from r₂, a code mutation (the Gauss count catches it); JSON μ changed |
| 49a (14) | F missing one set; F plus a set that closes a sunflower with Sperner kept; claim +10⁻⁷; a B′ extra set replaced by one that keeps the port statuses and avoids H but closes a sunflower (pin intact; pin updated: the search finds it); one extra set deleted; the row-80 claim nudged; the row-79 N₀₀ +1; IRSI v1.0 (no page hash) with a set replaced so as to close a sunflower (found), a duplicated set, a superset (Sperner fails), a changed port, a nudged claim; IRSI v1.2 with a set removed (pin catches it) |

Two findings:

- **49a-4, a code mutation rather than a data mutation.** I built the Cla2026
  transfer matrix with the wrong (same-status) convention. The checker still
  exits 0 and prints CONFIRMED.
  - It does print "20 + 2 sqrt(66): False" and "same trace/det: False".
  - Those page cross-checks are *not* part of its pass/fail decision. The same
    is true of the row-80 "1127 + sqrt(925536)" check in the Syl2026 checker,
    though row 79's closed form *is* enforced.
  - The wrong convention gives a larger ρ, so a convention bug would have passed
    unnoticed.
  - The convention actually used is correct: my explicit chains match the XOR
    counts. The weakness is in the checker's robustness, not in the result.
- **1c-8.** If the minimiser recorded on the page is changed, the checker prints
  "argmin matches the page: False" but still exits 0. The README says the
  minimiser is "compared … (equal)". It is compared but not enforced. This is
  harmless for the bound.

Design notes, not defects:

- The 1d checker accepts a bound if either reading confirms it. That is
  mathematically right, since each reading is a real function.
- The 70a and 16a checkers hard-code the parameters from the page and use the
  JSON only for a comparison. So a data mutation fails through that comparison,
  and a change of parameters fails through the mathematics.

---

## 5. The claims in the READMEs and `VERIFY_LOG.md`, checked against code and logs

**Verified as stated** (selection): every number in the five verdict tables and
run logs; every hash; the row line numbers; "66 asterisked rows across 30 constant
pages", which I recounted from the pages exactly. Also verified:

- every value and source key in the Candidates table;
- the 1c details (24592 weights, 8 trailing zeros, 22.08 %, minimiser unique);
- about 3·10⁸ products in check A for 1c, and about 3·10⁶ nonzero n for 16a;
- the 70a paper's lemma and eq. (factorial), and its reported value for the
  Patankar witness, 1.20192714257250284496…;
- mpmath raising an exception on an undecidable interval comparison;
- STEPS2026's checker being "also written by a Claude agent", as its README says;
- the 84b page crediting [T2026];
- the `vert` typos in the duplicated 1d comments.

**Flagged:**

| # | Where | Statement | Problem | Severity |
| --- | --- | --- | --- | --- |
| 1 | 16a README; `VERIFY_LOG.md` | "a trial function with δ ≈ 3.93 would then say nothing"; "The only discrepancy found is the stale duplicate row on the 1d page" | Understated. Under the literal first sentence the bound is false, because the best constant would then be (β+π)/π ≈ 1.82283, the source's L_∞ (§3.4). The source's Theorem 3.8 confirms the reading the branch used. The log's summary also leaves out the 16a definitional inconsistency that the README itself raises | moderate |
| 2 | 1d README; `VERIFY_LOG.md` | the starred CERT2026 row "looks like a superseded copy … left behind by a merge" / "a leftover from a merge" | Incomplete. Upstream, [#232](https://github.com/teorth/optimizationproblems/pull/232) and [#243](https://github.com/teorth/optimizationproblems/pull/243) were merged minutes after the maintainer posted a hold on asterisk removals. The replayer then asked on [#243](https://github.com/teorth/optimizationproblems/pull/243) which row should go ("if the hold stands, the unstarred row should go"), and no answer is visible. The arithmetic statements are right, but which row survives is a maintainer decision still pending | moderate |
| 3 | task statement | "15 bounds confirmed" | The documents claim 13 confirmations, 12 of them asterisked (§1) | minor |
| 4 | `VERIFY_LOG.md` | "the seven smaller certificates were all finite exhaustive checks" | Row 79's 62-point unit (1,086,359,092,267 ≈ 1.1·10¹² sets) is not checked exhaustively. Its goodness comes from the lemma, which the README itself says correctly | minor |
| 5 | 49a README | "I proved it myself and tested it by brute force"; "losing 2 points" quoted as the page's wording | The branch's test covers only (ii); (i) is proved but untested, because `glue()` deduplicates. The page never says "losing 2 points"; it says "each copy adds 8 points", "one period adds 17 points", "60 added per unit", and so on | minor |
| 6 | 1c README | "compared … with the recorded minimiser (equal)" | Printed but not enforced (mutation 1c-8) | minor |
| 7 | 1d README | "The 'Recent progress' section lists them" | It lists STEPS2026 and SCIEL2026 but not AER2026 | minor |
| 8 | `check_c16_lower.py` docstring | method B: "at most 4 correctly rounded operations … < 6u" | Stale. The code and README use 2–3 roundings, with bound (1+u)^{k+1}/(1−u)^k − 1 ≈ 7.8·10⁻¹⁶. The code is right | minor |
| 9 | 49a checkers | page cross-checks of trace/det and closed-form ρ | Printed but not enforced, so they cannot fail the run (mutation 49a-4) | minor |
| 10 | 49a README | IRSI data "git show v1.0:…" etc. | Pinned by tag; tags can move, and the page records no hash for v1.0. `audit/fetch_all.sh` pins commits `4d23c9a`, `f685bfa` and `e478c81` | informational |
| 11 | `VERIFY_LOG.md` | (omission) | It does not mention that upstream already has open replay PRs for the same rows: [#292](https://github.com/teorth/optimizationproblems/pull/292) (1c Kos2026) and [#235](https://github.com/teorth/optimizationproblems/pull/235) (49a rows 74–78) | informational |
| 12 | all | "Independence" sections | Accurate and candid: the replays, several certificates (Kos2026 1c, Cla2026, STEPS2026, Kos2026 49a) and this audit were all done by Claude agents. They are independent of each other's *code*, not of the AI tooling, and no human has checked anything | informational |

Side note, outside the log's stated scope: README.md marks 10c (3.65*) and 22a
(10.02*) with asterisks, but their pages do not.

---

## 6. How independent replays have been submitted upstream

Sources: the fork's git history, which is upstream's history; the PR bodies, via
GitHub search; and the PR threads. I read these only, and posted nothing.

### 6.1 The accepted format: [T2026] and the earlier replays

The pull requests: [#216](https://github.com/teorth/optimizationproblems/pull/216) (C3b, C3c, C71), [#230](https://github.com/teorth/optimizationproblems/pull/230) (C3c), [#232](https://github.com/teorth/optimizationproblems/pull/232) (C1a, C1b) and [#243](https://github.com/teorth/optimizationproblems/pull/243)
(C1c, C1d). All are by Carlos Toledo; all were merged; [#232](https://github.com/teorth/optimizationproblems/pull/232) and [#243](https://github.com/teorth/optimizationproblems/pull/243) were merged
with [#261](https://github.com/teorth/optimizationproblems/pull/261) on 25 October (US Pacific time; 26 October UTC).

**The pull request is Markdown only.** No code enters the repository. CONTRIBUTING
says so too: "Pull requests here should consist of Markdown changes only", and
code and data "must live somewhere else … and be linked from the constant page",
with "a hash or pinned commit".

The PR body has these parts:

- a table with columns *bound | bytes replayed (repo @ commit, file, SHA-256) | exact value*;
- **How**: the reduction in two sentences, and two implementations that share no
  code with each other or with the claimants' verifiers;
- **Red controls**: perturbations that must make the replay fail (a claim nudged
  past the exact value, a negative weight, and so on);
- **Re-derive**: the exact commands, with runtimes, against the replayer's own
  repository at a pinned commit (here `carlostoledo1891/cert-machine` @ `d9a3942`),
  plus a public write-up. [#216](https://github.com/teorth/optimizationproblems/pull/216) also cited a Zenodo DOI;
- **What changes**, and an AI-use disclosure.

The page edits are small:

- one sentence appended to each row's Comments ("Independently replayed [T2026]: …");
- a reference entry with the pinned-commit link;
- a Contribution note: "The [T2026] replay was prepared with AI assistance (Claude);
  its numbers are read from the record at the commit cited";
- the README cell, plus one "Recent progress" line.

At the time, these PRs also removed the asterisk.

### 6.2 The rule since 25–26 October: a second party

Commit `6552def`, by the maintainer, added to CONTRIBUTING: "Removing an asterisk
takes a second party … A replay carried out by the person requesting the removal
is not by itself sufficient … Post the replay, and let a second party confirm it."

On 26 October the maintainer posted the same note on [#232](https://github.com/teorth/optimizationproblems/pull/232), [#235](https://github.com/teorth/optimizationproblems/pull/235), [#242](https://github.com/teorth/optimizationproblems/pull/242), [#243](https://github.com/teorth/optimizationproblems/pull/243) and
[#249](https://github.com/teorth/optimizationproblems/pull/249): "The replay stands as posted; it just needs one of the four. The quickest
routes are a Palomar registration of the construction, or someone unconnected
confirming in this thread that they re-ran it and got the same enclosure … I am
leaving these open rather than closing them, so the confirmations can land on the
existing threads."

[#232](https://github.com/teorth/optimizationproblems/pull/232) and [#243](https://github.com/teorth/optimizationproblems/pull/243) nevertheless show as merged a few minutes later, as part of the
[#261](https://github.com/teorth/optimizationproblems/pull/261) merge. The page history shows one CERT2026 row before that merge commit
(`3cd3495`) and two from it onwards; this is the duplicate in §5, item 2.

Since then:

- [#292](https://github.com/teorth/optimizationproblems/pull/292) (rozetyp, 30 October; open, no comments) replays the Kos2026 certificates
  for 1c and 86a. It keeps the asterisks "pending a second party": one sentence per
  row, one reference per page, and an AI-use note.
- [#249](https://github.com/teorth/optimizationproblems/pull/249) (C31) shows what a second-party confirmation looks like. An unconnected
  contributor re-implemented the check, posted the matching state counts and
  bounds, then stated that they had no connection to the claimant and that their
  code was written without the claimant's code. They also disclosed using Claude
  Code. No maintainer response yet.
- [#278](https://github.com/teorth/optimizationproblems/pull/278), which added scripts to the repository, has had no maintainer response.

### 6.3 Recommended format for this work

1. **Do not submit the `verify/*` branches as they are.** They add Python code, run
   logs and `VERIFY_LOG.md` to the repository tree, which upstream does not accept.
2. **Host the code and logs in a separate public repository** at a pinned commit,
   ideally archived on Zenodo for a DOI. The checkers from the five branches,
   their logs and this `audit/` directory would all go there.
3. **Where a replay is already posted, be the second party.**
   - [#292](https://github.com/teorth/optimizationproblems/pull/292) covers 1c Kos2026.
   - [#235](https://github.com/teorth/optimizationproblems/pull/235) covers 49a rows 74–78.
   - On each thread, a short confirmation of the kind on [#249](https://github.com/teorth/optimizationproblems/pull/249) is what the
     maintainer asked for: no connection to the claimant or the replayer; the
     bytes re-run, by SHA-256; the exact values; the command lines and the pinned
     repository; and an AI-use disclosure.
   - This must come from the human owner, after they have reviewed it themselves.
     The CONTRIBUTING AI policy requires the human contributor to review and verify
     everything.
   - It only counts as a second party if the owner really is unconnected to the
     claimant and to the replayer. The maintainer has accepted AI-assisted
     confirmations when this is disclosed: the [#249](https://github.com/teorth/optimizationproblems/pull/249) confirmation says it was
     written with Claude Code.
   - [#235](https://github.com/teorth/optimizationproblems/pull/235) also asks for the asterisks to come off, in the pre-rule style; a
     confirmation there covers rows 74–78 only, not the Syl2026 rows 79–80.
4. **For the rows with no replay posted upstream, open a Markdown-only PR** in the
   [#292](https://github.com/teorth/optimizationproblems/pull/292) style: "independent replays … (asterisks kept pending a second party)".
   - Rows: 1d STEPS2026 and AER2026; 70a Pin2026; the 16a lower bound; 49a rows
     79–80.
   - Contents: one sentence per row, one reference per page, an AI-use note, the
     red controls, and the stated caveats (70a: depends on the criterion; 16a: the
     reading of the definition; 49a: the gluing lemma).
   - Do not touch the asterisks.
5. **Raise the 16a definition separately**, as a one-line Markdown fix or an issue.
   Cite [BDZ2013] Theorem 3.8, which states the inequality for all zero-mean u with
   L = max over δ ≥ 1. The same note could add that the paper's printed L ∼ 2.15627
   is about 4.5·10⁻⁵ above what its own formulas give (§3.4).
   On the 1d duplicate row, point to the existing [#243](https://github.com/teorth/optimizationproblems/pull/243) thread rather than editing
   the rows unilaterally.
6. **Mind the pending PRs.**
   - Several would add rows to these pages: 1d [#269](https://github.com/teorth/optimizationproblems/pull/269), [#271](https://github.com/teorth/optimizationproblems/pull/271), [#286](https://github.com/teorth/optimizationproblems/pull/286) and [#312](https://github.com/teorth/optimizationproblems/pull/312); 1c [#318](https://github.com/teorth/optimizationproblems/pull/318);
     16a [#319](https://github.com/teorth/optimizationproblems/pull/319) (2.156225528*, consistent with §3.4).
   - The tables are histories, so replays of the older rows remain useful. Keep any
     PR small, to avoid merge conflicts.

---

## 7. Plain-language summary

**What was checked.** Another AI agent re-computed 13 published bounds; 12 of them
are marked "unverified" with an asterisk. I tried to prove it wrong in four ways:

- I re-ran everything from scratch.
- I worked out the mathematics behind each check myself.
- I wrote my own versions with different methods.
- I deliberately broke the inputs to see whether the checks would notice.

**What is safe to say.** All 12 asterisked bounds it confirmed are correct as
numbers. Its programs give the same results every time; my separate programs agree
to the last digit; and its checks reject deliberately corrupted data or inflated
claims.

The 12 are:

- 1d: STEPS2026 and AER2026;
- 1c: Kos2026;
- 70a: Pin2026;
- 16a: the lower bound;
- 49a: rows 74–80.

**What needs a caveat.**

- **16a.** The page defines its constant in two slightly different ways. The
  bound is right under the definition used by the 2013 source paper, which is also
  the one the page's own numbers use. The page's first sentence adds a condition
  that is not in the paper. Read literally, that condition makes the bound wrong,
  so the sentence should be fixed. The paper's own printed value 2.15627 is
  slightly too high; recomputing it from the paper's formulas gives 2.1562255,
  which fits the page's bounds.
- **70a and 49a** each rely on a short mathematical argument. I wrote both proofs
  out and stress-tested them, but no human mathematician has checked them.
- **The original sources.** Nobody here has read the 1997 paper that the 49a page
  cites for the gluing step. For 16a, I read the arXiv version of the 2013 paper,
  supplied by you, but not the journal version.

**What is not safe to say.**

- That 15 bounds were confirmed (it is 12, plus one already replayed).
- That any asterisk can now be removed. The repository's rule requires someone
  unconnected to confirm, and a replay by the person asking does not count.
- That SCIEL2026 (1d), the 16a upper bound, or 49a row 81 were checked.
- That a human has reviewed any of this, including this audit.

**How to submit.** Put the code in a separate public repository, pinned to a
commit. Send upstream only Markdown changes:

- For 1c and 49a rows 74–78, someone has already posted a replay upstream (PRs
  [#292](https://github.com/teorth/optimizationproblems/pull/292) and [#235](https://github.com/teorth/optimizationproblems/pull/235)). There, add a short "I re-ran it independently and got the same
  numbers" comment, after reviewing the work yourself.
- For the other rows, open one small pull request that records the replays and
  leaves the asterisks for a second person to remove.

---

## Appendix: the `audit/` directory

| File | Purpose |
| --- | --- |
| `fetch_all.sh ROOT` | Clones the five branches and fetches all certificate data, pinned by commit, into ROOT. Checks 12 SHA-256 values |
| `run_all.sh ROOT [OUT]` | Re-runs every documented command of the five branches, then all the checks below. About 14 minutes on 4 cores |
| `c1_independent.py` | C_1d and C_1c recomputed by Kronecker substitution, with a text parser for the AER `.py` file |
| `c70_independent.py` | Steiner and parallelotope formula tests (Monte Carlo); the exact Szász/AM–GM test; a standard-library `decimal`+Robbins enclosure of R; the side statements on the page |
| `c16_readings.py` | Both readings of the 16a definition: the exact extremal family, the Kronecker constant, F(δ) → (β+π)/π, the untruncated maximum, and an independent value of the trial function. Also the comparison with [BDZ2013]: its Bessel-series formulas, the maximum L, and its Θ table |
| `c49_independent.py` | The gluing lemma tested exhaustively (≤ 4 points) and by classes (≤ 5 points); necessity demonstrations; explicit chains; F and H rebuilt; kernel-bucket and zeta checks of B′ and IRSI; exact bound decisions |
| `mutation_tests.py` | The 38 mutation tests of §4 |
| `logs/` | The outputs of the runs cited in this document, and the environment they ran in |

Requirements: Python 3.13, numpy, python-flint and mpmath, installed where
`python3 -I` can import them; see §2. Network access is needed only for
`fetch_all.sh`.
