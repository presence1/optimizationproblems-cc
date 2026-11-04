# Next steps: a guide for presence1

This guide is for you, the owner of this fork. It assumes you are comfortable
with GitHub but are not a trained mathematician. It walks you through what to
do next, in order. Each step says why it matters, roughly how long it takes,
and what "done" looks like.

Nothing has been posted to the upstream repository yet. Everything below is
your decision. You can stop at any step.

## The situation in plain words

- **The upstream repository** ([teorth/optimizationproblems](https://github.com/teorth/optimizationproblems))
  is a public table of the best known numerical bounds for many mathematical
  constants. A *bound* is a statement such as "this constant is at least
  1.5678015".
- **An asterisk** (`*`) next to a bound means its verification is currently
  minimal. Typically the evidence is a large computer file (a *certificate*)
  that only its author has checked.
- **What was done for you.** Claude agents re-ran (*replayed*) the
  computations behind 12 asterisked bounds from scratch, with programs of
  their own. All 12 came out correct.
- **The audit.** A second, separate Claude session audited that work. It
  found no wrong bound, but it did find weak spots in the programs and some
  overstated wording. A third session fixed those problems and re-ran
  everything.
- **No human mathematician has checked any of this.** That matters for two
  reasons:
  - The repository's rules require the person submitting AI-assisted work to
    review and verify it.
  - Two of the results (pages 70a and 49a) also rest on short mathematical
    arguments, which a program cannot fully check.
- **What you would propose upstream is modest.** It adds one sentence on each
  of six table rows ("independently replayed …"), plus a reference and an
  AI-use note per page.
- **You are not asking for any asterisk to be removed.** The rules say only
  someone other than the person asking can do that.
- **One real problem turned up, on page 16a.** Its definition can be read in
  two ways. The bound is correct under one reading and false under the
  other. That deserves a separate question to the maintainer.

## What is where

| Where | What it is |
| --- | --- |
| Branch `replay/package` | All the evidence: the programs, their output logs, the audit, and these notes. It stays in your fork and is never submitted upstream. **Commit `c16fe56`** on this branch holds the code and logs; the links inside the page edits point to it. |
| Branch `replay/upstream-notes` | The small Markdown change you would propose upstream: four files, `constants/1d.md`, `16a.md`, `49a.md` and `70a.md`. **Commit `d79b144`** is that change, and is what your pull request will contain. |
| `DRAFT_ISSUE_16A.md`, `DRAFT_PULL_REQUEST.md` | Drafts of the text for Steps 8 and 9, written from your Step 7 answers. |
| `SUBMISSION_NOTES.md` | Checklists of what your pull request and your 16a question must say, and a list of things you must not claim. |
| `AUDIT.md` | The audit. Its §7 is a plain-language summary; the appendix at the end lists what was fixed afterwards. |
| `VERIFY_LOG.md` | The overall results table. |

## Step 1: Protect the evidence (5 minutes)

**Why:** the text you would submit links to commit `c16fe56` of your fork. If
that commit disappears, the links break.

- Do not delete `replay/package`, and never force-push it.
- Keep the fork public.

**Done when:** you know not to touch that branch. A permanent tag is added in
Step 3.

## Step 2: Read the summaries (30 to 60 minutes)

**Why:** you will be the one answering for this work. You don't need to follow
the mathematics, but you should know what is being claimed.

Read, in this order:

1. `VERIFY_LOG.md`: the "Results" table and the "Count" paragraph under it.
2. `AUDIT.md`: §7, "Plain-language summary", then the appendix at the end.
3. `SUBMISSION_NOTES.md`: all of it.

**Done when** you can say in your own words:

- which six rows the pull request touches;
- what "replayed" means;
- the three caveats:
  - 70a depends on a geometric argument (Patankar's criterion);
  - 49a depends on a combinatorial argument (the gluing lemma);
  - 16a depends on which reading of the definition is meant;
- that the asterisks stay.

## Step 3: Re-run everything yourself (about an hour, mostly waiting)

**Why:** this is the part of "review and verify" that you can do without
being a mathematician. You confirm that the programs run on your own
computer and print the same results.

**You need:**

- a Mac or a Linux computer (on Windows, use WSL, the Windows Subsystem for
  Linux);
- git, an internet connection and about 2 GB of free memory;
- Python 3.13. That is what was used; other recent versions will probably
  work but were not tested.

Run these commands one at a time, in a terminal. First, get the code and
enter the folder:

```bash
git clone --branch replay/package https://github.com/presence1/optimizationproblems-cc.git
```

```bash
cd optimizationproblems-cc
```

Optionally, give the cited commit a permanent name (a *tag*), so it survives
even if a branch is deleted by mistake:

```bash
git tag replay-2026-11-04 c16fe56894c5c725faa9acb7c2743db31d25c304
```

```bash
git push origin replay-2026-11-04
```

Create a private Python environment, so nothing is installed system-wide, and
install the three libraries at the versions used:

```bash
python3 -m venv "$HOME/replay-venv"
```

If that command complains that `venv` or `ensurepip` is missing, which is
common on Ubuntu and Debian, install your system's `python3-venv` package
first, or ask for help.

```bash
. "$HOME/replay-venv/bin/activate"
```

```bash
pip install numpy==2.5.3 python-flint==0.9.0 mpmath==1.4.1
```

```bash
python3 -I -c "import numpy, flint, mpmath; print('libraries OK')"
```

The last command must print `libraries OK`. If `pip install` fails, stop and
ask for help (see "When to stop and ask for help" below). If you come back
later in a new terminal window, run the `activate` command again first.

Download the certificate data. This needs a new, empty folder name; the
script only downloads files and checks their fingerprints (SHA-256 hashes),
and it runs none of them:

```bash
sh audit/fetch_all.sh "$HOME/replay-data"
```

It must end with 12 lines that each end in `: OK`. If you run it again
later, use a new folder name (for example `replay-data-2`) and use that name
in the commands below too.

Now run everything. This takes 20 to 30 minutes on a 4-core computer, and
longer on fewer cores:

```bash
sh audit/run_all.sh "$HOME/replay-data"
```

At the end, the script prints a long list of lines. **Some of them say
`MISMATCH` or `NOT CONFIRMED`, and that is expected.** Those lines come from
the *mutation tests*, which deliberately break copies of the programs to make
sure the programs then fail. Don't judge the run by that list. Use these two
checks instead.

**Check 1**, the mutation tests:

```bash
grep -h SUMMARY "$HOME/replay-data/package_logs/mutation_tests.txt" "$HOME/replay-data/package_logs/mutation_tests_original_checkers.txt"
```

It must print exactly:

```
SUMMARY: 52 of 52 tests behaved as a correct checker must
SUMMARY: 39 of 52 tests behaved as a correct checker must
```

The second line is about the old, unfixed programs. 39 of 52 is the expected
result there, and it shows the fixes were needed.

**Check 2**, the actual results:

```bash
grep -h -E '^RESULT|^checker integrity|^selftest passed' "$HOME/replay-data/package_logs/"run_*.txt "$HOME/replay-data/package_logs/"c*_*.txt
```

It must print these 15 lines (the order may differ):

```
RESULT: CONFIRMED: C_16 >= 2.1562247706
selftest passed
checker integrity (hashes, shape, A == B, check C, fractions, argmin): OK
selftest passed
checker integrity (hashes, A == B, check C, recorded fractions): OK
selftest passed
RESULT: CONFIRMED (given the XOR-gluing chain lemma, proved in README)
RESULT: CONFIRMED rows 79 and 80 (given the XOR-gluing lemma)
RESULT: all three rows CONFIRMED
selftest passed
RESULT: CONFIRMED: C_70 > 1.20194336 (given the criterion)
RESULT: ALL CHECKS PASSED
RESULT: ALL CHECKS PASSED
RESULT: ALL CHECKS PASSED
RESULT: ALL CHECKS PASSED
```

**Done when** both checks match. Write down the date, your computer and
operating system, your Python version (`python3 --version`), and the fact
that everything matched. You will state this in Step 9.

**If anything differs, stop.** Don't submit, and ask for help.

## Step 4: Check the proposed page edits against the evidence (30 minutes)

**Why:** you are vouching that the text matches the evidence. Checking that
every number in the text appears in the logs needs care, not mathematics.

1. Open the comparison:
   <https://github.com/presence1/optimizationproblems-cc/compare/main...replay/upstream-notes>.
   It must show exactly four changed files (`constants/1d.md`, `16a.md`,
   `49a.md`, `70a.md`), with no asterisk removed.
2. Each new row sentence starts with "Independently replayed [RPL2026]". Find
   each number from it in the log named below. The digits in the sentence
   must match the beginning of the digits in the log.

   | Page and row | Number or statement in the new sentence | Log file in `replay/package` | Line to look for |
   | --- | --- | --- | --- |
   | 1d, STEPS2026 | "the same fraction" | `verification/1d/run_output.txt` | `equals the exact fraction recorded on the page: True` |
   | 1d, STEPS2026 | 1.46021728402287397507… | same | `= 1.4602172840228739750723381...` |
   | 1d, AER2026 | 1.45998904690538314495… and 1.45998904690538324315… | same | `= 1.4599890469053831449525924...` and `= 1.4599890469053832431503032...` |
   | 70a | 1.2019433684431505669948027797… | `verification/70a/run_output.txt` | the lines starting `method 1` and `method 2` |
   | 16a | 2.15622477064423579… | `verification/16a/run_output.txt` | `L >= [2.1562247706442357903 ...` |
   | 16a | (β+π)/π ≈ 1.82283 | `audit/logs/package/c16_readings.txt` | first line: `(beta + pi)/pi = 1.82282524967885` |
   | 49a, row 79 | 1.5675517557… | `verification/49a/run_output_syl2026.txt` | `rho^(1/60) = [1.5675517557581882198 ...` |
   | 49a, row 80 | 4349 sets; all 9520066 pairs | same | `has 4349 sets; equals data/B.txt` and `over all 9520066 pairs: none found` |
   | 49a, row 80 | 1.5678015201… | same | `rho^(1/17) = [1.5678015201687483405 ...` |

3. Click the link in each of the four new reference entries. Each must open a
   folder on GitHub at commit `c16fe56`, which holds the code and logs. The
   comparison page itself shows a different commit, `d79b144`: that is the
   commit containing the page edits. Both are correct.
4. Read the AI-use note on each page and make sure you are comfortable with
   it. It says the replay was done by Claude Opus 5.5 agents, audited by a
   second Claude session, revised after the audit, and not reviewed by a
   human mathematician.
5. Decide on the two placeholders:
   - The author line "presence1 (GitHub)" is how you would be credited.
     Replace it with your name if you prefer.
   - The reference key `[RPL2026]` can stay. If you change it, change all 14
     occurrences: 6 row sentences, 4 references and 4 notes.

   To edit, open the file on GitHub with the branch set to
   `replay/upstream-notes`, click the pencil icon, edit, and commit to that
   same branch.

**Done when** every number is found, every link opens, and you are happy with
the wording.

## Step 5 (optional, strongly recommended): ask a mathematician to look

**Why:** this is the one thing you cannot do yourself, and it is the main gap
in the work. Each item below is short, a page or two.

| Page | What to ask them to read | The question for them |
| --- | --- | --- |
| 70a | `verification/70a/README.md`, section "The reduction (re-derived)" | Is this argument right? |
| 49a | `verification/49a/README.md`, section "The XOR-gluing lemma (proof)" | Is this proof right? |
| 16a | `verification/16a/README.md`, section "Caveat on the definition" | Do you agree there are two readings, with these consequences? |

- If they find a problem, stop and have it looked into before submitting.
- If someone does review part of the work, the AI-use note is no longer
  accurate in saying no human mathematician reviewed it. Update the note to
  say exactly who read exactly what, with their permission.

## Step 6: Check whether upstream has moved (5 minutes)

**Why:** this work describes the upstream pages as they were on 3 November
2026. If those pages have changed since, the text may need adjusting first.
Other open pull requests touch the 1d and 16a pages.

Open the history of each of the four pages and look for changes after
3 November 2026:

- <https://github.com/teorth/optimizationproblems/commits/main/constants/1d.md>
- <https://github.com/teorth/optimizationproblems/commits/main/constants/16a.md>
- <https://github.com/teorth/optimizationproblems/commits/main/constants/49a.md>
- <https://github.com/teorth/optimizationproblems/commits/main/constants/70a.md>

**Done when:** none of the four has changed. If any has, ask for help before
continuing: the branch may need updating, and the statements re-checking.

## Step 7: Write down your own honest statement (15 minutes)

**Why:** the repository's AI policy requires that AI use be noted in the
submission text, and that "all references and other information provided by
the AI are reviewed and verified by the human contributor". Write your
answers to these questions in your own words. They go into your pull
request.

- Did you re-run the checks yourself? When, and on what computer? Did
  everything match? (Step 3)
- Did you check every number in the page edits against the logs, and did
  every link work? (Step 4)
- Did a mathematician read any part of it? If yes, who and what. If no, say
  that plainly.
- Do you have any connection to the authors of the certificates involved
  (steps-re, the AER2026 contributor, R. Pinho, maximusrufus, Sylla)? If you
  do, say so.
- Can you answer technical questions yourself, or will you pass them on to
  Claude? Either is acceptable if you say which.

## Step 8: Ask the maintainer about the 16a definition (30 minutes)

**Why:** the 16a page states its definition twice, and the two versions
disagree.

- **The first sentence** requires the inequality only for functions "with
  sufficiently large frequency ratio".
- **The second sentence** ("Equivalently, …") requires it for every allowed
  function.
- The bound 2.1562247706* is correct under the second reading, which is also
  how the original 2013 paper defines the constant. It would be false under
  the first.
- You are asking which reading is intended. You are **not** saying the page
  is wrong.

Before writing, check the source yourself. This needs reading, not
mathematics:

- Open the arXiv paper you supplied for the audit, arXiv:1012.2061v1
  (Bartuccelli, Deane and Zelik).
- **Theorem 3.8.** It should say the inequality holds "for all 2π × 2π-periodic
  functions u with zero mean", and define L as a maximum over δ ≥ 1 (formula
  (3.20)).
- **Page 4.** It should mention "L_∞ := (β+π)/π".

Then open a new issue at <https://github.com/teorth/optimizationproblems/issues/new>:

- A factual title, for example "C_16 (16a): which reading of the definition
  is intended?".
- Write the text yourself, following the checklist "Checklist: issue asking
  which reading of the 16a definition is intended" in `SUBMISSION_NOTES.md`,
  or start from the draft `DRAFT_ISSUE_16A.md`. Read every line of the draft,
  and change anything you are not sure is true.

**Done when** the issue is posted. Note its number for Step 9.

## Step 9: Open the pull request (30 to 60 minutes)

1. On GitHub, open your fork and switch to the branch
   `replay/upstream-notes`. Click **Contribute**, then **Open pull request**.
2. Check the header:
   - base repository `teorth/optimizationproblems`, base `main`;
   - head repository `presence1/optimizationproblems-cc`, compare
     `replay/upstream-notes`.
3. The "Files changed" tab must show only the four files.
4. Give it a factual title, for example "Record independent replays of six
   asterisked rows (asterisks kept)".
5. Write the description yourself, or start from the draft
   `DRAFT_PULL_REQUEST.md`. Check it against "Checklist: what the
   pull-request description must state" in `SUBMISSION_NOTES.md` box by box.
   Make sure your Step 7 statement is in it, and mention the 16a issue by its
   number (write "#" followed by the number GitHub gave the issue). Read
   every line of a draft before posting it.
6. If GitHub says the branch has conflicts, don't resolve them by hand unless
   you know git well. Ask for help.
7. Before clicking **Create pull request**, re-read "Do not claim" in
   `SUBMISSION_NOTES.md`. Do not ask for any asterisk to be removed.

**Done when** the pull request is open and its description covers every box.

## Step 10: After posting (ongoing)

- **Be patient.** Replies can take days or weeks; some similar pull requests
  have had no response yet. Don't ping repeatedly.
- **Asked to change wording?** Edit the files on `replay/upstream-notes`;
  the pull request updates by itself. Keep the links pointing at `c16fe56`.
- **Asked a question you can't answer?** Say so honestly. You can ask Claude
  to help draft a reply, but post only what you have read, understood and
  agree with, and say that you had AI help.
- **Someone reports an error?** Thank them and don't argue. Get it looked
  into, then correct or withdraw.
- **The maintainer answers the 16a question:**
  - If they mean the second ("Equivalently") reading, the 16a sentence stands.
    They may also fix the page's first sentence.
  - If they mean the first reading, the 16a bound would be false, and the 16a
    sentence must come out of your pull request. Ask for help with that.
- **Whatever happens to the pull request,** keep `replay/package` and the tag
  from Step 3.

## Step 11 (optional, later): confirm other people's replays

Other contributors have already posted replays of some of the same bounds:

- upstream pull request
  [teorth/optimizationproblems#292](https://github.com/teorth/optimizationproblems/pull/292)
  covers page 1c;
- upstream pull request
  [teorth/optimizationproblems#235](https://github.com/teorth/optimizationproblems/pull/235)
  covers page 49a, rows 74 to 78.

The repository needs someone unconnected to confirm each of those before
their asterisks can come off. Your replay covers the same rows, so you could
post a short confirmation on each, but only if all of these are true:

- you have no connection to those contributors or to the certificate
  authors;
- you have checked those rows' results yourself. Step 3 already re-ran
  them: see `run_1c.txt` and `run_49a.txt` in your `package_logs` folder,
  and `verification/1c/` and `verification/49a/` in the repository;
- you disclose the AI use and say exactly what you checked.

It is reasonable to wait until your own pull request has had a response.

## When to stop and ask for help

- Anything in Step 3 doesn't match, or a command fails.
- A number or link in Step 4 can't be found or doesn't open.
- One of the four pages changed upstream after 3 November 2026 (Step 6).
- GitHub reports conflicts on the pull request.
- Someone reports an error, or asks something you can't answer.

**How to get help:** start a new Claude Code session on this fork (branch
`replay/package`) and describe the problem, or ask a mathematically trained
person. These notes and `SUBMISSION_NOTES.md` give either of them the
context.

## Glossary

- **Constant, bound.** A constant is a specific number defined by a
  mathematical problem, often not known exactly. A bound says it is at least
  (lower bound) or at most (upper bound) some value.
- **Asterisk.** In this repository, a mark meaning "verification is currently
  minimal".
- **Certificate.** A data file that makes a bound checkable by computer, such
  as a list of numbers that defines a function.
- **Checker, replay.** A checker is a program that verifies a certificate. A
  replay is an independent re-run with your own checker.
- **Mutation test.** A test that deliberately breaks the data or a program, to
  make sure the checker then fails. A checker that cannot fail proves
  nothing.
- **Second party.** Someone other than the person asking, who confirms a
  replay. The repository needs one before an asterisk can be removed.
- **Pinned commit.** A link to one exact version of the code, identified by
  its commit hash (here `c16fe56…`), so it cannot change after you cite it.
- **SHA-256 hash.** A fingerprint of a file. If even one byte changes, the
  fingerprint changes completely.
- **Fork, branch, pull request, issue.** Your copy of the repository; a line
  of work inside it; a proposal to change the upstream repository; a
  discussion thread there.
