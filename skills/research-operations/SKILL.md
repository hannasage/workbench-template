---
name: research-operations
description: "The operating procedure for the business research team. Use when the owner asks for research on a market, a competitor set, a purchase, a prospect, or a quarterly plan, and the work will be split across the research roles in agents/. Covers the six stages from request to filed deliverable, the folder layout under central-context/docs/, the BRIEF.md, notes, CHECK.md and deliverable formats, the CEO escalation protocol, and the rules that never bend. Route what may be cited to research-sourcing, and the subject procedures to competitor-research, quarterly-planning, purchase-research, and prospect-dossier."
---

# Research operations

The research team is the delivery pipeline's sibling. The delivery pipeline
turns a request into merged code. The research team turns a question into a
document the owner can act on, with every fact traceable to a source they can open.

Read `AGENTS.md` at the container root first. Its always-on rules bind every
stage below. Rule 10 binds each role's report to the session. It never binds a
deliverable.

## When to activate

Activate when a request needs facts the practice does not hold, and the answer
will be read more than once: a comparison, a dossier, a plan, a recommendation.

Do not activate for a question the wiki already answers. Run `wiki-query`
first. A research run that repeats what the wiki holds wastes a session and
produces a second home for a fact that already has one.

## The stages

The main session orchestrates. There is no orchestrator role, for the same
reason the delivery pipeline has none: a role that reads everyone's task starts
doing everyone's task.

| Stage | Role | Writes | Ends with |
|---|---|---|---|
| 1 | `research-lead` | `BRIEF.md` | Questions, assignments, and questions for the owner |
| 2 | The owner | Answers | An approved brief, or a changed ask |
| 3 | `market-analyst`, `procurement-analyst`, `prospect-analyst` | `notes/<role>-<slug>.md` | One notes file per assignment, with a fact register |
| 4 | `fact-checker` | `CHECK.md` | Every registered fact re-retrieved and marked |
| 5 | `research-editor` | The deliverable | One document, pure content, decisions named |
| 6 | The owner | Nothing, or an ingest | A decision, and optionally a source filed to the wiki |

Stage 3 runs the specialists in parallel. Each one receives only its own
section of the brief. Stages 4 and 5 run once per deliverable.

Stage 2 is skipped only when the brief carries no questions for the owner. A brief
with an open question is not ready, and the main session says so instead of
guessing the answer.

## Where the work lives

```
central-context/docs/
  README.md
  <YYYY-MM-DD>-<slug>/
    BRIEF.md                the research-lead's plan
    notes/
      <role>-<slug>.md      one per specialist assignment
    CHECK.md                the fact-checker's report
    <deliverable>.md        the research-editor's document
    BLOCKED.md              only while a role is blocked
```

The date is the day the brief was written. The slug is three words or fewer,
lowercase, hyphens. One folder per research run. A follow-up run on the same
subject gets its own dated folder and its brief names the earlier one.

`docs/` is not the wiki. Nothing in it is a wiki page, nothing in it is
linted as one, and nothing in it is a source until the owner files it through
`wiki-ingest`. `central-context/AGENTS.md` carries this rule in its layout
section.

## BRIEF.md

The research-lead writes it. Four parts and nothing else.

```markdown
---
type: brief
status: draft | approved
created: YYYY-MM-DD
requested_by: <name>
deliverable: comparison | dossier | plan | recommendation | report
---

# <Title>

## The ask
One paragraph, in the owner's terms.

## Questions
1. <A question with a checkable answer.> Assigned: <role>. Skill: <skill>.
2. ...

## Out of scope
What a reader might assume is included and is not.

## Questions for the owner
1. <The decision.> Options: (a) ..., (b) ..., (c) ...
```

A question in the `Questions` list is answerable by retrieval. "What do
fractional CTOs charge" is a question. "Should we charge that" is a decision,
and it goes under `Questions for the owner`.

## Notes files

Each specialist writes one file per assignment. It is a working document, not
a deliverable, so rule 7 does not bind it: process notes, dead ends, and
retrieval failures belong here.

