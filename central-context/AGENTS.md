# AGENTS.md: central-context

Repo entrypoint. It inherits `../CLAUDE.md` at the workbench root and adds what
is specific to this directory. On conflict, this file wins for wiki-specific
rules and the root file wins for universal gates and identity.

`CLAUDE.md` here is a symlink to this file.

This file is the schema. It is the third layer of the pattern below, and it is
meant to change. When a rule here stops matching how the wiki actually works,
edit this file in the same session and say what changed.

---

## What this is

An LLM wiki, in the pattern Andrej Karpathy published in April 2026.

A source enters once and never changes. An agent reads it, compiles what it
says into wiki pages, and keeps those pages current as later sources arrive.
Questions are answered from the wiki, not from the sources. Knowledge is
compiled once, not re-derived on every question.

The pattern has three layers, and this workbench adds a fourth:

| Layer | Directory | Who writes it |
|---|---|---|
| Raw sources, immutable | `raw/` | A person, or an agent acting on an explicit instruction to file a source |
| The wiki, maintained | `wiki/` | The agent, on every ingest, query, and lint |
| The schema | this file | A person and the agent together |
| Research deliverables, outside the pattern | `docs/` | The research roles, per the `research-operations` skill |

The skeleton below exists and holds no pages. Create a domain directory the
first time a page needs it, and not before.

### What this is not

This is a knowledge base. It holds what is known about subjects, compiled from
sources. It is not the operating manual: the root `AGENTS.md` carries that.

### What is not knowledge

`skills/`, `agents/`, and `scripts/` are code and configuration. They do not
compile into wiki pages and they do not belong in `raw/`. They move by copy.

**No code lives in this directory. Ever.** Not a script, not a hook, not a
plugin. A knowledge base that also ships code is two things wearing one name.
If a check here needs to be executable, it goes to `../scripts/` and this file
names it by path.

---

## Layout

```
central-context/
  AGENTS.md              this file, the schema
  CLAUDE.md              symlink to AGENTS.md
  index.md               the catalog, one line per page
  log.md                 append only, one line per operation
  raw/
    sources/             immutable documents
    assets/              images and attachments a source refers to
  docs/
    README.md            what a run folder holds
    <date>-<slug>/       one research run: brief, notes, check, deliverable
  wiki/
    overview.md          the map of active domains
    domains/<domain>/
      overview.md        what is known about this domain
      sources/           one page per source filed to this domain
      entities/          people, companies, products, places
      concepts/          topics, methods, theses
      queries/           an answer worth keeping
    global/
      entities/          an entity that two or more domains use
      concepts/          a concept that two or more domains use
    archive/             merged, superseded, or demoted pages
```

A domain is a subject the workbench keeps returning to. Create one when a third
source lands on the same subject, not on the first.

`docs/` is outside the other three layers: a deliverable is not a source until
someone files it to `raw/` through ingest, it is not a page, and lint does not
check it. Only the research roles in `../agents/` write there, in the formats
the `research-operations` skill sets. A file in `docs/` that a page cites is a
bug; the page cites the raw source the ingest created.

Move a page from `domains/` to `global/` when a second domain links to it. Do
not start a page in `global/`.

---

## Page schema

Every page in `wiki/` carries YAML frontmatter:

```yaml
---
type: overview | source | entity | concept | query
status: draft | current | stale | archived
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [raw/sources/<file>]
---
```

`sources` lists every raw file the page draws on. An `overview` page may state
an empty list, because it draws on the pages below it. Every other type names
at least one source.

The body is:

1. A summary paragraph. Two or three sentences. What a reader needs if they
   read nothing else.
2. `## Key points`. What is known, as a list.
3. `## Evidence`. The claim, then where it came from. Cite the raw file by
   path.
4. `## Links`. `[[wikilinks]]` to related pages.
5. `## Open questions`. What is not known. Omit the section only when there is
   nothing to say.

A `source` page adds three lines above `## Key points`: the ingest date, the
kind of source, and the pages this ingest changed.

One page holds one subject. When a page covers two, split it.

---

## Open items schema

An open item is a question nobody has settled, written where the work it blocks
will find it. It lives in YAML frontmatter under `open_items`. This section is
the authority; the `wiki-open-items` and `wiki-verify` skills run it.

A context file carries them: any `AGENTS.md`, any `SKILL.md`, any `SPEC.md`.
`CLAUDE.md` is a symlink to `AGENTS.md`, so it inherits. A wiki page states its
own unknowns in `## Open questions` in the body instead.

```yaml
---
open_items:
  - id: kebab-case-slug
    opened: YYYY-MM-DD
    checked: YYYY-MM-DD
    triggers: [short phrase, short phrase]
    asks: One question the owner answers to close this. Empty when no decision is owed.
    item: >
      One paragraph. What is unresolved, why, and what closing it would take.
---
```

| Field | Holds |
|---|---|
| `id` | Lowercase, hyphens, unique in the file. Never reused after a close. |
| `opened` | The date the item was first written down. |
| `checked` | The date someone last verified the item. Equals `opened` when nobody has rechecked. |
| `triggers` | Short phrases an agent matches against the task in hand. This is what makes an item surface during unrelated work. |
| `asks` | The question the owner answers, one sentence, in their words. Empty when the item closes by doing work. |
| `item` | One self-contained paragraph. It reads correctly with no other file open. |

