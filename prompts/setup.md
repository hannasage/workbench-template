# Setup

Paste this whole file into your harness at the start of a session, running from
the workbench root, the first time you open a fresh clone. A harness is the
program that runs the agent loop and reads these files. This file is written for
the agent, not for you. You will be asked questions, and answering them is the
work.

Nothing below runs by itself. Do it in order, and stop where it says stop.

The template ships no permission rules, so every approval prompt you see while
this runs is your own machine asking you. Answering one, or writing a rule that
stops it asking, is yours to decide.

---

## What you are doing

This repo is a clone of a template. It carries a working structure and a set of
example roles and skills that came out of one practice. The structure
transfers. The opinions do not: they name a business, a writing standard, a
buyer segment, and a jurisdiction that are not this owner's.

Your job is to replace every one of those with this owner's own, and to leave
nothing half-replaced. A workbench that says "the owner" in nine files and a
real name in two is worse than one that says "the owner" everywhere, because
the reader cannot tell which is deliberate.

The marker for everything unfilled is a line starting `> FILL:`, indented or
not. This is the check you run at the end:

```bash
grep -rn '^ *> FILL:' --include='*.md' .
```

An empty result is the finish line for stages 1 to 4. There are ten: eight in
`AGENTS.md`, one in `skills/prospect-research/SKILL.md`, one in
`skills/quarterly-planning/SKILL.md`.

---

## Stage 0: the harness, then the remote

**1. Prove the wiring.** Run this from the workbench root before anything
else:

```bash
python3 scripts/check-harness.py
```

`0 failure(s)` is the pass. The wiring for every supported harness is tracked
in git, so there is nothing to install: the symlinks each harness discovers
the tree through, and the files generated in each harness's own format, came
with the clone. A failure names the file and the fix. The one a fresh clone
can produce is a symlink checked out as a plain file, which happens on Windows
without `core.symlinks` and on any zip download; the message says what to run.
Do not continue with a failure standing.

**2. Which harness does the owner run?** The neutral core is what you cloned:
the entrypoint, the knowledge base, the skills, the roles, the scripts, and
this file. It names no harness. Every harness-specific path lives in one thin
adapter under `adapters/`, and `adapters/README.md` is the index: it lists the
adapters that exist and carries the support matrix, one row per harness. Read
it with the owner. Take the current list from that index and not from this
file, because this file goes stale first.

Two outcomes, and each one is a legitimate end to this step:

- **An adapter exists for their harness.** Its `README.md` opens with the
  steps for this harness: an optional plugin install, how to start the session,
  and how to confirm the roles and skills loaded. Walk them.
- **No adapter exists for their harness.** Adding one is one directory under
  `adapters/` with a manifest and a `README.md`, one row in the support
  matrix, and a run of `python3 scripts/sync-harness.py`, and
  `adapters/README.md` says how. Every path in it comes from that harness's
  own documentation, with the URL and the date you read it. Root rule 4 binds
  here.

Record the harness and the adapter path as the first item in this session's
report. Stage 5 logs it as a decision.

**3. Point the remote somewhere else.** `origin` is the template. Anything
pushed there goes to the template, not to this workbench.

```bash
git remote -v
```

Ask the owner for their own repository URL, then:

```bash
git remote set-url origin <their-url>
git remote -v
```

If they have not made a repository yet, say so and leave `origin` alone rather
than inventing a URL. Record it in this session's report.

---

## Stage 1: the identity and the always-on rules

Open `AGENTS.md`. It has eight `> FILL:` blocks. Work them in order, asking one
question at a time and waiting for the answer. Do not guess an answer from
context and do not batch the questions into one wall.

**1. What this workbench is for.** One paragraph, in the owner's words. What
work happens here, and what it is not for.

**2. Identity.** Who the agent acts as, and who owns the decisions. Get the
owner's name and what the business or team is called.

Then decide with them how the name enters the files. Two variants:

- **Keep "the owner" everywhere.** Every role and skill already reads this way.
  Nothing to change. Costs nothing, reads slightly impersonally.
- **Use their name everywhere.** One pass across `agents/` and `skills/`:
  `grep -rln 'the owner' --include='*.md' agents skills` finds every file.
  Reads better. It must be done in full or not at all.

Name both. Do not pick.

Do the same for "the practice", which is the placeholder for the business name
and appears in the same files.

**3. Rule 2, the writing standard.** Ask whether they have a writing standard
skill to install. If they do, install it under `skills/<name>/SKILL.md` and
name it in rule 2, then in the `skills:` frontmatter of `research-editor.md`.
If they do not, delete the `> FILL:` line and leave the plain-language rules
that follow it standing. Say which you did.

