# Verification log: unverified (asterisked) bounds

> Corrected on branch `replay/package` (4 November 2026). The statements
> flagged in AUDIT.md §5 have been fixed; the list of corrections is at the
> end. On `replay/package` the five `verification/<id>/` folders are
> combined, together with the audit (`AUDIT.md`, `audit/`) and the checker
> fixes it called for. All of this work, including the original replays, the
> audit and the fixes, was done by Claude agents (Anthropic). No human
> mathematician has reviewed any of it.

Survey of `constants/*.md` at fork commit `87b4ebb` (2026-11-03). This
repository marks a bound "unverified" with an asterisk (`*`) in its row; see
CONTRIBUTING.md, "Recording bounds". There are 66 asterisked rows across
30 constant pages, plus a few rows that say "Unverified" in words without
the marker. Each row is listed below with its artifact and with my estimate
of how hard an independent, rigorous re-check would be in Python with exact
or interval arithmetic.

"Reachable" means the artifact could be fetched from this session. GitHub
repositories were reachable. zenodo.org was blocked by this session's network
policy.

Tractability:
- **A**: a finite exact computation from published data, with an elementary
  reduction I can prove in a few lines.
- **B**: finite, but the reduction rests on a paper's lemma or framework that
  would have to be read and trusted or re-derived. Or the computation is large
  but still feasible.
- **C**: very large computations, deep analytic inputs, a Lean build, or no
  finite certificate at all.

Each checked constant had its own branch, `verify/<id>`, containing
`verification/<id>/` (checker, README with findings, run log) and this file.
Branch `replay/package` combines them.

## Results

| Constant | Row(s) | Outcome | Branch / folder |
| --- | --- | --- | --- |
| 1d | STEPS2026 ≤ 1.460217284022874*, AER2026 ≤ 1.459989046905384*, CERT2026 ≤ 1.4630715826075594 | **Confirmed**, all three, in exact rational arithmetic. Each exact value is at or below the printed bound | `verify/1d`, `verification/1d/` |
| 1d | CERT2026 duplicate row ≤ 1.463071582607559* | **Printed value not implied.** It is 3.3·10⁻¹⁶ *below* the certificate's exact value. The page's own replayed row (…594) already says so. Which of the two rows should stay is an **open maintainer question** on upstream [#243](https://github.com/teorth/optimizationproblems/pull/243), not a settled leftover (see the 1d README) | same |
| 1d | SCIEL2026 ≤ 1.457854884921989* | **Not checked**: the data is in a restricted Zenodo record | same |
| 1c | Kos2026 ≥ 0.4103333* | **Confirmed**, exact: 0.41033335274849…, equal to the page's fraction, with the minimiser at k = 21264 | `verify/1c`, `verification/1c/` |
| 70a | Pin2026 ≥ 1.20194336* | **Confirmed, given Patankar's criterion** (re-derived in the README; it rests on Steiner's formula and the zonotope intrinsic-volume formula). Two independent rigorous enclosures give 1.2019433684431505669948… | `verify/70a`, `verification/70a/` |
| 16a | lower bound ≥ 2.1562247706* | **Confirmed for the constant as defined by the page's "Equivalently" sentence and by the source, [BDZ2013] Theorem 3.8.** Two independent rigorous lattice-sum enclosures give 2.15622477064423579…. **Under the literal reading of the page's first sentence ("sufficiently large frequency ratio") the best constant would be (β+π)/π ≈ 1.82283 and this bound would be false** (see the 16a README) | `verify/16a`, `verification/16a/` |
| 16a | upper bound ≤ 2.1562256466* | **Not checked**: needs an infinite lattice-sum tail bound and a branch-and-bound over δ | same |
| 49a | rows 74–80: 1.5617847*, 1.5621220*, 1.5647730*, 1.5664286*, 1.5666969*, 1.5675517*, 1.5678015* | **Confirmed, given the XOR-gluing lemma**, proved in the README (the audit checked the proof; no human has) and tested by brute force (both parts of the lemma since `replay/package`). The base families of rows 74–78 and 80 were checked exhaustively; row 79's 62-point unit (about 1.1·10¹² sets) was not, and its goodness rests on the lemma alone. F and H were rebuilt from the page text | `verify/49a`, `verification/49a/` |
| 49a | row 81: Kos2026 1.5678599* | **Not checked**: the 252292-set family is too large for an exhaustive Python search here | same |

**Count.** 13 rows are confirmed. 12 of them are asterisked bounds: 1d
STEPS2026 and AER2026; 1c Kos2026; 70a Pin2026; the 16a lower bound; 49a rows
74–80. The 13th, the 1d CERT2026 row at 1.4630715826075594, carries no
asterisk and had already been replayed by [T2026]. No other count of
confirmed bounds is supported by this work.

No claimed bound was refuted. Two problems with the pages were found:

