# Submission notes for the replay of 12 asterisked bounds

These notes are for the owner of this fork, who will decide what to submit
upstream and submit it personally. They are checklists of facts, not text to
paste. Nothing has been posted to `teorth/optimizationproblems`. Statements
below about upstream pull requests and threads come from `AUDIT.md` §6; they
were not re-checked, because this work did not touch upstream at all.

## What is where

- **Branch `replay/package`** (this branch). The five `verification/<id>/`
  folders (checkers, READMEs, run logs), `VERIFY_LOG.md`, the audit
  (`AUDIT.md`, `audit/`), the checker fixes the audit called for, and re-run
  logs in `audit/logs/package/`.
  - **Pinned commit: `c16fe56894c5c725faa9acb7c2743db31d25c304`.** The
    upstream notes link to it. Later commits on this branch (this file) do
    not change any checker, README or log.
  - The upstream links only work if this fork is public and that commit stays
    reachable. Do not delete or force-push `replay/package`. `AUDIT.md` §6.3
    suggests a separate public repository, ideally archived on Zenodo, as
    the long-term home. If you move the code, re-pin the links in the
    upstream notes.
- **Branch `replay/upstream-notes`** (commit `d79b144`), made from `main`.
  It contains only Markdown edits to `constants/1d.md`, `constants/16a.md`,
  `constants/49a.md` and `constants/70a.md`, and is what a pull request
  would contain.
  - Six rows are covered, one sentence each: 1d STEPS2026 and AER2026, 70a
    Pin2026, the 16a lower bound, and 49a rows 79 and 80.
  - Each page also gets one reference entry, `[RPL2026]`, and one AI-use
    note. All asterisks are left in place.
  - Placeholders to adjust before submitting: the author line
    "presence1 (GitHub)" and the key `[RPL2026]`, which appears in 6 row
    sentences, 4 reference entries and 4 notes.
- **Not prepared here:** second-party confirmations on #292 (1c) and #235
  (49a rows 74–78), which `AUDIT.md` §6.3 item 3 suggests. That is a
  separate decision. It needs your own review and a truthful statement that
  you are unconnected to the claimant and to the replayer.

## Checklist: what the pull-request description must state

**Scope**

- [ ] The pull request is Markdown only: `constants/{1d,16a,49a,70a}.md`. No
      code, logs or README.md changes.
- [ ] It records independent replays of six asterisked rows. **The asterisks
      are kept, pending a second party** (CONTRIBUTING, commit `6552def`).
- [ ] Rows deliberately not covered, and why:
  - [ ] 1c Kos2026 is already replayed in open upstream #292.
  - [ ] 49a rows 74–78 are already replayed in open upstream #235.
  - [ ] Neither 1d CERT2026 row is touched. The unstarred one was already
        replayed by [T2026]; which of the duplicate rows stays is an open
        question on #243.
  - [ ] Not checked at all: 1d SCIEL2026 (restricted Zenodo record), the 16a
        upper bound, 49a row 81 (Kos2026).

**Per row: bytes replayed (repository @ commit, file, SHA-256) and the value obtained**

- [ ] 1d STEPS2026, ≤ 1.460217284022874*
  - Bytes: `steps-re/c1d-certificate` @ `9a091494facc801eaf6b92b175b63c58b7c3b30b`,
    `construction.json`, `3dd39fae744555179b0356b84e752db724e892bd23dda51403976edfb5b3a28c`.
  - Exact R. Binary64 reading: `698746209786798359455483373677229695641600/478522078482569620433992386249161163190849`
    = 1.46021728402287398524…, equal to the page's fraction. Decimal reading:
    1.46021728402287397507….
- [ ] 1d AER2026, ≤ 1.459989046905384*
  - Bytes: `unclegareth-create/alphaevolve_repository_of_problems` @ `4b3bbd2a44db92442e4ebb4e64e0bb90f229aad1`,
    `experiments/autocorrelation_problems/problem_4_signed_autoconvolution_bounds.py`,
    `1a290ad1074c10a871adaf2bd44402af56be8cf151f1f775a8fc37c7bdff54b2`.
    The file is parsed as text and never executed.
  - Exact R. Decimal reading: `20684250041098457118804665472/14167400834233061222366701921`
    = 1.45998904690538314495…. Binary64 reading: 1.45998904690538324315….
