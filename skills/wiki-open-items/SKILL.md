---
name: wiki-open-items
description: "Runs the open_items frontmatter across every context file: lists the items, matches their triggers to the work in hand, puts the asks question to the owner with named variants, and opens or closes items with a log line. Use at the start of any task, when work exposes a question nobody has settled, when the owner answers one, and when work closes one. Covers the item shape, the trigger match, the ask, the close, and what the log records. Route re-testing an old item against the disk to wiki-verify, and page health to wiki-lint."
---

# Wiki Open Items

An open item is a question nobody has settled, or a claim that work is blocked,
written where the work it blocks will find it. It lives in YAML frontmatter
under `open_items`, in one file, in the shape the schema sets. This skill runs
that shape: open, match, ask, close.

The failure this skill exists for is the quiet one. A question sits in a file.
The work that answers it happens in another session. Nobody connects the
two, and the item is still open a month after it was answerable. The
`triggers` field is the connection, and this skill reads it.

The skill never answers the owner's question for them. It puts the question, names
the variants, and stops.

## Read this first

`central-context/AGENTS.md` holds the open items schema, in the section of that
name. It is the authority on the shape this skill matches, opens and closes, so
read it before touching an `open_items` block. When this skill and that file
disagree, that file wins and this skill gets corrected.

That section defines the six fields, `id`, `opened`, `checked`, `triggers`,
`asks` and `item`, and the five rules that bind this skill in full: frontmatter
holds open items only, a close leaves a record, `checked` moves on verification
only, verify before writing, one item in one file. This skill states none of the
six and none of the five on its own authority. Without that file open, it cannot
tell a well formed item from a malformed one.

A context file is any `AGENTS.md`, any `SKILL.md`, any `SPEC.md`, and any page
under `central-context/wiki/`.

The main session opens and closes items. A role that finds an item its work
made relevant, or a question nobody has settled, reports it in one `Context:`
line, as `agents/README.md` says, and changes nothing. Step 2 of this skill,
the trigger match, is the one step a role runs for itself before it starts.

## When to run

- At the start of any task. Match triggers before the work starts, not after.
- When work exposes a question that nobody has settled. Open an item.
- When the owner answers an `asks` question. Close the item.
- At the end of a session that did the work an item names. Close it by work.

## Procedure

**1. List every item.**

Run from the container root. One line per item: file, id, dates, triggers.

```bash
grep -rl --include='*.md' '^open_items:' AGENTS.md central-context skills agents 2>/dev/null | while read -r f; do
  awk -v F="$f" '
    /^---$/ { fm++; if (fm==2) exit; next }
    fm==1 && /^open_items:/ { inb=1; next }
    fm==1 && inb && /^[^ ]/ { inb=0 }
    inb && /^  - id:/       { id=$3 }
    inb && /^    opened:/   { op=$2 }
    inb && /^    checked:/  { ck=$2 }
    inb && /^    triggers:/ { sub(/^    triggers: */,""); print F " · " id " · opened " op " · checked " ck " · " $0 }
  ' "$f"
done
```

**2. Match triggers to the task in hand.**

This needs reading, not grep. A trigger is a short noun phrase such as `commit
to the root repo` or `any new brand artifact`. Read the task, read every
trigger, and name the items that match. When in doubt, a match. Reading one
paragraph costs less than missing an item.

For each match, read the `item` paragraph. It is self-contained on purpose.

**3. Act on each match.**

- `asks` is empty. The item closes by doing work. If this task does that work,
  do it and close the item at step 5. If it does not, the item still blocks:
  say so in the report and carry on.
- `asks` is not empty. A decision is owed. Put the question to the owner in their
  words, one sentence, then name the variants the `item` paragraph supports.
  Container rule 8 binds: named variants, never one option presented as
  settled. Then stop that thread until they answer. Do not close the item, do
  not pick a variant, and do not do work that assumes one.

**4. Open an item.**