**4. Rule 3, interface and copy standards.** Same question for interface work
and client-facing copy. If they install any, name them in rule 3.

**5. Rule 9, the names that never appear in client-facing material.** Ask
directly: are there employers, clients, or partners that must not be named in
anything a client sees? List them, or write "None" and leave the rule
standing. Several skills cite rule 9 by number, so the rule stays either way.

**6. The routing table and the on-disk table.** Add a row per skill installed in
this stage, and a row per project repo the owner intends to nest here. For each
project repo, also add its directory to `.gitignore` and to the `dirs` list in
`skills/wiki-verify/SKILL.md`.

---

## Stage 2: read the agent roles

There are six in `agents/`, all research roles, and every one of them is an
example. Read `agents/README.md` first, then work the table in it.

For each role, put one question to the owner: keep, edit, or delete. Give them
what they need to answer it in one line, not a summary of the whole file.

Code and design work does not run through a role here. It runs through the
plugin named under "How work runs" in `AGENTS.md`, which the owner installs on
their harness following the adapter's `README.md`. If the owner does not build
software in this workbench, say so in that section instead of leaving a
pipeline nobody runs.

Delete a role by deleting its file and its row in `agents/README.md`. Do not
leave a row pointing at a file that is gone.

After any change:

```bash
python3 scripts/check-roles.py
python3 scripts/sync-harness.py
```

Zero failures from the first before you move on. A harness skips a malformed
role file in silence, so this script is the only thing that reports one. The
second regenerates the copy of each role that a harness reads in its own
format; a role you edited or deleted has one, and `python3
scripts/check-harness.py` fails until it is regenerated. Commit what it wrote.

`scripts/model-registry.txt` ships with no values in it, and no role file names a
model, so the model check never fires on the tree you cloned. You need the
registry only if you add a `model:` value to a role file. A value that is not
registered is reported as a question, not a failure, and the answer is either a
typo in the role file or one new line in the registry saying what the value is
and where you read it. Where an adapter maps each role to a model, that mapping
is the better home for an identifier and the registry stays empty.

---

## Stage 3: the research skills

Seven of the thirteen installed skills describe how to research something.
Two of them have sections left deliberately empty, because they cannot be
written once for everybody.

**`skills/prospect-research/SKILL.md`** has two: the buyer segment, and the
tier 1 records of authority for the jurisdiction. Ask the owner who they sell
to, where, and what researching one prospect establishes. Then find the actual
tools for that jurisdiction: the business registry, the property records
search, the licences portal, the trade regulator, the local licensing office.
Verify each URL loads before you write it down. Root rule 4 binds here as hard
as anywhere: a registry URL from memory is exactly the failure this skill
exists to prevent.

Also name the tier 2 services the segment actually uses. The generic list in
the file invites a guess.

**`skills/quarterly-planning/SKILL.md`** has the compliance calendar, which is
empty for the same reason. Do not fill it from memory under any circumstance.
Either research each row against the agency's own page and cite it, or leave
the rows reading "not checked" and open an item saying so. A confident wrong
filing deadline is the worst single thing this workbench could contain.

**`skills/competitor-research/SKILL.md`** and
**`skills/purchase-research/SKILL.md`** carry market figures and rate data from
the practice this template came from, each with its source and date. Those are
real citations, not placeholders, but they are now old and they describe one
market. Read them with the owner and decide per figure: keep with the date
visible, re-research, or cut.

If the owner does not do research runs at all, delete all seven research skills
and the six research roles, and cut the research rows from `agents/README.md`
and the routing table. That is a legitimate outcome, and a smaller workbench is
a better one.

---

## Stage 4: the first source

The wiki is empty, and an empty wiki teaches nothing. Ingest one real source
before you finish, so the owner has seen the loop run once.

Ask for the best single document they already have about how they work: an
engineering standard, a process doc, a client onboarding note. Then run
`wiki-ingest` on it, exactly as the skill says. That means: copy it to
`central-context/raw/sources/YYYY-MM-DD-slug.ext`, read the whole thing, write
the source page, write the entity and concept pages it touches, update
`wiki/overview.md` and `index.md`, and append the log line.

Then run `wiki-lint` and show them the result.

If they have nothing to ingest, say so plainly and skip this stage. Do not
invent a source.

---

## Stage 4A: prove the harness

This stage proves the harness recorded in stage 0 and records the result in
the support matrix in `adapters/README.md`. It carries a letter so that the
numbers of the stages around it do not move. It has two halves, and only the
first can run today.

