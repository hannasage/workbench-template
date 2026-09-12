---
type: index
updated: 2026-09-12
---

# agents

Role definitions for the delivery pipeline and the research team. One file per
role: YAML frontmatter carrying `name` and `description`, then the system prompt
as the body. A role is one job with one output. The frontmatter carries no tool
list and no model, because no two harnesses name those the same way. A harness
is the program that runs the agent loop, and each one gets those values from its
own adapter.

**Every role in this folder is an example.** They came out of one working
practice and they carry that practice's opinions about testing, about what a
brief holds, and about what a research note may cite. The shape is what
transfers: one role, one job, one thing it writes, and a `Context findings`
section that keeps it out of the knowledge base. Read the ones you will use,
change what does not fit, and delete the ones you will not. A role you kept
without reading is a role that will make decisions you did not agree to.
`../prompts/setup.md` walks the first pass.

These files are the one copy of every role. Whatever a harness needs to find
them, or to run them in its own format, lives in that harness's adapter. The
routing table in `../AGENTS.md` has the row that leads there. Nothing in this
folder is generated, and nothing here is a copy of anything else.

How the roles fit together, and where a human still has to touch the work,
belongs on a page in your own wiki. The practice this came from keeps it at
`../central-context/wiki/domains/engineering/concepts/delivery-pipeline.md`.
Until you write it, the tables below are the map.

These files carry the role schema, not the wiki page schema, so `wiki-lint` does
not check them. Links that resolve still bind.

`../scripts/check-roles.py` checks their frontmatter: a name that is lowercase
and hyphens and matches the filename, a description, that every skill named
exists, and that a `model:` value, where a role names one, is listed in
`../scripts/model-registry.txt`. No role here names a model, so the model check
never fires on the shipped tree; it is there for a cloner who pins one. An
unregistered value is reported as a question, not an error, because the script
cannot tell a typo from a model nobody has registered yet. The registry ships
with no values in it on purpose, which is a different thing from a registry that
is not there: a file the script cannot read is reported as a failure. A harness
skips a malformed role file and reports nothing, so run the script before
committing a role.

A harness that dispatches roles usually reads them when the session starts, so a
role added mid-session is not available until the next one. A harness that
dispatches nothing still runs the whole pipeline in the main session: read the
role file yourself and follow it in turn. No rule lives only in a role file.

## Reporting to the context

No role writes the knowledge base. A role that finds a fact the context states
differently, a gap the context should have covered, or an open item its work
just made relevant reports it in one line that starts with `Context:` and
changes nothing. The main session decides what the practice now knows and makes
the edit.

The reason is judgement, not permission. A role sees one task. It cannot tell
whether a fact it found changes one page, three pages, or nothing. The main
session can. One writer at a time also keeps two agents out of the same file.

Context files are the container `AGENTS.md`, each repo's `AGENTS.md`, each
`SKILL.md`, each `SPEC.md`, every page under `../central-context/wiki/`, and the
`open_items` frontmatter in any of them.

The `scribe` is the one exception, and a narrow one. It writes `DECISIONS.md`
and the one-line entry in `central-context/log.md`, because both are append-only
records of what happened in one run. It does not edit `AGENTS.md`, a
`SKILL.md`, a wiki page, or an `open_items` block. Those state what is true now,
which is the judgement the main session keeps.

Every role file carries a `Context findings` section that says what counts as
one for that role.

## The roles

| File | Does | Writes |
|---|---|---|
| `spec-writer.md` | Turns a request into acceptance criteria and named open questions | `SPEC.md` |
| `planner.md` | Breaks an approved spec into an ordered task list | Nothing |
| `builder.md` | Implements one task | Source |
| `interface-builder.md` | Implements one task that a person will look at | Source, styles |
| `test-writer.md` | Writes tests against the criteria, not against the code | Tests |
| `gatekeeper.md` | Runs the gates and fixes only what they flag | Source, narrowly |
| `critic.md` | Reviews the diff against the house rules | Nothing |
| `scribe.md` | Writes the decision entry, the context log line and the pull request | Logs, the PR |

## The research team

Six roles that turn a question into a document under `central-context/docs/`.
The main session orchestrates, as it does for the delivery pipeline. The
stages, the folder layout, and the file formats are in the
`research-operations` skill. What a role may cite is in `research-sourcing`.

| File | Does | Writes |
|---|---|---|
| `research-lead.md` | Turns a request into a brief with checkable questions, one specialist each, and questions for the owner | `BRIEF.md` |
| `market-analyst.md` | Researches one market, competitor, rate, or planning question | `notes/market-analyst-*.md` |
| `procurement-analyst.md` | Researches one purchase: requirements, candidates, evidence, cost model | `notes/procurement-analyst-*.md` |
| `prospect-analyst.md` | Researches one prospect: entity, vertical, public image, web presence | `notes/prospect-analyst-*.md` |
| `fact-checker.md` | Re-retrieves every registered fact and gives a verdict | `CHECK.md` |
| `research-editor.md` | Writes the deliverable from the notes and the check, adds no fact | The deliverable |

The specialists run in parallel, each with only its own question. Stage 2, the
owner answering the brief's questions, is skipped only when there are none. The
`scribe` still writes `DECISIONS.md` when the owner decides something from a
deliverable; research roles never write there.

The three specialists each load a subject skill that says what to look for:
`competitor-research` and `quarterly-planning` for the market analyst,
`purchase-research` for procurement, `prospect-research` and `prospect-dossier`
for prospects. Those skills ship with sections left deliberately empty, because
a buyer segment and a compliance calendar cannot be written once for everybody.
Fill them before the first real run. `../prompts/setup.md` says which.
