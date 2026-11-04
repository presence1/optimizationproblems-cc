# Independent check of the asterisked upper bounds on C_1d

Constant: [C_1d, the signed third autocorrelation constant](../../constants/1d.md),
the largest C with max_t |(f∗f)(t)| ≥ C (∫f)² for every real f supported on
[−1/4, 1/4]. Any such f with ∫f ≠ 0 gives the upper bound C_1d ≤ R(f), where
R(f) = max_t |(f∗f)(t)| / (∫f)².

## Verdict

| Row of `constants/1d.md` | Claimed | Artifact | Result |
| --- | --- | --- | --- |
| line 20, [STEPS2026] | C_1d ≤ 1.460217284022874* | 600-cell step function, `construction.json` @ `9a09149` | **Confirmed.** R(f) is exactly the fraction recorded on the page, 1.46021728402287398524…, which is below the printed bound by 1.5·10⁻¹⁷ |
| line 21, [AER2026] | C_1d ≤ 1.459989046905384* | 600-cell step function `STEP_FUNCTION_C4_PRIME_N600` @ `4b3bbd2` | **Confirmed.** R(f) = 1.45998904690538314495… when the printed decimals are read exactly, and 1.45998904690538324315… when they are read as binary64. Both are below the printed bound |
| line 22, [SCIEL2026] | C_1d ≤ 1.457854884921989* | 800-cell step function on Zenodo | **Not checked.** The page says the Zenodo record is restricted (files on request), and zenodo.org is blocked from this session anyway. I had no access to the data |
| line 19, [CERT2026] (duplicate of line 23) | C_1d ≤ 1.463071582607559* | 300-cell step function, registry copy @ `50520b9` | **The printed value does not follow from the certificate, by 3.3·10⁻¹⁶.** R(f) = 1.46307158260755932746… is slightly *above* 1.463071582607559. This isn't a new finding: line 23 of the same page already says this, after the [T2026] replay, and reprints the bound as 1.4630715826075594, which I confirm. **Which of lines 19 and 23 should stay is an open maintainer question, not a settled leftover.** Upstream, the replay pull requests [#232](https://github.com/teorth/optimizationproblems/pull/232) and [#243](https://github.com/teorth/optimizationproblems/pull/243) were merged minutes after the maintainer posted a hold on asterisk removals; the replayer then asked on [#243](https://github.com/teorth/optimizationproblems/pull/243) which row should go, and no answer was visible when the audit was written (AUDIT.md §6.2). This replay settles only the arithmetic |

What "confirmed" means: the published data defines a real step function f on
[−1/4, 1/4], and I recomputed max_t |f∗f| / (∫f)² exactly, with no rounding, and
found it at or below the bound in the table. That proves the inequality
C_1d ≤ (printed value) for the bound as stated. I am not making any claim about
how the functions were found, or about whether they are near-optimal.

## Why a finite computation is enough (the knot formula)

Say f has N equal cells: f = Σ_{i=0}^{N−1} v_i 1_{[a+ih, a+(i+1)h)}, with
a = −1/4 and h = 1/(2N). Let Λ = 1_{[0,h)} ∗ 1_{[0,h)}. Then
Λ(u) = max(0, h − |u − h|), a tent of height h supported on [0, 2h] and linear
on [0,h] and on [h,2h]. Bilinearity of convolution gives

  (f∗f)(t) = Σ_{i,j} v_i v_j Λ(t − 2a − (i+j)h) = Σ_s c_s Λ(t + 1/2 − sh),  with c_s = Σ_{i+j=s} v_i v_j.

Every term is linear on each interval [−1/2 + mh, −1/2 + (m+1)h], so f∗f is
continuous and piecewise linear with knots t_m = −1/2 + mh, m = 0, …, 2N.
It vanishes outside [−1/2, 1/2]. At a knot, Λ((m−s)h) equals h when s = m−1 and
0 otherwise, so (f∗f)(t_m) = h c_{m−1}. A linear function's absolute value on a
closed interval is largest at an endpoint, so max_t |f∗f| = h max_s |c_s|.
Together with ∫f = h Σ v_i this gives

  R(f) = 2N · max_s |c_s| / (Σ_i v_i)².

This is exact and needs only integer arithmetic once the v_i are put over a
common denominator. The same formula appears on the constant page and in the
STEPS2026 README. I derived it again here and did not take it from either.

## What the checker does

`check_c1d.py` runs on the standard library plus python-flint, which is
required for check B. If python-flint cannot be imported, the checker stops
with exit status 2 and says why; it never skips check B. (Until
`replay/package` it skipped check B silently in that case, still printing
"integrity: OK". Under `python3 -I` that happens whenever python-flint was
installed with `pip --user`, because `-I` ignores the user site directory.)

1. It checks each input file's SHA-256 against the value recorded on the
   constant page (all three match), then parses the file **as data only**:
   `json` for the two JSON files, and Python's `ast` parser for the AER2026
   `.py` file, which is never imported or executed. Each number's literal text
   is kept.
