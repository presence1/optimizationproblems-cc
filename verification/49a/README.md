# Independent check of the asterisked lower bounds on C_49

Constant: [C_49 = μ₃^S, the Erdős–Szemerédi 3-sunflower-free capacity](../../constants/49a.md),
defined as lim f(n)^{1/n}, where f(n) is the largest sunflower-free family in 2^{[n]}.

## Verdict

| Row of `constants/49a.md` | Claimed | What I checked | Result |
| --- | --- | --- | --- |
| 74, [IRSI2026] v1.0 | ≥ 1.5617847* | the 6127-set certificate, exhaustively (SHA-256 `c30a74fe…715b`, pinned by this replay; the page records none) | **Confirmed.** ρ^{1/18} = 1.561784708950537… |
| 75, [IRSI2026] v1.1 | ≥ 1.5621220* | the 6150-set certificate, exhaustively (SHA-256 `c12d0dd6…fc7b`, as on the page) | **Confirmed.** ρ^{1/18} = 1.562122056006815… |
| 76, [IRSI2026] v1.2 | ≥ 1.5647730* | the 6341-set certificate, exhaustively (SHA-256 `7472112c…4e82e`, as on the page) | **Confirmed.** ρ^{1/18} = 1.564773096082831… |
| 77, [Cla2026] | ≥ 1.5664286* | F, rebuilt from the page's description and checked exhaustively | **Confirmed.** (20+2√66)^{1/8} = 1.566428662250036… |
| 78, [Cla2026] | ≥ 1.5666969* | F and H, rebuilt from the page's description and checked exhaustively | **Confirmed.** (1042+2√261207)^{1/17} = 1.566696978754315… |
| 79, [Syl2026] | ≥ 1.5675517* | gadget and unit port counts recomputed from F and H (pure gluing). The 62-point unit (1,086,359,092,267 ≈ 1.1·10¹² sets) is **not** enumerated: its goodness rests on the lemma alone | **Confirmed.** All four port counts equal the page's. ρ^{1/60} = 1.567551755758188… |
| 80, [Syl2026] | ≥ 1.5678015* | B rebuilt and compared with `data/B.txt`; B′ (4364 sets) checked exhaustively | **Confirmed.** ρ^{1/17} = 1.567801520168748… |
| 81, [Kos2026] | ≥ 1.5678599* | — | **Not checked.** The 252292-set family needs an exhaustive search. Even with the lemma below, about 4·10⁸ bitset queries on 252292-bit sets remain, which is impractical in pure Python. A compiled checker would be the right tool |

Every "confirmed" here is **conditional on the XOR-gluing lemma below**. I
proved it myself, and the audit (AUDIT.md §3.5, another Claude session)
checked every step of the proof. It has two parts: (i) distinct pairs give
distinct members, and (ii) the glued family is good. The original self-test
of `check_c49_cla2026.py` tested only (ii), because `glue()` returns a set and
so hides duplicates; since `replay/package` it also tests (i). The audit's
`audit/c49_independent.py` tests both parts exhaustively on all good families
on ≤ 4 points and by classes on 5 points. The lemma is the step the page calls
"[DEGKM1997], Lemmas 3.1, 4.4", but nobody here has read that paper. The
lemma's statement matches every count on the page: the 4349 = 44·46 + 31·75
sets of B, the points added per gluing (the page says "each copy adds 8
points", "one period adds 17 points" and "60 added per unit"; each gluing
merges two points and drops them), and the transfer matrices.

## The XOR-gluing lemma (proof)

Call a family **good** if it is Sperner (no member contains another) and
contains no 3-sunflower.

**Lemma.** Let F₁ be good on X with a point x, and let F₂ be good on a disjoint
set Y with a point y. Put
G = { (A∖x) ∪ (B∖y) : A ∈ F₁, B ∈ F₂, exactly one of x ∈ A, y ∈ B holds }
on (X∖x) ∪ (Y∖y). Then (i) distinct admissible pairs (A, B) give distinct
members of G, and (ii) G is good.

