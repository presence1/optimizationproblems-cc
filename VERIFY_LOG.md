# Verification log: unverified (asterisked) bounds

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

## Results so far

| Constant | Row(s) checked | Outcome | Where |
| --- | --- | --- | --- |
| 1d | STEPS2026 1.460217284022874*, AER2026 1.459989046905384*, CERT2026 1.4630715826075594 | **Confirmed**, all three, in exact rational arithmetic | branch `verify/1d`, [`verification/1d/`](verification/1d/README.md) |
| 1d | CERT2026 duplicate row 1.463071582607559* | The printed value is 3.3·10⁻¹⁶ **below** the certificate's exact value, so it is not implied as printed. The same page's replayed row (…594) already records this | same |
| 1d | SCIEL2026 1.457854884921989* | **Not checked**: the data is in a restricted Zenodo record | same |

The 1c row is the next candidate (see below). This table is updated as checks
finish.

## Candidates

| Const. | Asterisked bound(s) | Source | Artifact (location) | Reachable | Tract. | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 1a | ≥ 1.292* | PBV2026 | code/certificate, GitHub AndreiPiterbarg/sidon-autocorrelation | yes | C | A lower bound for a sup-of-autoconvolution constant must cover all f. Not a single test function |
| 1c | ≥ 0.4103333* | Kos2026 | step function, K = 24576, 24592 integer weights, GitHub DennisKoshta/c1c-autocorrelation-certificate @ `a4ee94ef29ff` | yes | **A** | Exact autocorrelation at all lags. About 6·10⁸ products by direct loop, or seconds by FLINT polynomial multiplication |
| 1d | ≤ 1.463071582607559*, 1.460217284022874*, 1.459989046905384*, 1.457854884921989* | CERT2026, STEPS2026, AER2026, SCIEL2026 | step functions, 300/600/600/800 cells (GitHub ×3, Zenodo ×1) | 3 of 4 | **A** | Done (see above) |
| 3a | ≥ 1.173077*, 1.187326…*, 1.19102809*, 1.19519192*, 1.19230254*, 1.19281555*, 1.19359680* | Z2025, Num2026, K2026, K2026b, M2026, Syl2026 | masked-digit limit constructions with directed-rounding/MPFR certificates, Lean for K2026b. GitHub (K2026, M2026, Syl2026), Zenodo (Num2026) | mostly | B | Needs the GHR framework and the K2026b Prop. 3 reduction. The final step is a Stirling bound at 10¹³–3·10²⁴ digits, which is feasible in interval arithmetic once the reduction is accepted |
| 5a | ≤ 0.98173*, 0.94325*, 0.9428095* | St26, Mad26, Akw26 | exact-rational covering inequalities in the HZ26 framework (161 and 6145 inequalities). GitHub for St26 and Akw26; forum only for Mad26 | partly | B | The page names HZ26 Lemma 2.1 as the load-bearing unreviewed input |
| 10a | ≤ 1.7813* | P2026 | Arb certificates for a degree-51 polynomial (arXiv 2609.20074) | not tried | B/C | |
| 12a | ≤ 0.8618* | O2026 | integer computation (Edmundson–Madansky on a mesh), GitHub devinokeefe/travelling-sales-person-constant-bounds @ `f5d1842` | yes | B | The integer is recomputable, but the probabilistic reduction is intricate |
| 13a | ≥ 0.239* | K2026 | polygonal arcs + subdivision certificate (arXiv 2609.21968) | not tried | C | geometric case analysis |
| 16a | ≤ 2.1562256466*, ≥ 2.1562247706* | maximusrufus | lattice sums with tail bounds, interval branch-and-bound, GitHub maximusrufus/c16-bgw-certificates | yes | B | The lower bound is an explicit trial function with \|k\| ≤ 4000, about 5·10⁷ lattice terms with outward rounding |
| 19a | ≤ 0.4395*, 0.423* | XL2026, Lin2026 | Lean 4 with `native_decide` | yes | C | a Lean build, not a Python replay |
| 21a | ≤ 0.1965*, 0.1875*, 0.172422*, 0.16*, 0.1595* | MI2026a–d, Kor2026 | certified numerics for H_t zeros (Zenodo ×3, GitHub ×2) | partly | C | heavy rigorous numerics |
| 22b | ≤ 7.2012719* | Claude2026 | interval-arithmetic thickness proof of explicit curves, GitHub YouhuaLi/tight-alternating-knot-constant @ `debf7c9` | yes | B/C | C^{1,1} curve thickness, with an asymptotic step |
| 24a | ≤ 7.5199*, 6.9013* | GFL2026a, AS2026 | analytic proofs (arXiv). AS2026 has code (suvrit/komlos) | yes | C | The number 6.9013 is a root that is easy to recompute. The bound itself rests on the proof |
| 28a | ≤ 9* | OAI2026 | paper + Lean files | yes | C | proof-based |
| 31a | ≤ 0.825101*, 0.824120* | J2026 | Lueker automaton, 5·10⁷ / 4·10⁸ states, GitHub leandrejack-afk/chvatal-sankoff-bound | yes | C | Too large for a Python replay here |
| 31a | ≥ 0.79970 ("unverified", no `*` on the page) | AA2026 | Monte Carlo + Hoeffding | — | — | The page says it is probabilistic, not a deterministic bound |
| 41a | ≤ 2.2195* | Baek2024 | analytic proof | — | — | no finite certificate |
| 42a | ≤ 0.6906538*, 0.6888863712*, 0.6873358063* | Gri26, Pin26, Kos2026 | rational profiles + interval/Arb checks of a limiting inequality, GitHub ×3 | yes | B | The asymptotic reduction is unrefereed. The finite check is an interval evaluation |
| 43a | ≥ 0.860* | S2026 | 3.3·10⁸ region certificates (Zenodo + GitHub aimathpapers/Steiner_Ratio) | partly | C | conditional on the KHSHGW2026 lemma layer |
| 44a | ≤ 4.3654674227*, 4.3576549226* | Epi2026, P2026 | exact rational degree-48 certificates in Wellens's recurrence, GitHub BakeLab/Epi-results, rpinho/c44-certificate | yes | B | needs Wellens's recurrence |
| 49a | ≥ 1.5617847* … 1.5678599* (8 rows) | IRSI2026, Cla2026, Syl2026, Kos2026 | explicit set families (75 to 250659 sets) + 2×2 transfer matrices, GitHub ×4 | yes | B | Sunflower-freeness is finite and checkable. The chain construction relies on [DEGKM1997] Lemmas 3.1/4.4 |
| 57c | ≤ 0.656319277272*, 0.65628589* | OCP2010, vS2026 | numerical / Arb conformal-radius proof, GitHub WynandVStaden/bloch-landau-slit-discs | yes | C | |
| 65a | ≤ 2.4*, 3.99* | OAI2026+IK2004, Nas2026 | deduction (no certificate); LP certificates on 4.2·10⁶ boxes | yes | C | |
| 68a | ≥ 0.432* | Pin2026 | explicit measure (12 atoms + Lebesgue on [0.999,1]), GitHub rpinho/korenblum-c68-certificate @ `9d48de6` | yes | B | needs the paper's criterion; possibly a one-variable interval check |
| 70a | ≥ 1.20194336* | Pin2026 | single Steiner-term evaluation at n = 10¹², GitHub rpinho/c70-certificate @ `680e074` | yes | B | log-gamma in interval arithmetic once the formula is pinned down |
| 82a | ≤ 0.2535744749068227*, 0.2534449* | Epi26, Pin26 | Doche limit-point construction (deg Q ≈ 10⁹), Arb checkers, GitHub rpinho/c82-height-certificate | yes | B/C | |
| 84a | ≥ 1.0427*, 1.04317* | Nas2026(b) | Lean (Palomar) + interval L-function certificates | yes | C | |
| 84b | ≤ 1.9993* | Al26 | explicit-constant calculation in a note (no certificate file) | yes | B | proof-based; the arithmetic was checked by [T2026] per the page |
| 86a | ≤ 1.8117251*, 1.8084990* | Pin26, Kos2026 | measure with 11 or 19 auxiliary polynomials, exact rational + Arb, GitHub ×2 | yes | B | a one-variable inequality over an interval; feasible with interval arithmetic once the [SO24] criterion is set up |
| 89a | ≤ 0.0301388876*, 0.0301388794*, 0.0301388857* | VSJ2026, SK2026, Kos2026 | step graphons with 3840 / 7680 classes, exact K4 counts, GitHub ×3 | yes | B/C | A naive O(n⁴) count is about 10¹⁴–10¹⁵ terms, so symmetry reduction is needed |
| 90a | ≥ 44* | M2026 | Lean proof (about 8000 files, about 250 CPU-hours), SAT checks | yes | C | |

## Choice

Priority went to the tractability-A rows: **1d** first (three certificates
reachable, small, and the reduction proved in a few lines), then **1c**. The
B rows that need only one framework lemma (70a, 68a, 86a, 49a) come after, if
time allows.