- [ ] 70a Pin2026, ≥ 1.20194336*
  - Bytes: `rpinho/c70-certificate` @ `680e074bb50929734bfd76484d716cd3e85827f0`,
    `certificates/c70_candidate.json`,
    `03ff0d6df3dfa6ea06f901a9319c968eb7c013f5d0cc3f1f00cfa58e9490c0cc`.
    Only its parameters n, k, side and claim are read.
  - Arb (literal criterion): [1.2019433684431505669948027797355241 ± 3.8·10⁻³⁵].
  - mpmath intervals (closed form, Robbins' bounds):
    [1.201943368443150566994802779735524137829, …524138179].
  - Margin 8.4·10⁻⁹.
- [ ] 16a lower bound, ≥ 2.1562247706*
  - Bytes: `maximusrufus/c16-bgw-certificates` @ `0c570700f080ca23549e10380901addfc8b7b8ae`,
    `lower_certificate.json`, `de314c10bd4a63d35604d28c0d0556b8b5ae67ab1840c06628039d8fd64b6991`.
    The page pins no commit; this is the repository HEAD when the replay was
    made. Only R and μ are read from it.
  - Arb: L ≥ [2.1562247706442357903 ± 4.3·10⁻²⁰]. binary64 + `fsum` with a
    proven error bound: [2.1562247706442 ± 4.6·10⁻¹⁴]. Margin 4.4·10⁻¹¹.
- [ ] 49a row 79, ≥ 1.5675517*
  - No data file is used: F and H are rebuilt from the page text.
  - Gadget 250659 = 98308 + 152351. Unit port counts N00 = 148811965456,
    N01 = N10 = 279351870092, N11 = 378843386627.
  - ρ^{1/60} = 1.5675517557581882198….
- [ ] 49a row 80, ≥ 1.5678015*
  - Bytes: `xSyllaa/sunflower-pendant-chain` @ `8e21d0287711b4f0bfc23e9443523e2aa472cca1`:
    `data/B.txt` (`340cef5e71124ed624425abf81e9621839406cbf44b3fd242594d8edcb7d37af`)
    and `data/Bprime.txt` (`2a72385704b8203269cda4f4b0dfdabc74d5adb8f4a2bc1dac1f570cb96b5cec`).
  - B rebuilt from F and H equals `B.txt`. B′ is 4364 sets, Sperner, with no
    3-sunflower in any of the 9,520,066 pairs searched.
  - ρ^{1/17} = 1.5678015201687483405….

**How, and the caveats each result depends on**

- [ ] 1d. R(f) = 2N·max|c_s|/(Σv)² by the knot formula. The c_s are
      computed by a direct integer loop and by FLINT squaring. The knot
      formula itself is checked by exact brute-force integration at every
      knot and at 200 interior points. Both readings of the data are
      evaluated.
- [ ] 70a. **Conditional on Patankar's cube–ball criterion**, which rests on
      Steiner's formula and the parallelotope intrinsic-volume formula. The
      replay and the audit re-derived it; no human has reviewed it. Only the
      finite certificate is checked, not the limit exp(1/(2e)).
- [ ] 16a. **The result depends on which reading of the definition is
      intended.** It holds under the "Equivalently" formula (the maximum over
      δ ≥ 1, as in [BDZ2013] Theorem 3.8). It would be false under a literal
      reading of the first sentence. Refer to the separate issue about the
      definition (checklist below).
- [ ] 49a. **Conditional on the XOR-gluing lemma.** The proof is written out
      in `verification/49a/README.md` and was checked by the audit, but by no
      human. Nobody here has compared it with [DEGKM1997]. Row 79's 62-point
      unit (about 1.1·10¹² sets) is not enumerated, so its goodness rests on
      the lemma alone.

**Red controls**

- [ ] `audit/mutation_tests.py` at the pinned commit has **52**
      perturbations, and with the fixed checkers **all 52** behave as a
      correct checker must (`audit/logs/package/mutation_tests.txt`).
      Examples: claims nudged past the exact value, data changed with the
      hash pin intact and with it updated, a negative weight, a recorded
      page value changed, wrong transfer-matrix conventions, python-flint
      made unavailable.
- [ ] Against the original (pre-audit) checkers, the same suite gives
      **39 of 52**. The 13 failures are exactly the tests of the fixes:
      1d-7, 1d-8, 1c-8 to 1c-10, 49a-4, 49a-16 to 49a-22. This shows the
      audit's fixes were needed; state that they were made after the audit
      (see below).

**Re-derive**

- [ ] Repository and commit: `presence1/optimizationproblems-cc` @
      `c16fe56894c5c725faa9acb7c2743db31d25c304`.
- [ ] Commands, in a full (not shallow) clone at that commit:
      `sh audit/fetch_all.sh ROOT`, then `sh audit/run_all.sh ROOT`, about 21
      minutes in total on 4 cores. `fetch_all.sh` needs network access for
      the certificate data, and the clone's history for the original
      checkers. The per-checker commands are in each
      `verification/<id>/README.md`.
- [ ] Requirements: Python 3.13, numpy 2.5.3, python-flint 0.9.0 and mpmath
      1.4.1, installed where `python3 -I` can import them.

**Audit and fixes**

- [ ] A second, separate Claude session audited the replay (`AUDIT.md`). It
      found no wrong bound. It found checks that were printed but not
      enforced, overstated wording, and the 16a definitional problem.
- [ ] The fixes, made after the audit:
  - 1d and 1c stop instead of silently skipping their FLINT check.
  - 1c enforces the recorded minimiser.
  - The three 49a checkers enforce every comparison with the page.
  - The READMEs and `VERIFY_LOG.md` were corrected.

**AI use and independence (must be filled in truthfully by you)**

- [ ] The replay was done by Claude Opus 5.5 agents and audited by a second
      Claude session. A further Claude session revised it after the audit.
      **No human mathematician has reviewed it.**
- [ ] What you yourself reviewed or re-ran. CONTRIBUTING's "AI use policy"
      requires that AI use be noted in the submission text, and that "all
      references and other information provided by the AI are reviewed and
      verified by the human contributor". List only what you actually did.
- [ ] Your relationship, if any, to the claimants: steps-re, the AER2026
      contributor, R. Pinho, maximusrufus, Sylla.
- [ ] The replay is independent of the claimants' code: their verifiers were
      not opened or run. It is **not** independent of the AI tooling:
      STEPS2026's own checker was also written by a Claude agent, and the
      Syl2026 families are built from the [Cla2026] families, which were
      found with Claude.
- [ ] It has not been compared with the code of #292 or #235.

**Coordination**

- [ ] Pending upstream pull requests add rows to the same pages: 1d #269,
      #271, #286, #312; 16a #319. Expect possible merge conflicts. The edits
      only append to existing rows and add one reference and one note per
      page.

## Checklist: issue asking which reading of the 16a definition is intended

**The two sentences** (`constants/16a.md` at `87b4ebb`)

- [ ] Quote line 12: the inequality "holds for all zero-mean functions
      u ∈ H²(𝕋²) **with sufficiently large frequency ratio** δ(u)".
- [ ] Quote lines 18–22: "Equivalently, L = max_{δ≥1} [4πΘ(δ) − ln δ − ln(1+ln δ)]".
- [ ] Write F(δ) = 4πΘ(δ) − ln δ − ln(1 + ln δ).

**Reading A: every zero-mean u (equivalently, the maximum over δ ≥ 1)**

- [ ] Every zero-mean u has δ(u) ≥ 1, because |k|⁴ ≥ |k|² on ℤ²∖{0}. So the
      qualifier is vacuous, and the first sentence agrees with the
      "Equivalently" formula.
- [ ] What it implies for the asterisked bound: **2.1562247706\* holds.** The
      trial function gives 2.15622477064423579…, margin 4.4·10⁻¹¹; the
      enclosures are listed above. [Pat2026]'s 2.156224 also holds.
- [ ] The untruncated maximum is F ≈ 2.156225528 at δ* ≈ 3.9288. That is
      high-precision numerics, not an interval computation. It lies inside
      the page's bracket [2.1562247706*, 2.1562256466*] and agrees with
      pending #319.

**Reading B: only u with δ(u) ≥ δ₀, for δ₀ as large as one likes**

- [ ] The best constant is then governed by the limit of F(δ) as δ → ∞,
      which is (β+π)/π = 1.8228252497…, the source's L_∞.
- [ ] Every L > (β+π)/π is admissible. L = (β+π)/π itself is not, because F
      stays strictly above its limit. So there is no smallest constant, and
      the infimum is (β+π)/π, the page's own [BDZ2013] lower-bound row.
- [ ] What it implies for the asterisked bound: **2.1562247706\* would be
      false**, and so would [Pat2026]'s 2.156224. The upper bound
      2.1562256466* would remain true but not sharp.
- [ ] Even with a fixed threshold δ₀ = 5, the supremum of F over δ ≥ 5 is
      numerically about 2.1547, below the claim.

**Evidence**

- [ ] [BDZ2013], arXiv 1012.2061v1, as supplied to the audit. The 2013
      journal version was not seen.
  - [ ] Theorem 3.8 states inequality (3.19) "for all 2π × 2π-periodic
        functions u with zero mean".
  - [ ] It defines L := max_{δ≥1} {4πΘ(δ) − (log δ + log(1 + log δ))} in
        (3.20), attained at a finite δ*.
  - [ ] Neither Theorem 3.8 nor the introduction's statement (1.9) restricts
        to large δ.
  - [ ] p. 4: "L ≥ L_∞ := (β+π)/π … the numerics shows that L ≥ L_opt > L_∞".
- [ ] The page itself presupposes reading A in several places:
  - the "Equivalently" formula;
  - BDZ2013's maximiser δ* ≈ 3.92888 in the upper-bound table;
  - [Pat2026]'s trial function at δ ≈ 3.93181;
  - the upper-bound certificate's branch-and-bound over δ ∈ [1, ∞);
  - "The maximum in the variational definition is unique and achieved at
    finite δ*" (Additional comments).
- [ ] F along the exact extremal family (`AUDIT.md` §3.4):
      F(3.93) = 2.156225528, F(148.5) = 2.0865, F(1.1·10³) = 2.0538,
      F(7.3·10⁴) = 2.0074, F(5.5·10⁶) = 1.9771, F(3.6·10¹⁰) = 1.9402, with
      limit 1.82283.
- [ ] Scripts and logs: `audit/c16_readings.py` and
      `audit/logs/package/c16_readings.txt` at
      `c16fe56894c5c725faa9acb7c2743db31d25c304`.
- [ ] Optional side note. BDZ2013's printed L ∼ 2.15627 is about 4.5·10⁻⁵
      above what its own formulas give (2.15622552815 at δ* = 3.92884). The
      page already notes that the printed value lies above the certified
      upper bound.

**The question and the fix**

- [ ] Ask which reading is intended.
- [ ] If A: suggest replacing "with sufficiently large frequency ratio" by
      wording such as "for all zero-mean u ≠ 0 (every such u has δ(u) ≥ 1)".
- [ ] If B: the rows 2.156224 and 2.1562247706* would be false, and the
      value would be the infimum (β+π)/π.
- [ ] Disclose that the analysis is by Claude sessions (the audit), not
      reviewed by a human mathematician, and say what you checked yourself.

## Do not claim

- That 15 bounds were confirmed. The count is 12 asterisked bounds, plus one
  non-asterisked row (1d CERT2026 at 1.4630715826075594) that [T2026] had
  already replayed.
- That any asterisk can now be removed, or that this replay is the "second
  party". It is a replay organised by the person submitting it.
- That a human, you included, has reviewed the mathematics, unless you have;
  then name exactly what you checked.
- That the 16a bound is unconditionally true. It holds under reading A and
  would be false under the literal first sentence.
- That the duplicate 1d CERT2026 row is a merge leftover that should be
  deleted. Which row stays is the maintainer's open question on #243.
- That SCIEL2026, the 16a upper bound or 49a row 81 were checked.
- That row 79 of 49a was checked exhaustively, that the gluing lemma was
  checked against [DEGKM1997], or that the 70a limit exp(1/(2e)) was
  verified.
- That the replay is independent of AI tooling, or of the code in #292 and
  #235.
- That the checkers enforced every check from the start. The enforcement of
  the page comparisons, the minimiser and the python-flint requirement was
  added after the audit.

## Side observations, not acted on

- Lines 38 and 40 of `constants/1d.md` each contain a raw carriage-return
  byte followed by `vert`, where `\rvert` was meant (the audit's "`vert`
  typos"). Replacing each byte with the two characters `\r` would fix them,
  and could go with any future edit of that duplicated "Additional comments"
  block. The upstream notes leave both lines byte-for-byte unchanged.
- README.md marks 10c (3.65*) and 22a (10.02*) with asterisks that their
  pages do not have (`AUDIT.md` §5, side note).