2. Each literal is turned into an exact rational in two ways: the decimal
   string itself, exactly ("decimal"), and the IEEE binary64 value nearest it,
   exactly ("binary64"; `Fraction(float(s))`). The STEPS2026 and CERT2026
   certificates say the binary64 reading is the intended one. For AER2026 the
   page says either works. Both readings are reported for every certificate.
3. The c_s are computed by:
   - **A**, a direct O(N²) loop over Python integers;
   - **B**, squaring the integer polynomial Σ a_i xⁱ with FLINT's `fmpz_poly`,
     which uses a different multiplication algorithm.
   A and B must agree exactly.
4. **C** is a structurally different check of the knot formula itself. It
   computes (f∗f)(t) = ∫ f(x) f(t−x) dx by brute-force exact integration over
   the breakpoints of x ↦ f(x) f(t−x), with no tent formula. It does this at
   **every** knot, where it must equal h c_{m−1}, at 200 random rational points
   strictly between knots, where it must equal the linear interpolation of the
   two neighbouring knot values, and at two points outside [−1/2, 1/2], where it
   must be 0. All checks agree exactly.
5. R(f) is formed as an exact fraction, compared with the fraction recorded on
   the page where there is one, and compared exactly with the printed decimal
   bound.
6. `--selftest` checks hand-computed cases. For example f ≡ 1 gives R = 2,
   (v) = (2, 1) gives 16/9, and (v) = (1, −1/2) gives 16. It also checks
   formula against brute force on 40 random small step functions, including
   that no point on a fine rational grid beats the knot maximum.

## Reproduce

```bash
sh verification/1d/fetch.sh /some/empty/dir
```

```bash
python3 -I verification/1d/check_c1d.py --selftest
```

```bash
python3 -I verification/1d/check_c1d.py --data /some/empty/dir
```

The first line of the output must read `python-flint 0.9.0` (or another
installed version). The output of the re-run on branch `replay/package` is in
[`run_output.txt`](run_output.txt); the original run of 3 November 2026 is in
the git history of this file, with the same numbers. The full run takes about
20 s on one core of an Intel Xeon @ 2.30 GHz (Python 3.13.18,
python-flint 0.9.0). Check C accounts for almost all of that. The exact ratio
itself takes well under a second.

## Assumptions

- The definition of C_1d is the one on the constant page at fork commit
  `87b4ebb`. The bounds and fractions I compare against were copied from that
  page.
- Python's `float()` is correctly rounded (IEEE 754 round-to-nearest), and
  `fractions.Fraction` and Python integers are exact. These matter only for the
  binary64 reading. The decimal reading uses no floating point at all.
- The data files at the pinned commits are the certificates the rows refer to.
  The SHA-256 values match the ones recorded on the page.
- No floating point is used in any comparison that decides a result. The
  "margin" figures in the output are exact differences converted to floats
  for display only.

## Independence

I wrote the checker from the definition on the constant page. I did not open
or run the certificate authors' code (`verify.py`, `numeric_check.py` and
`optimize.py` in steps-re/c1d-certificate, or the `evaluate_SignedLInf`
function in the AER2026 file). I read only the STEPS2026 README, to learn the
data format. The checker was written by an AI agent (Claude), working for the
owner of this fork. I have no connection to the certificate authors. One
caveat applies under this repository's rules: STEPS2026's own checker was also
written by a Claude agent, so this is not independent of the AI tooling in
that sense. Whether this counts as the "second party" needed to remove an
asterisk is for a maintainer to decide.

## Side observations, not acted on

- `constants/1d.md` carries line 19 (asterisked 1.463071582607559*) and line 23
  (1.4630715826075594, replayed) for the same CERT2026 certificate. Which one
  stays is an open maintainer question on upstream
  [#243](https://github.com/teorth/optimizationproblems/pull/243) (see the
  verdict table), and this replay does not decide it. The page's "Additional
  comments" section is also duplicated, and the second copy has `vert` typos
  where `\rvert` was meant. Following the instructions for this task, I did
  not edit the page.
- The README table still shows 1.4630715826075594 as the best upper bound,
  without the asterisked improvements. The "Recent progress" section lists two
  of them, STEPS2026 and SCIEL2026, but not AER2026.

## Corrections made on branch `replay/package` (4 November 2026)

- `check_c1d.py` now requires python-flint and stops with exit status 2 without
  it, instead of skipping check B silently (AUDIT.md §2). Mutation tests 1d-7
  and 1d-8 in `audit/mutation_tests.py` check this.
- The duplicate CERT2026 row is described as an open maintainer question on
  upstream #243, not as a settled merge leftover (AUDIT.md §5, item 2).
- "The 'Recent progress' section lists them" was inaccurate: it lists
  STEPS2026 and SCIEL2026 but not AER2026 (AUDIT.md §5, item 7).