*Proof.* Write A′ = A∖x, B′ = B∖y, s = [x∈A] and t = [y∈B] = 1 − s. A member
S determines A′ = S∩X and B′ = S∩Y.

(i) If (A, B) ≠ (Â, B̂) give the same S, then s ≠ ŝ, so A and Â differ only
in x. One then strictly contains the other, which is impossible in a Sperner
family.

(ii) *Sperner.* Suppose S₁ ⊊ S₂. Then A₁′ ⊆ A₂′ and B₁′ ⊆ B₂′. If s₁ ≤ s₂,
then A₁ ⊆ A₂, so A₁ = A₂. Hence s₁ = s₂, t₁ = t₂ and B₁ ⊆ B₂, so B₁ = B₂ and
S₁ = S₂, a contradiction. If s₁ = 1 and s₂ = 0, then t₁ = 0 and t₂ = 1, so
B₁ = B₁′ ⊆ B₂′ ⊊ B₂, which is again impossible.

*No sunflower.* Suppose distinct S₁, S₂, S₃ have all pairwise intersections
equal to K. Intersecting with X∖x and with Y∖y, the A_i′ have equal pairwise
intersections, and so do the B_i′. A Sperner fact will be used: if three
members T₁, T₂, T₃ (not necessarily distinct) have equal pairwise
intersections, they are either all equal or all distinct. Indeed, if
T₁ = T₂ ≠ T₃, then T₁ = T₁∩T₂ = T₁∩T₃ ⊆ T₃.

- If s₁ = s₂ = s₃, the pairwise intersections of the A_i are equal, because x
  is in all of them or in none. The same holds for the B_i. The A-triple and
  the B-triple cannot both be constant, since that would make S₁ = S₂ = S₃.
  So one of them is a 3-sunflower in F₁ or F₂.
- If exactly one s_i equals 1, x lies in no pairwise intersection of the A_i,
  so their pairwise intersections are equal. A_i with s_i = 1 differs from the
  others, so by the fact above the A-triple is all distinct, and it is a
  3-sunflower in F₁.
- If exactly two s_i equal 1, then exactly one t_i equals 1, and the previous
  case applies to the B-triple in F₂. ∎

The lemma is sharp in the way that matters here. The same-status rule that
also drops the merged point ("same-drop") fails. `check_c49_cla2026.py
--selftest` glues 327 random pairs of good families by brute force. The XOR
rule gave 0 failures, the same-status rule that keeps the merged point gave
0, and the same-drop control gave 276. So the test can detect a broken rule.
Since `replay/package` the self-test also checks part (i): for every XOR
gluing, the number of admissible pairs equals the number of distinct members
(0 failures in 327). It also confirms that this count can fail, on a family
that is not Sperner: {∅, {x}} glued to itself.

**Chains.** Glue copies B₁, B₂, … of good families on disjoint ground sets,
the port v_i of the running family to the port u_{i+1} of the next copy.
Ports not yet used remain points of the glued family. By induction the chain
G_k is good, and each gluing loses 2 points. By (i), |G_k| counts the tuples
(A₁, …, A_k) with [v_i ∈ A_i] + [u_{i+1} ∈ A_{i+1}] = 1. Equivalently, it is
a product of 2×2 transfer matrices T[a][a′] = N_{a,1−a′}, where
N_{ab} = #{S : [u∈S] = a, [v∈S] = b} and the state is the u-status. For
positive T with Perron root ρ, |G_k| ≥ cρ^k (take a positive eigenvector).
If each period adds p points, then f(pk + O(1)) ≥ cρ^k, and since the limit
exists (as shown on the page), C_49 ≥ ρ^{1/p}. A tree of gluings, as in the
[Syl2026] gadget, works the same way: each glued pendant multiplies a
member's count by the number of compatible pendant members, which is 46 or 75
for H at a point, by the injectivity in (i).

## What the scripts check