**First, the wiring.** Run `python3 scripts/check-harness.py` again, now that
stages 1 to 3 have edited roles and skills. Zero failures. Then do the
confirmation the adapter's `README.md` gives for this harness: open a session
at the root and see the roles and the skills listed where that README says they
appear. Write the date into the `Wiring` column of that harness's row in the
support matrix, as `checked YYYY-MM-DD`, and into the "Wiring check" section
of the adapter's `README.md`. That column records a check of files and a
listing on screen, nothing more.

**Second, the behaviour. The test does not exist yet.**
`scripts/harness-acceptance.py` is named in `scripts/README.md` as not built,
and it is absent from the tree on 2026-09-12. So the four surface columns have
no command to run today. Do not improvise a substitute, and do not write a
result into a surface column from a reading of the files or from the listing
above. A cell that reads `not tested` is correct. A cell that reads `verified`
with no transcript behind it is a false claim.

What that half will be once the script lands: the test proves a harness by
checking four surfaces, which are the entrypoint loading without being asked,
one role dispatched, one skill loaded on demand, and one wiki operation
completed end to end. Each result goes into that harness's row in the support
matrix with the date of the run. A failing surface is a named finding in this
session's report and not a reason to stop the setup, because the workbench
still works on the surfaces that passed.

Write that half's commands from the script itself the first time you run it,
and add the script's row to the table in `scripts/README.md`.

---

## Stage 5: close out

**1. No markers left.**

```bash
grep -rn '^ *> FILL:' --include='*.md' .
```

Empty, or a named reason per remaining line.

**2. No half-replaced placeholders.**

```bash
grep -rn 'the owner\|the practice' --include='*.md' agents skills AGENTS.md | wc -l
```

The count is either zero, or it is every occurrence. Anything between means the
pass in stage 1 was partial. Finish it.

**3. Roles and skills load, and every harness copy is current.**

```bash
python3 scripts/check-roles.py
python3 scripts/check-harness.py
python3 scripts/check-open-items.py
```

Zero failures from each.

**4. Close the open item.** `AGENTS.md` carries
`open_items: workbench-not-specialised`. It closes by work, and this was the
work. Follow `wiki-open-items`: remove the item from the frontmatter, append
the close line to `central-context/log.md`, and leave nothing struck through.

**5. Log the decisions.** Anything the owner settled in stages 0 to 3 that a
future session would otherwise re-litigate earns a `DECISIONS.md` entry. The
harness from stage 0 is one of them. Write each entry with the question, the
variants, and their answer.

**6. The neutral core stayed neutral.** This is the last check before the commit,
and it has two halves.

First, no file in the neutral core names a harness. The neutral core is
`AGENTS.md`, `central-context/`, `skills/`, `agents/`, `scripts/`, `prompts/`,
`DECISIONS.md`, `README.md` and `.gitignore`. `SPEC.md` belongs to that list too,
and the template ships none, so nothing is missing while that file is absent.
`python3 scripts/check-harness.py`, which item 3 ran, scans those paths for
every pattern in `adapters/harness-names.txt` and reports each hit with its
file and line. One hit is a defect, whatever file it is in and whichever
harness it names. Fix it by moving the sentence into the adapter that owns it,
or by rewriting it to name no harness.

The `adapters/` path is not a harness name, and the scan strips it before it
matches. A neutral-core file may name that path, and any path below it, as
often as it needs to: telling a reader where the wiring lives is the opposite
of carrying the wiring. No count applies and no file is an exception.

Second, deleting the adapters directory leaves a workbench that still passes its
own checks. Run this against a copy. Never delete `adapters/` in the working
tree:

```bash
rm -rf /tmp/neutral-core-check
cp -R . /tmp/neutral-core-check
rm -rf /tmp/neutral-core-check/adapters
(cd /tmp/neutral-core-check && python3 scripts/check-roles.py && python3 scripts/check-harness.py)
rm -rf /tmp/neutral-core-check
```

Zero failures and zero questions from the first, and zero failures from the
second, which with no adapter left has nothing to declare and no pattern to
scan for. Anything else means the neutral core depends on
something an adapter carries, and the fix belongs in the neutral core: move the
dependency into the adapter, or drop it. A question names a `model:` value that
is not registered, and it counts against this check the same way a failure does.

**7. Commit.** Branch, commit, open a draft pull request. Never commit directly
to `main`. Root `AGENTS.md` carries the attribution lines.

---

## What you never do in this setup

- Fill a `> FILL:` marker with a plausible answer instead of asking.
- Write a filing deadline, a tax rate, a registry URL, or a rate benchmark from
  memory. Root rules 4 and 5 bind: retrieve it or record the gap.
- Write a result into the support matrix that no run produced.
- Pick one of two named variants on the owner's behalf. Root rule 8.
- Delete a role or a skill because it looked unused. Ask.
- Leave the placeholder pass half done.