Five rules:

1. Frontmatter holds open items only. A closed item leaves `open_items`. It
   does not stay behind struck through.
2. A close leaves a record: one line in `log.md`. A decision from the owner
   also earns a `DECISIONS.md` entry, which the `scribe` writes.
3. `checked` moves when the item is verified, not when the file is edited. An
   old `checked` date is a claim nobody has tested.
4. An item is written only after its claim is checked against disk, git, or a
   source. Root rule 4 binds.
5. One item lives in one file, the file whose work it blocks. It is never
   copied into a second file.

---

## The five operations

Ingest, query and lint came with the pattern. Verify and open items are this
workbench's own, and they exist because lint checks the wiki against itself and
cannot catch a claim that is simply old.

### Ingest

Run when a new file lands in `raw/`.

1. Read the source. Do not edit it.
2. Say what it is and which domain it belongs to. If no domain fits, say so and
   stop.
3. Write the `source` page under that domain.
4. Update every entity and concept page the source touches. Create the ones
   that do not exist.
5. Update the domain `overview.md`, then `wiki/overview.md` if the map changed.
6. Add a line to `index.md` for every page created.
7. Append one line to `log.md`.

When a source contradicts a page, do not overwrite the page silently. Write the
correction, dated, saying what the page used to claim and what replaced it. The
audit trail is the point.

### Query

Run when someone asks a question.

1. Read `index.md`. Open the pages it points to.
2. Answer from the wiki. Cite each page by path.
3. If the wiki does not hold the answer, say so. Do not answer from the raw
   sources without saying that is what you did, and do not answer from memory.
4. If the answer took real work and will be asked again, save it under
   `queries/` and add it to `index.md`.
5. Append one line to `log.md`.

### Lint

Run before every commit, and whenever the wiki feels wrong.

Check six things:

- Every `[[wikilink]]` resolves to exactly one page.
- Every page carries the frontmatter its `type` requires.
- Every `sources` entry names a file that exists in `raw/`.
- No two pages cover the same subject.
- No page contradicts another page.
- Every page in `index.md` exists, and every page exists in `index.md`.

Report what fails. Fix only what the check flagged.

There is no build here and no test suite. Lint is the gate. When it grows past
what a person can run by reading, it becomes a script at `../scripts/` and this
file names it. No code lives in this directory, so the script lives there and
never here.

### Verify

Run on a cadence, and before a research run or a plan embeds a fact from a
context file.

Lint asks whether the wiki is consistent with itself. Verify asks whether it is
still true. Five mechanical checks find old `checked` dates, prose the disk
contradicts, a raw source no page cites, a question the sources already
answered, and a draft that never moved. A reading pass then re-tests each one
against the disk, git, or the source that page cites.

Verify moves `checked` and `updated` dates and writes dated corrections. It
never edits `raw/`, and it never closes an item that `asks` a question of the
owner.

### Open items

Run at the start of a task, and whenever work settles or exposes a question.

1. List every item across the context files.
2. Match `triggers` against the task in hand. When in doubt, a match.
3. For a match with an `asks`, put the question to the owner with named
   variants, per root rule 8, and stop that thread. Never pick a variant for
   them.
4. For a match with no `asks`, the item closes by work. Do that work, or say
   the item still blocks.
5. Open an item only after testing its claim. Close one by removing it.

Every open and every close appends a line to `log.md`.

---

## The two flat files

`index.md` is the catalog. One line per page, grouped by domain, each line a
wikilink and a summary of ten words or fewer. It is read first on every query,
so it stays short. A line that needs a sentence belongs on the page, not here.

A domain section reads like this, with double square brackets around each page
name:

```
## engineering

- [ [branch-discipline] ] never commit to main, branch, draft pull request
- [ [the-gates] ] typecheck, lint, test, build, all zero before commit
```

The spaces inside the brackets are this example's only. A real line has none,
or lint check 1 counts it as a broken link on a page that does not exist.

`log.md` is append only. One line per operation, newest at the bottom:

```
2026-09-10 · ingest · raw/sources/<file> · created 3, updated 2
2026-09-10 · query · <the question, short> · answered from 4 pages
2026-09-10 · lint · 2 broken links, fixed
2026-09-11 · verify · 3 items rechecked · 1 correction, 2 dates moved
2026-09-11 · open-items · AGENTS.md#some-item · opened
```

Never edit a past line. A mistake earns a new line that corrects it.

---

## Rules

1. **Never modify `raw/`.** A source is a record of what someone said or wrote.
   Fix nothing in it, not a typo, not a broken link. If a source is wrong, the
   wiki page says so.
2. **Cite everything.** A claim on a wiki page names the raw file it came from.
   A claim with no source is an open question, not a key point.
3. **Missing data is a finding.** Say a figure does not exist in the sources.
   Never estimate into a gap.
4. **Separate fact from reading.** A key point is what the source says. An
   interpretation is labelled as one.
5. **Cross link hard.** A page with no links is a page nobody will find.
6. **Keep the active wiki smaller than the archive.** Archive a page rather
   than letting two half pages stand.