Every comparison with the page is enforced: if any one disagrees, the
checker prints `MISMATCH` and `NOT CONFIRMED` and exits with status 1. Until
`replay/package`, several were printed but did not affect the verdict, so a
transfer matrix built with the wrong convention still gave CONFIRMED
(AUDIT.md §4, mutation 49a-4). The enforced comparisons are listed below; exact
values are compared in integer arithmetic. The page prints the transpose of T
as defined here.

- `check_c49_cla2026.py` rebuilds F and H **from the page's description
  alone**. F is the 5 stars K_{1,4}, the 10 K_{2,3} and the 60 complements of
  chairs. H is the orbits of 55, 55 and 11 images under x ↦ ax+b with a a
  square mod 11. It checks Sperner and runs an exhaustive triple search
  (67 525 and 287 980 triples, 0 sunflowers). It finds port counts
  (11, 20, 20, 24) and (15, 31, 31, 44) for **every** ordered port pair, and
  computes the two Perron roots and bounds in Arb. Enforced page comparisons
  (12): the port counts of F and H, the points added per period (8 and 17),
  the matrices of F, H and their product as printed, the closed forms
  20 + 2√66 and 1042 + 2√261207 (as trace and discriminant), the product's
  trace and determinant, and the printed leading digits 1.5664286… and
  1.5666969…. `--selftest` runs the random lemma test above.
- `check_c49_syl2026.py` handles rows 79 and 80. For row 79 it computes the
  gadget counts (98308, 152351) and the unit counts from F and H alone; all
  equal the page. For row 80 it rebuilds B by XOR-gluing F at edge (0,3) with
  H at 0, using the labelling given in the certificate README, and finds it
  identical to `data/B.txt`. It checks that `data/Bprime.txt` = B ∪ 15 sets
  with no H-point, then runs an exhaustive check of B′: Sperner, and a pair
  search for any C with C ∩ (A∪B) = A∩B over all 9 520 066 pairs, which finds
  none. Port counts are (622, 1127, 1127, 1488). The bitset search is first
  validated against brute force on F, H and 400 random uniform families, 279
  of which contain a sunflower. Enforced page comparisons (13): the gadget
  counts 250659 = 98308 + 152351, the point counts 28 / 62 / 60, the unit's
  port counts, the row-79 closed form N01 + √(N11·N00), the "first step" that
  row 79 states for B alone (port counts (1123, 1481, 622, 1123), closed form
  1123 + √921182, digits 1.5675245…), B′ = B plus 15 sets with no H-point
  (4364 distinct sets on 19 points, 17 added per copy), B′'s port counts, the
  row-80 closed form 1127 + √925536, and the printed digits 1.5675517… and
  1.5678015….
- `check_c49_irsi2026.py` handles rows 74–76. For each certificate it checks
  the SHA-256 of the file, distinctness, Sperner (numpy), runs the same
  exhaustive pair search over 1.9–2.0·10⁷ pairs (none found), and compares
  layer sizes and port matrices with the page. Further enforced page
  comparisons: the trace and determinant of the page's matrix, 18 points per
  copy, the ports u = 18, v = 19 (v1.1 and v1.2), the characteristic
  polynomials x² − 3710x + 1969416 and x² − 3901x + 2333844 and the closed
  forms 1855 + √1471609 and (3901 + √5882425)/2 (v1.1 and v1.2), ρ to the 4
  decimals printed, and the printed digits 1.5621220560… and 1.5647730960….

## Reproduce

The run outputs are in `run_output_*.txt`. They are the re-run on branch
`replay/package`; the original runs of 3 November 2026 are in the git
history of these files. Runtimes were under 1 s for `check_c49_cla2026.py`,
about 10 s for `check_c49_syl2026.py` and 60–90 s for `check_c49_irsi2026.py`,
on Python 3.13.18, numpy 2.5.3 and python-flint 0.9.0.

```bash
python3 -I verification/49a/check_c49_cla2026.py --selftest
```

```bash
python3 -I verification/49a/check_c49_cla2026.py
```

Data for rows 79–80 comes from xSyllaa/sunflower-pendant-chain @ `8e21d02`:
`data/B.txt` has SHA-256 `340cef5e…7d37af` and `data/Bprime.txt` has
`2a723857…96b5cec`, both pinned in the script. Copy both files into one
directory and run:

