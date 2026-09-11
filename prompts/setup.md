# Setup

Paste this whole file into Claude Code, running from the workbench root, the
first time you open a fresh clone. It is written for the agent, not for you.
You will be asked questions; answering them is the work.

Nothing below runs by itself. Do it in order, and stop where it says stop.

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

## Stage 0: point the remote somewhere else

`origin` is the template. Anything pushed there goes to the template, not to
this workbench.

```bash
git remote -v
```

Ask the owner for their own repository URL, then:

```bash
git remote set-url origin <their-url>
git remote -v
```

If they have not made a repository yet, say so and leave `origin` alone rather
than inventing a URL. Record it as the first item in this session's report.

Confirm the four symlinks survived the clone. Git preserves them, a zip
download does not:

```bash
ls -l CLAUDE.md central-context/CLAUDE.md .claude/agents .claude/skills
```

All four must be symlinks. If any is a regular file, delete it and recreate it:
`ln -sf AGENTS.md CLAUDE.md`, `ln -sf AGENTS.md central-context/CLAUDE.md`,
`ln -sf ../agents .claude/agents`, `ln -sf ../skills .claude/skills`.

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
  Reads better; must be done in full or not at all.

Name both. Do not pick.

Do the same for "the practice", which is the placeholder for the business name
and appears in the same files.

**3. Rule 2, the writing standard.** Ask whether they have a writing standard
skill to install. If they do, install it under `skills/<name>/SKILL.md` and
name it in rule 2, then in the `skills:` frontmatter of `spec-writer.md`,
`scribe.md`, and `research-editor.md`. If they do not, delete the `> FILL:`
line and leave the plain-language rules that follow it standing. Say which you
did.

**4. Rule 3, interface and copy standards.** Same question for interface work
and client-facing copy. If they install any, name them in rule 3 and in
`agents/interface-builder.md`'s `skills:` frontmatter.

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

There are 14 in `agents/`, and every one of them is an example. Read
`agents/README.md` first, then work the two tables in it.

For each role, put one question to the owner: keep, edit, or delete. Give them
what they need to answer it in one line, not a summary of the whole file.

Three roles carry opinions that are almost certainly wrong for a new workbench,
so flag these specifically:

- `agents/interface-builder.md` has a block headed "The rules that will fail
  your work". Square corners, one accent under five percent of the area,
  hairlines not shadows. That is one practice's house style. Ask whether to
  keep it, replace it, or cut it to the accessibility rules alone, which are
  the only ones in the list that are not taste.
- `agents/test-writer.md` has a list of "things that have actually broken
  before". That history is not this codebase's. Ask whether to keep it as a
  starting heuristic or empty it.
- `agents/builder.md` has four rules about secrets, prompts, schema validation
  and `main`. They are sound defaults for a web codebase and meaningless for
  anything else. Ask what this owner actually builds.

Delete a role by deleting its file and its row in `agents/README.md`. Do not
leave a row pointing at a file that is gone.

After any change:

```bash
python3 scripts/check-roles.py
```

Zero failures before you move on. Claude Code skips a malformed role file
silently, so this script is the only thing that reports one.

---

## Stage 3: the research skills

Seven of the twelve installed skills describe how to research something. Two
of them have sections left deliberately empty, because they cannot be written
once for everybody.

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

**3. Roles and skills load.**

```bash
python3 scripts/check-roles.py
```

**4. Close the open item.** `AGENTS.md` carries
`open_items: workbench-not-specialised`. It closes by work, and this was the
work. Follow `wiki-open-items`: remove the item from the frontmatter, append
the close line to `central-context/log.md`, and leave nothing struck through.

**5. Log the decisions.** Anything the owner settled in stages 1 to 3 that a
future session would otherwise re-litigate earns a `DECISIONS.md` entry. The
`scribe` writes those. Hand it the question, the variants, and their answer.

**6. Commit.** Branch, commit, open a draft pull request. Never commit directly
to `main`. Root `AGENTS.md` carries the attribution lines.

---

## What you never do in this setup

- Fill a `> FILL:` marker with a plausible answer instead of asking.
- Write a filing deadline, a tax rate, a registry URL, or a rate benchmark from
  memory. Root rules 4 and 5 bind: retrieve it or record the gap.
- Pick one of two named variants on the owner's behalf. Root rule 8.
- Delete a role or a skill because it looked unused. Ask.
- Leave the placeholder pass half done.
