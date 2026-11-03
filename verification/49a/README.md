# Independent check of the asterisked lower bounds on C_49

Constant: [C_49 = μ₃^S, the Erdős–Szemerédi 3-sunflower-free capacity](../../constants/49a.md),
defined as lim f(n)^{1/n}, where f(n) is the largest sunflower-free family in 2^{[n]}.

## Verdict

| Row of `constants/49a.md` | Claimed | What I checked | Result |
| --- | --- | --- | --- |
| 74, [IRSI2026] v1.0 | ≥ 1.5617847* | the 6127-set certificate, exhaustively | **Confirmed.** ρ^{1/18} = 1.561784708950537… |
| 75, [IRSI2026] v1.1 | ≥ 1.5621220* | the 6150-set certificate, exhaustively (SHA-256 `c12d0dd6…fc7b`, as on the page) | **Confirmed.** ρ^{1/18} = 1.562122056006815… |
| 76, [IRSI2026] v1.2 | ≥ 1.5647730* | the 6341-set certificate, exhaustively (SHA-256 `7472112c…4e82e`, as on the page) | **Confirmed.** ρ^{1/18} = 1.564773096082831… |
| 77, [Cla2026] | ≥ 1.5664286* | F, rebuilt from the page's description and checked exhaustively | **Confirmed.** (20+2√66)^{1/8} = 1.566428662250036… |
| 78, [Cla2026] | ≥ 1.5666969* | F and H, rebuilt from the page's description and checked exhaustively | **Confirmed.** (1042+2√261207)^{1/17} = 1.566696978754315… |
| 79, [Syl2026] | ≥ 1.5675517* | gadget and unit port counts recomputed from F and H (pure gluing) | **Confirmed.** All four port counts equal the page's. ρ^{1/60} = 1.567551755758188… |
| 80, [Syl2026] | ≥ 1.5678015* | B rebuilt and compared with `data/B.txt`; B′ (4364 sets) checked exhaustively | **Confirmed.** ρ^{1/17} = 1.567801520168748… |
| 81, [Kos2026] | ≥ 1.5678599* | — | **Not checked.** The 252292-set family needs an exhaustive search. Even with the lemma below, about 4·10⁸ bitset queries on 252292-bit sets remain, which is impractical in pure Python. A compiled checker would be the right tool |

Every "confirmed" here is **conditional on the XOR-gluing lemma below**. I
proved it myself and tested it by brute force. It is the step the page calls
"[DEGKM1997], Lemmas 3.1, 4.4", but I did not read that paper. The lemma's
statement matches every count on the page: the 4349 = 44·46 + 31·75 sets of B,
"losing 2 points" per gluing, and the transfer matrices.

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

- `check_c49_cla2026.py` rebuilds F and H **from the page's description
  alone**. F is the 5 stars K_{1,4}, the 10 K_{2,3} and the 60 complements of
  chairs. H is the orbits of 55, 55 and 11 images under x ↦ ax+b with a a
  square mod 11. It checks Sperner and runs an exhaustive triple search
  (67 525 and 287 980 triples, 0 sunflowers). It finds port counts
  (11, 20, 20, 24) and (15, 31, 31, 44) for **every** ordered port pair, and
  computes the two Perron roots and bounds in Arb. `--selftest` runs the
  random lemma test above.
- `check_c49_syl2026.py` handles rows 79 and 80. For row 79 it computes the
  gadget counts (98308, 152351) and the unit counts from F and H alone; all
  equal the page. For row 80 it rebuilds B by XOR-gluing F at edge (0,3) with
  H at 0, using the labelling given in the certificate README, and finds it
  identical to `data/B.txt`. It checks that `data/Bprime.txt` = B ∪ 15 sets
  with no H-point, then runs an exhaustive check of B′: Sperner, and a pair
  search for any C with C ∩ (A∪B) = A∩B over all 9 520 066 pairs, which finds
  none. Port counts are (622, 1127, 1127, 1488). The bitset search is first
  validated against brute force on F, H and 400 random uniform families, 279
  of which contain a sunflower.
- `check_c49_irsi2026.py` handles rows 74–76. For each certificate it checks
  distinctness, Sperner (numpy), runs the same exhaustive pair search over
  1.9–2.0·10⁷ pairs (none found), and compares layer sizes and port matrices
  with the page.

## Reproduce

The run outputs are in `run_output_*.txt`. Runtimes were under 1 s for
`check_c49_cla2026.py`, 9 s for `check_c49_syl2026.py` and 59 s for
`check_c49_irsi2026.py`, on Python 3.13.18, numpy 2.5.3 and python-flint 0.9.0.

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

Data for rows 74–76 comes from Aspect5/sunflower-free-capacity. Run
`git show v1.0:cert_c49_chain20.json > DIR/v10.json`,
`git show v1.1:cert_c49_chain20_s17.json > DIR/v11_s17.json` and
`git show v1.2:cert_c49_chain20_v12.json > DIR/v12.json`, then:

```bash
python3 -I verification/49a/check_c49_irsi2026.py --data DIR
```

## Assumptions

- The definition and the existence of the limit are as on the page at fork
  commit `87b4ebb`.
- The XOR-gluing lemma is the proof above, which I have not seen checked by
  anyone else.
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
