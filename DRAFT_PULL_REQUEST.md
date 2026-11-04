<!-- Suggested title: Record independent replays of six asterisked rows on 1d, 16a, 49a and 70a (asterisks kept) -->
<!-- Before posting: replace both "#ISSUE" below with the number of your 16a issue. -->

This pull request changes Markdown only. It records independent replays of six asterisked bounds and **keeps all six asterisks**, pending a second party, as CONTRIBUTING requires. I organised this replay, so it cannot by itself justify removing them.

The replay was done by AI agents (Claude). I re-ran it myself, but I am not a mathematician, and no mathematician has reviewed it. Details are under "AI use and my own review" below.

### What changes

- `constants/1d.md`, `16a.md`, `49a.md` and `70a.md`:
  - one sentence appended to the comments of each replayed row;
  - one reference entry, `[RPL2026]`, per page;
  - one AI-use note per page.
- No asterisk, bound or existing sentence is changed. In the 16a row, a full stop is added before the new sentence.
- The code, logs and an audit are in my fork at a pinned commit (see "Re-derive"). Only Markdown is proposed here.

### Rows covered

| Row | Bytes replayed (repository @ commit, file, SHA-256) | Value obtained |
| --- | --- | --- |
| 1d, STEPS2026, ≤ 1.460217284022874\* | steps-re/c1d-certificate @ `9a09149`, `construction.json`, `3dd39fae…b3a28c` | Values read as binary64: exactly the page's fraction, 1.46021728402287398524…. Read as the printed decimals: 1.46021728402287397507…. |
| 1d, AER2026, ≤ 1.459989046905384\* | unclegareth-create/alphaevolve_repository_of_problems @ `4b3bbd2`, `experiments/autocorrelation_problems/problem_4_signed_autoconvolution_bounds.py` (parsed as text, never executed), `1a290ad1…ff54b2` | Decimals: 1.45998904690538314495…. Binary64: 1.45998904690538324315…. |
| 70a, Pin2026, ≥ 1.20194336\* | rpinho/c70-certificate @ `680e074`, `certificates/c70_candidate.json` (parameters only), `03ff0d6d…90c0cc` | Arb: [1.2019433684431505669948027797355241 ± 3.8·10⁻³⁵]. mpmath intervals: [1.201943368443150566994802779735524137829, …524138179]. |
| 16a, lower bound, ≥ 2.1562247706\* | maximusrufus/c16-bgw-certificates @ `0c57070` (the page pins no commit; this was the repository's latest commit at the time), `lower_certificate.json` (R and μ only), `de314c10…4b6991` | Arb: ≥ [2.1562247706442357903 ± 4.3·10⁻²⁰]. binary64 with `math.fsum` and a proven error bound: [2.1562247706442 ± 4.6·10⁻¹⁴]. |
| 49a, row 79, ≥ 1.5675517\* | No file: the families F and H are rebuilt from the page's description | All port counts as on the page. ρ^(1/60) = 1.5675517557581882198…. |
| 49a, row 80, ≥ 1.5678015\* | xSyllaa/sunflower-pendant-chain @ `8e21d02`, `data/B.txt` (`340cef5e…7d37af`) and `data/Bprime.txt` (`2a723857…6b5cec`) | B rebuilt from F and H equals `B.txt`. B′ (4364 sets) is Sperner, with no 3-sunflower among all 9,520,066 pairs. ρ^(1/17) = 1.5678015201687483405…. |

<details>
<summary>Full commit hashes and SHA-256 values</summary>

| File | Commit | SHA-256 |
| --- | --- | --- |
| steps-re/c1d-certificate `construction.json` | `9a091494facc801eaf6b92b175b63c58b7c3b30b` | `3dd39fae744555179b0356b84e752db724e892bd23dda51403976edfb5b3a28c` |
| unclegareth-create/alphaevolve_repository_of_problems `…/problem_4_signed_autoconvolution_bounds.py` | `4b3bbd2a44db92442e4ebb4e64e0bb90f229aad1` | `1a290ad1074c10a871adaf2bd44402af56be8cf151f1f775a8fc37c7bdff54b2` |
| rpinho/c70-certificate `certificates/c70_candidate.json` | `680e074bb50929734bfd76484d716cd3e85827f0` | `03ff0d6df3dfa6ea06f901a9319c968eb7c013f5d0cc3f1f00cfa58e9490c0cc` |
| maximusrufus/c16-bgw-certificates `lower_certificate.json` | `0c570700f080ca23549e10380901addfc8b7b8ae` | `de314c10bd4a63d35604d28c0d0556b8b5ae67ab1840c06628039d8fd64b6991` |
| xSyllaa/sunflower-pendant-chain `data/B.txt` | `8e21d0287711b4f0bfc23e9443523e2aa472cca1` | `340cef5e71124ed624425abf81e9621839406cbf44b3fd242594d8edcb7d37af` |
| xSyllaa/sunflower-pendant-chain `data/Bprime.txt` | `8e21d0287711b4f0bfc23e9443523e2aa472cca1` | `2a72385704b8203269cda4f4b0dfdabc74d5adb8f4a2bc1dac1f570cb96b5cec` |

</details>

### How the values were checked

- **1d.** For a step function with N equal cells, |f∗f| is piecewise linear, with knots at the cell boundaries. So `R(f) = 2N·max|c_s| / (Σv)²` exactly, where the c_s are the autoconvolution coefficients.
  - The c_s were computed in exact rational arithmetic by two different multiplication algorithms: a direct loop, and FLINT.
  - The knot formula itself was checked by brute-force exact integration at every knot.
- **70a.** The retained Steiner term was evaluated in two independent ways: literally in Arb ball arithmetic, and in closed form with mpmath interval arithmetic and Robbins' factorial bounds.
  - The result is **conditional on Patankar's cube–ball criterion**. The replay re-derives it (`verification/70a/README.md`), but no human has reviewed that derivation.
  - The limit exp(1/(2e)) was not checked.
- **16a.** The trial function's three lattice sums were enclosed in two ways: by Arb, and separately by binary64 terms with a proven error bound, summed with `math.fsum`. The counts r₂(n) were checked against Gauss's circle count and Jacobi's formula.
  - **This holds for the constant as defined by the page's "Equivalently" formula. Under a literal reading of the page's first sentence, the bound would be false.**
  - I have asked which reading is intended in #ISSUE.
- **49a.** F and H were rebuilt from the page text, and B′ was checked exhaustively. All counts were recomputed exactly, and the checkers enforce every comparison with the page.
  - Both rows are **conditional on the gluing lemma**. A proof is written out in `verification/49a/README.md`, but nobody involved has compared it with [DEGKM1997], and no human has reviewed it.
  - Row 79's 62-point unit (about 1.1·10¹² sets) is not enumerated; its goodness rests on the lemma.

### Red controls

The checkers come with 52 mutation tests. Each one breaks something on purpose:

- claims nudged past the exact values;
- data changed, both with the hash pin intact and with it updated;
- a negative weight;
- recorded page values changed;
- wrong transfer-matrix conventions;
- python-flint made unavailable.

With the checkers at the commit cited, all 52 behave as a correct checker must: each mutation makes the run fail, for the right reason. Run against the checkers as they were before the audit, the same tests give 39 of 52. The 13 failures are exactly the weaknesses the audit found, which were then fixed.

### Re-derive

Code and logs: [presence1/optimizationproblems-cc @ `c16fe56`](https://github.com/presence1/optimizationproblems-cc/tree/c16fe56894c5c725faa9acb7c2743db31d25c304).

You need Python 3.13, numpy 2.5.3, python-flint 0.9.0 and mpmath 1.4.1, and a full clone at that commit. Then run:

```
sh audit/fetch_all.sh ROOT
sh audit/run_all.sh ROOT
```

- `fetch_all.sh` downloads the certificate files listed above, by commit, and checks their SHA-256. Nothing it downloads is executed.
- `run_all.sh` takes about 20 minutes on 4 cores.
- The commands for each checker are in each `verification/<id>/README.md`.

### Audit

A second, separate Claude session audited the replay (`AUDIT.md` at the commit cited). It found no wrong bound. It did find:

- checks that were printed but not enforced;
- some overstated wording;
- the 16a definitional problem.

These were fixed afterwards and everything was re-run. The appendix of `AUDIT.md` maps each finding to its fix.

### AI use and my own review

- **Who did the work.** The replay (checkers, written proofs, logs) was done by Claude Opus 5.5 agents. A second Claude session audited it, and a further Claude session made the fixes the audit asked for.
- **This description** was drafted with Claude's help. I have read it and checked it against the logs.
- **No mathematician.** I am not a mathematician, and no mathematician has reviewed any of this work.
- **What I checked myself.** On 4 November 2026 I re-ran everything from the commit cited, on my own laptop (Debian GNU/Linux 13 under WSL, Python 3.13.5).
  - Every checker reported CONFIRMED (or OK), and the four independent checks passed.
  - The mutation tests gave 52 of 52, and 39 of 52 against the pre-audit checkers, as expected.
  - Every number quoted in the page edits appears in the logs at that commit, and all the links open.
  - As a non-mathematician, I may have missed something.
- **No connection.** I have no connection to the authors of these certificates (steps-re, the AER2026 contributor, R. Pinho, maximusrufus, Sylla).
- **Questions.** I cannot answer technical questions myself. I will pass them to Claude and post its answers after reading them, marked as such.

### Related

- #ISSUE asks which reading of the 16a definition is intended.
- Rows not covered here:
  - 1c Kos2026 is already replayed in #292, and 49a rows 74–78 in #235.
  - Neither 1d CERT2026 row is touched. The unstarred one was replayed by [T2026], and which of the two should stay is the open question on #243.
  - Not checked at all: 1d SCIEL2026 (its Zenodo record is restricted), the 16a upper bound, and 49a row 81.
- Other open pull requests also edit these pages (as of 3 November: 1d #269, #271, #286, #312; 16a #319). This one only appends a sentence to existing rows and adds one reference and one note per page, so any conflicts should be small.
