---
type: log
updated: 2026-09-11
---
# DECISIONS.md

Append-only decision log. Newest entries at the bottom. Entries are never
edited or deleted. A reversal earns a new entry that supersedes the old one by
date.

The main session writes here, when the owner decides something. No role
does. The rule for what belongs here is in `AGENTS.md`.

An entry is warranted when a choice was settled that a future session would
otherwise re-litigate. Routine work does not earn one. An open question does
not either: that belongs in an `open_items` frontmatter block, which the main
session writes.

Format:

```
### YYYY-MM-DD · Short title
**Decided:** what was chosen, in one sentence.
**Instead of:** the alternatives that were on the table.
**Because:** the reasoning, in one or two sentences.
**Affects:** files or systems this changes.
```

---

### 2026-09-11 · The workbench starts from the template
**Decided:** This workbench is a clone of `workbench-template`, and the
template's example roles and skills stand until someone reads and replaces
them.
**Instead of:** writing the structure from scratch, or deleting the examples
before reading them.
**Because:** the shape is worth keeping and the opinions inside the examples
are not yet this workbench's. Keeping them visible makes the difference
findable. `AGENTS.md#workbench-not-specialised` tracks the pass that resolves
it.
**Affects:** `agents/`, `skills/`, `AGENTS.md`, `central-context/AGENTS.md`.