```bash
python3 -I verification/49a/check_c49_syl2026.py --data DIR
```

Data for rows 74–76 comes from Aspect5/sunflower-free-capacity. Fetch it by
commit, not by tag, because tags can be moved. The commits below are the ones
the tags v1.0, v1.1 and v1.2 point to (checked on 4 November 2026). In a clone
of that repository, run:

```bash
git show 4d23c9ad391c9a087cad03a3c3346b5f79badae0:cert_c49_chain20.json > DIR/v10.json
```

```bash
git show f685bfab116e36568aacc9558eb582376764b88d:cert_c49_chain20_s17.json > DIR/v11_s17.json
```

```bash
git show e478c81d8b57eba956fdaf621643eb6f0781f820:cert_c49_chain20_v12.json > DIR/v12.json
```

The checker verifies all three SHA-256 values. For v1.1 and v1.2 they match
the abbreviated values printed on the page (`c12d0dd6…fc7b` and
`7472112c…4e82e`). The page records none for v1.0, so the checker pins the
bytes this replay checked:
`c30a74fed64616c5c6980fae91f94ae5899fed6a4cb338b537480ee9517d715b`.
`audit/fetch_all.sh` does all of this. Then run:

```bash
python3 -I verification/49a/check_c49_irsi2026.py --data DIR
```

## Assumptions

- The definition and the existence of the limit are as on the page at fork
  commit `87b4ebb`.
- The XOR-gluing lemma is the proof above. The audit, another Claude session,
  checked it step by step and tested it (AUDIT.md §3.5); no human has
  checked it, and nobody here has compared it with [DEGKM1997].
- For rows 79–80 I used the labelling convention stated in the Syl2026
  README. It is confirmed by my independent rebuild of B matching `B.txt`
  exactly. For rows 74–76 I took bit i of each mask to be point i. That is
  consistent with the port matrices and layer sizes matching the page.

## Independence

I read the constant page, and only the format and labelling paragraphs of the
Syl2026 and IRSI READMEs. I did not open their `verify.py`, `verify_bprime.py`,
`gadget.py`, `sf_tri.c`, `check_c49.py`, `check_openai_v12.py` or
`sunflower_scan.c`. F and H were rebuilt from the page text, not read from
their files. The lemma's proof is my own. All of this was written by an AI
agent (Claude). The certificates were found with AI agents too, some of them
Claude, so this is independent of their code but not of the tooling. No human
has checked it.

## Related upstream work

Upstream pull request
[#235](https://github.com/teorth/optimizationproblems/pull/235) (open when the
audit was written) already posts a replay of rows 74–78 and asks for their
asterisks to be removed, in the style used before the second-party rule
(AUDIT.md §6.2). Rows 79–80 are not covered by it. The checkers here do not
refer to #235, and nobody here has compared them with its code.

## Corrections made on branch `replay/package` (4 November 2026)

- All three checkers now enforce every comparison with the page (AUDIT.md §4,
  mutation 49a-4; §5, item 9). Besides the comparisons the audit named (the
  Cla2026 trace/determinant and closed forms, the row-80 closed form), the
  Syl2026 gadget counts and "the extra sets avoid H" were also printed
  without being enforced; both are now enforced. Mutation tests 49a-16 to
  49a-22 check the new enforcement.
- "I proved it myself and tested it by brute force" overstated the testing:
  the self-test covered only part (ii) of the lemma. It now covers part (i)
  too, and this README says which test covers what (AUDIT.md §5, item 5).
- "losing 2 points" is not the page's wording; the page's own phrases are
  now quoted (AUDIT.md §5, item 5).
- Row 79's 62-point unit is not enumerated; the verdict table now says so
  (AUDIT.md §5, item 4).
- The IRSI data is fetched by commit, not by tag, and the v1.0 bytes are
  pinned by SHA-256 in the checker (AUDIT.md §5, item 10).
- Added the note on upstream #235 (AUDIT.md §5, item 11).