Open one when the work exposes a question that nobody has settled and no item
holds it. Before writing, test the claim against the disk, git, or a source.
Schema rule 4 binds: an item is stated only after its claim is checked. An item
that states a false blocker costs every later session a read.

Write it in the file whose work it blocks. One file, never two. `opened` and
`checked` are both today. `triggers` names the work that makes it relevant.
`asks` is one sentence in the owner's words, or an empty string when no decision is
owed. `item` is one paragraph that reads correctly with no other file open.

Then test the shape:

```bash
grep -rl --include='*.md' '^open_items:' AGENTS.md central-context skills agents 2>/dev/null | while read -r f; do
  awk -v F="$f" '
    /^---$/ { fm++; if (fm==2) exit; next }
    fm==1 && /^open_items:/ { inb=1; next }
    fm==1 && inb && /^[^ ]/ { inb=0 }
    inb && /^  - id:/       { id=$3; seen[id]++; if (seen[id]>1) print F " · " id " · id used twice" }
    inb && /^    opened:/   { op=$2 }
    inb && /^    checked:/  { if ($2 < op) print F " · " id " · checked " $2 " before opened " op }
  ' "$f"
done
```

An empty result is a pass. Append one line to `central-context/log.md`:

```
YYYY-MM-DD · open-items · <file>#<id> · opened
```

**5. Close an item.**

Close one when the work is done, when the owner answered, or when `wiki-verify`
found that the claim no longer holds. Remove the item from `open_items`. It
does not stay struck through and it does not move to a closed list. Never reuse
the `id`.

If the close changes a fact in the file's body, edit the body in the same
session. The entrypoint said the root repo had no remote in its open items and
in its prose. Closing the item and leaving the prose is the failure this skill
was written after.

Make sure that the id is gone:

```bash
grep -rn --include='*.md' 'id: <the-id>' AGENTS.md central-context skills agents
```

Append one line to `central-context/log.md`:

```
YYYY-MM-DD · open-items · <file>#<id> · closed by work: <what was done>
YYYY-MM-DD · open-items · <file>#<id> · closed by the owner: <what they chose>
```

When the owner decided, the main session writes the `DECISIONS.md` entry. Give
it the question, the variants, and their answer. A role never writes that
entry.

**6. Wiki pages.**

A wiki page carries `## Open questions` in its body, as the page schema
requires. Schema rule 1 still applies: a question a source answers is removed
in the ingest that answers it, and the dated correction on the page is the
record. Whether a wiki page also carries `open_items` in frontmatter is not
settled. Until it is, this skill reads both.

## Stop and ask

- An item with `asks` set. It closes on the owner's answer and on nothing else.
- The owner's answer contradicts a page. Put the page and the answer side by side
  and stop. The page is corrected by an ingest, not by an answer in chat.
- Two items in two files hold one question. Schema rule 5. Variants: keep the
  one in the file whose work it blocks, or merge into the older one. Name which.
- The item to open has no file whose work it blocks. Variants: the root
  `AGENTS.md`, or the nearest domain overview in the wiki. Name which.

## Report

Say which items matched, which were put to the owner and are waiting, which were
opened, which were closed and how, and which still block the work. One line
each. No item is closed in the report that is not closed on disk.

## Provenance

First-party to the practice this template came from, written 2026-09-11. The
published record on tracking open questions in an LLM wiki is thin.
Karpathy's gist (2026-04-04) has lint find data gaps and fill them by search,
which is the opposite of tracking them. No first-hand account found states a
method for connecting an open question to the work that answers it. The
`triggers` field and this skill are this practice's own.

## Not this skill

- Re-testing an old item or an old page against the disk, git, or a source,
  and moving `checked`. Use `wiki-verify`.
- A broken wikilink, missing frontmatter, a duplicate subject, or two pages
  that contradict each other. Use `wiki-lint`.
- Filing the source that answers a question. Use `wiki-ingest`.
- Answering a question from the wiki. Use `wiki-query`.
- Writing the `DECISIONS.md` entry as a role. The main session does that.