1. **1d**: the duplicate starred CERT2026 row prints a value that the
   certificate does not imply. The page already documents this. Which of the
   two rows should stay is an open maintainer question on upstream #243.
2. **16a**: the page's first sentence and its "Equivalently" sentence define
   different constants. Under the literal first sentence the best constant
   would be (β+π)/π ≈ 1.82283, and the asterisked lower bound 2.1562247706*
   would be false. Under the "Equivalently" sentence, which matches the
   source's definition ([BDZ2013], Theorem 3.8), the bound holds.

**Related upstream work.** Upstream already has open replay pull requests for
some of these rows: [#292](https://github.com/teorth/optimizationproblems/pull/292)
(1c Kos2026) and [#235](https://github.com/teorth/optimizationproblems/pull/235)
(49a rows 74–78). The original version of this log did not mention them.

## Candidates

| Const. | Asterisked bound(s) | Source | Artifact (location) | Reachable | Tract. | Status / notes |
| --- | --- | --- | --- | --- | --- | --- |
| 1a | ≥ 1.292* | PBV2026 | code/certificate, GitHub AndreiPiterbarg/sidon-autocorrelation | yes | C | A lower bound for a sup-of-autoconvolution constant must cover all f, so no single test function suffices. Not attempted |
| 1c | ≥ 0.4103333* | Kos2026 | step function, K = 24576, GitHub DennisKoshta/c1c-autocorrelation-certificate @ `a4ee94e` | yes | **A** | **Confirmed** |
| 1d | ≤ 1.463071582607559*, 1.460217284022874*, 1.459989046905384*, 1.457854884921989* | CERT2026, STEPS2026, AER2026, SCIEL2026 | step functions, 300/600/600/800 cells | 3 of 4 | **A** | See Results |
| 3a | ≥ 1.173077*, 1.187326…*, 1.19102809*, 1.19519192*, 1.19230254*, 1.19281555*, 1.19359680* | Z2025, Num2026, K2026, K2026b, M2026, Syl2026 | masked-digit limit constructions with directed-rounding certificates. GitHub (K2026, M2026, Syl2026), Zenodo (Num2026) | mostly | B | Needs the GHR framework and the K2026b Prop. 3 reduction. Not attempted |
| 5a | ≤ 0.98173*, 0.94325*, 0.9428095* | St26, Mad26, Akw26 | exact-rational covering inequalities in the HZ26 framework | partly | B | The page names HZ26 Lemma 2.1 as the load-bearing unreviewed input. Not attempted |
| 10a | ≤ 1.7813* | P2026 | Arb certificates (arXiv 2609.20074) | not tried | B/C | Not attempted |
| 12a | ≤ 0.8618* | O2026 | integer computation, GitHub devinokeefe/travelling-sales-person-constant-bounds | yes | B | The probabilistic reduction is intricate. Not attempted |
| 13a | ≥ 0.239* | K2026 | arcs + subdivision certificate (arXiv) | not tried | C | Not attempted |
| 16a | ≤ 2.1562256466*, ≥ 2.1562247706* | maximusrufus | lattice sums, GitHub maximusrufus/c16-bgw-certificates | yes | A (lower) / B (upper) | Lower bound **confirmed** under the "Equivalently" definition (false under the literal first sentence; see Results). Upper bound not checked |
| 19a | ≤ 0.4395*, 0.423* | XL2026, Lin2026 | Lean 4 + `native_decide` | yes | C | a Lean build, not a Python replay |
| 21a | ≤ 0.1965*, 0.1875*, 0.172422*, 0.16*, 0.1595* | MI2026a–d, Kor2026 | certified H_t numerics (Zenodo, GitHub) | partly | C | Not attempted |
| 22b | ≤ 7.2012719* | Claude2026 | interval-arithmetic thickness proof, GitHub YouhuaLi/tight-alternating-knot-constant | yes | B/C | Not attempted |
| 24a | ≤ 7.5199*, 6.9013* | GFL2026a, AS2026 | analytic proofs | yes | C | proof-based |
| 28a | ≤ 9* | OAI2026 | paper + Lean | yes | C | proof-based |
| 31a | ≤ 0.825101*, 0.824120* | J2026 | Lueker automaton, 5·10⁷ / 4·10⁸ states | yes | C | too large for Python here |
| 31a | ≥ 0.79970 ("unverified", no `*` on the page) | AA2026 | Monte Carlo + Hoeffding | — | — | probabilistic by its own description |
| 41a | ≤ 2.2195* | Baek2024 | analytic proof | — | — | no finite certificate |
| 42a | ≤ 0.6906538*, 0.6888863712*, 0.6873358063* | Gri26, Pin26, Kos2026 | rational profiles + interval/Arb limit checks, GitHub ×3 | yes | B | The asymptotic reduction is unrefereed. Not attempted |
| 43a | ≥ 0.860* | S2026 | 3.3·10⁸ region certificates | partly | C | conditional on the KHSHGW2026 lemma layer |
| 44a | ≤ 4.3654674227*, 4.3576549226* | Epi2026, P2026 | exact rational certificates in Wellens's recurrence, GitHub ×2 | yes | B | Not attempted |
| 49a | ≥ 1.5617847* … 1.5678599* (8 rows) | IRSI2026, Cla2026, Syl2026, Kos2026 | set families + transfer matrices, GitHub ×4 | yes | B | Seven rows **confirmed** (see Results); Kos2026 not checked |
| 57c | ≤ 0.656319277272*, 0.65628589* | OCP2010, vS2026 | numerical / Arb conformal radius | yes | C | Not attempted |
| 65a | ≤ 2.4*, 3.99* | OAI2026+IK2004, Nas2026 | deduction; LP certificates on 4.2·10⁶ boxes | yes | C | Not attempted |
| 68a | ≥ 0.432* | Pin2026 | explicit measure, GitHub rpinho/korenblum-c68-certificate | yes | B | The finite checks only verify the hypotheses of a new analytic argument that the page says still needs mathematical review. Assessed, not attempted |
| 70a | ≥ 1.20194336* | Pin2026 | single Steiner term at n = 10¹², GitHub rpinho/c70-certificate @ `680e074` | yes | A | **Confirmed** (given the criterion) |
| 82a | ≤ 0.2535744749068227*, 0.2534449* | Epi26, Pin26 | Doche limit-point construction, Arb checkers | yes | B/C | Not attempted |
| 84a | ≥ 1.0427*, 1.04317* | Nas2026(b) | Lean (Palomar) + interval L-function certificates | yes | C | Not attempted |
| 84b | ≤ 1.9993* | Al26 | explicit-constant calculation in a note | yes | B | proof-based; the page credits [T2026] with checking the arithmetic |
| 86a | ≤ 1.8117251*, 1.8084990* | Pin26, Kos2026 | step-density measure + auxiliary polynomials, GitHub ×2 | yes | B | Assessed: needs rigorous log-potential bisection and the exact hypotheses of [Smi24] Prop. 5.15. A good next candidate. Not attempted |
| 89a | ≤ 0.0301388876*, 0.0301388794*, 0.0301388857* | VSJ2026, SK2026, Kos2026 | step graphons, 3840 / 7680 classes | yes | B/C | A naive K4 count is about 10¹⁴–10¹⁵ terms. Not attempted |
| 90a | ≥ 44* | M2026 | Lean (about 8000 files) + SAT | yes | C | Not attempted |

## How the work was prioritised

1. **1d and 1c**: tractability A. Exact rational autoconvolution and
   autocorrelation of published step functions. Each was computed by two
   different algorithms, and the piecewise-linear reduction was checked by
   brute-force integration at every knot.
2. **70a**: a closed-form expression at n = 10¹², enclosed by Arb and,
   separately, by mpmath intervals with Robbins bounds.
3. **16a (lower bound)**: an explicit trial function. Three lattice sums over
   5·10⁷ points were enclosed by Arb and, separately, by float64 with a
   proven error bound and `fsum`.
4. **49a**: after proving the gluing lemma, which no source in hand stated.
   For rows 74–78 and 80 the base families (IRSI v1.0–v1.2, F, H, B′) were
   checked exhaustively; the chains then follow from the lemma. Row 79's
   62-point unit (about 1.1·10¹² sets) is far too large to enumerate: only
   its port counts were computed, and its goodness rests on the lemma alone.

Not attempted, for lack of time: 86a (probably the next most tractable), the
16a upper bound, 49a row 81, and everything rated B/C or C above.

## Corrections made on branch `replay/package` (4 November 2026)

Following AUDIT.md §5:

- **Count** (item 3): the confirmed count is stated explicitly, 12 asterisked
  bounds plus one non-asterisked row that [T2026] had already replayed.
- **1d duplicate row** (item 2): no longer called "a leftover from a merge";
  which row stays is an open maintainer question on upstream #243.
- **16a** (item 1): the summary no longer says the only discrepancy is the 1d
  row. It now records the 16a definitional problem and says plainly that the
  bound would be false under the literal reading of the page's first
  sentence.
- **49a** (item 4): "the seven smaller certificates were all finite exhaustive
  checks" was inaccurate; row 79 rests on the lemma alone.
- **Upstream work** (item 11): the open replay pull requests #292 and #235 are
  now mentioned.

The checkers were also fixed (AUDIT.md §4): `check_c1d.py` and `check_c1c.py`
now stop instead of skipping their FLINT check when python-flint is missing;
`check_c1c.py` enforces the recorded minimiser; the three 49a checkers enforce
every comparison with the page. Re-run logs are in `audit/logs/package/`.