```markdown
---
type: notes
role: <role>
brief: ../BRIEF.md
question: <the question number from the brief>
created: YYYY-MM-DD
---

# <Question, restated>

## Findings
Numbered. Each finding is one claim and a source line in the form
`research-sourcing` specifies.

## Fact register
A YAML block, one entry per fact that may reach the deliverable, in the
schema `research-sourcing` specifies.

## Gaps
Every figure or answer looked for and not found. Retrieval failures by URL.

## Disagreements
Where sources conflict, and on what.

## For the owner
Decisions this research surfaced, each with named options.
```

## CHECK.md

The fact-checker writes it and writes nothing else. One line per registered
fact.

```
| # | Claim | Source | Verdict | Note |
```

Verdicts: `confirmed` (the source says this, retrieved again this session),
`changed` (the source now says something else, the note says what), `failed`
(the source could not be retrieved, the note says the error), `unsupported`
(the source does not say this). Then one line: the count per verdict, and
whether the deliverable may proceed. A `failed` or `unsupported` fact does not
proceed. It becomes a gap.

## The deliverable

The research-editor writes it from the notes and the check, and only from
those. The editor adds no fact, and it drops every fact the check did not
confirm.

```markdown
---
type: comparison | dossier | plan | recommendation | report
status: draft | checked | final
created: YYYY-MM-DD
updated: YYYY-MM-DD
brief: BRIEF.md
check: CHECK.md
audience: owner | client
---

# <Title>

## Summary
Two or three sentences. What the reader needs if they read nothing else.

## Findings
The body. Structure follows the subject skill's output section.

## Decisions for the owner
Numbered. Each one names the options and what each option costs or risks.
Nothing here is decided.

## Gaps
What was looked for and does not exist publicly, or could not be retrieved.

## Sources
Every fact, its source, and the date it was retrieved or observed.
```

Rule 7 holds: no process notes, no narrative of how the research went, no
caveats about the team's own effort. `Decisions for the owner` and `Gaps` are
content, not caveats. Rules 5, 6, and 8 require them.

A deliverable with `audience: client` also carries the rules in
`prospect-dossier`, including rule 9: it names no name that rule 9 withholds.

## Escalation

Every role raises concerns to the owner. None resolves them.

A concern is any of these:

- A fact the deliverable depends on that could not be retrieved or has no
  public source.
- Two credible sources that disagree in a way that changes the answer.
- A choice the brief left open that a role would otherwise have to make.
- A cost, legal, tax, or contractual item that binds the practice.
- A finding the requester will not like. Rule 6 binds hardest here.

Raise it in two places: the `For the owner` section of the notes file, and the
role's report to the session. The research-editor collects every one into
`Decisions for the owner`. A concern raised in a notes file and absent from the
deliverable is an editing defect.

A role that cannot proceed follows the self-correction protocol from the
delivery pipeline: three attempts at the same failure, then `BLOCKED.md` in the
run folder with what it was doing, what it tried, the exact error, and its
reading of the cause. Then it stops.

## Sizing

One question per specialist per session. A question that needs more than one
session is two questions, and the research-lead splits it. Two questions that
always draw on the same sources are one question, and the research-lead merges
them.

A run with more than six questions is two runs.

## After the deliverable

The owner reads it and decides. The team does nothing further unless they ask.

If the deliverable holds facts the practice will need again, the owner may file it
through `wiki-ingest`. It enters `raw/` as a synthesis, so every claim on the
resulting wiki pages is attributed to the research run, not to the underlying
sources. A page that needs the underlying source cites the deliverable's
`Sources` section and the owner files that source separately.

A decision the owner makes from a deliverable goes to `DECISIONS.md` by the
`scribe`, in the delivery pipeline's format. Research roles never write there.

## The rules that never bend

- No role answers a question raised for the owner.
- No fact reaches a deliverable from memory. Rule 4.
- A missing figure is written down as missing. Rule 5.
- The `fact-checker` changes nothing but `CHECK.md`.
- The `research-editor` adds no fact and keeps no unconfirmed one.
- No role writes to `wiki/`, `raw/`, `index.md`, `log.md`, or `DECISIONS.md`.
- A client-facing deliverable names no name that rule 9 withholds.
