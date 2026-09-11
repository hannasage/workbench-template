---
name: prospect-research
description: "Source tiers and exclusions for facts about a prospect in the practice's target segment. Use when researching a named business that the practice might sell to. Covers the tier 1 records of authority, the tier 2 dated observations the buyer segment leaves, the tier 3 leads, the prospect-specific exclusions, and the biases to avoid. The four gates, the fact register, and the gap outcome live in research-sourcing; what to look for and the dossier layout live in prospect-dossier. Fill in the segment and the tier 1 table before first use."
---

# Prospect Research

This skill decides which sources settle a question about a prospect.
`research-sourcing` carries the four gates, the three outcomes, and the fact
register that every research subject shares. `prospect-dossier` decides what to
look for and how the dossier and the handoff document are laid out. Brand
tokens, type steps, and component rules come from the workbench's brand skill,
if one is installed. Read `research-sourcing` first, because a dossier built
on an unadmitted fact is worse than no dossier.

## Fill this in first

> FILL: the segment paragraph below, and the tier 1 table further down.

Two sections below are empty on purpose, because they are the only two that
cannot be written once for everybody: your buyer segment, and the tier 1
records that cover it. A prospect skill with someone else's segment in it is
worse than none, because it reads as settled. `prompts/setup.md` covers both.

**The segment.** One paragraph. Who the practice sells to, where, and what
"researching a prospect" establishes about one of them. Be narrow. "Businesses
that need software" is not a segment; "owner-operated specialty retail in five
named counties" is.

> Example, from the practice this template came from: the practice sells to
> owner-operated specialty retail in five named counties. Research means
> establishing whether a named business is registered, licensed, open, and
> underserved. It does not mean surveying a field.

## When to activate

Activate when a task will put a fact in front of a person outside this
practice:

- A prospect dossier or a comparison artifact
- A brief, a pitch, or a proposal
- Client-facing site copy that states a figure
- Any answer where "I think it is about..." would be a wrong answer

Do not activate for internal notes, wiki work, or code. Those carry no
citation burden.

## The controlling rule

`AGENTS.md` rules 4 and 5, as `research-sourcing` states them: nothing from
memory, and a missing figure is a finding. For a prospect that means a
business name, an address, an owner, a licence number, a review count, a
price, and a founding year are each retrieved before they are written, and
each one that is not found is written down as not found.

## Source tiers

### Tier 1: records of authority

A tier 1 source is a government or operator record. It settles a question on
its own. Verify the current address by search before use, because these tools
move and go offline.

Fill the table for your jurisdiction. One row per tool, naming the tool and
exactly what it settles. Six rows is a working set. The kinds that exist almost
everywhere:

| Source | Settles |
|---|---|
| The state or national business registry | Whether the entity is registered, its status, its identifier, its agent, and its filing history |
| The property records search | Who owns the building, the assessment, the land use code, and the sale history |
| The licences and permits portal | Which licences and registrations the entity holds |
| The regulator for the specific trade, where one exists | Whether a licence is current, and where |
| The local licensing or permit office | Local trade licences, signage, occupancy. Name the locality |
| The business's own site, menu, hours, and ordering system | What the business says it sells and how it takes an order |

Two traps, both observed first-hand in the practice this template came from,
and both of which generalise.

1. **Lookalike domains exist.** Sites styled as official record lookups are not
   official. At least one state registry has publicly warned people off them.
   If the domain is not the government's own or the operator's own, it is not
   tier 1, whatever it looks like.
2. **A tier 1 tool goes offline.** One state's property search was pulled after
   a cyber threat. When a tier 1 tool is unavailable, that is a gap. Record it
   as one and move on. Do not substitute a scraper site to fill the hole.

### Tier 2: observed and dated

A tier 2 source shows behaviour rather than status. It is citable when it is
dated and named.

- The dominant local business listing: hours, rating, review count, last post
- The social accounts the segment actually uses, including how recently the
  business posted. Name them; they differ by trade
- The ordering, booking, or marketplace surfaces the segment sells through
- Job postings, which reveal headcount pressure and tooling
- Local press with a named reporter and a date

Name the specific services in the list above for your segment. The generic
version invites the researcher to guess.

Every tier 2 figure is a snapshot. Write the date beside it or do not write it.
"412 reviews" is wrong within a month. "412 reviews as of 7 September 2026" is
true forever.

### Tier 3: leads only

Aggregator directories, undated listicles, forum and Reddit chatter, and any
"best of" roundup. These point at a question. They never answer one. Follow a
tier 3 lead to a tier 1 or tier 2 source, or drop it.

## Exclusions

Reject before spending any more effort:

1. Any fact recalled rather than retrieved.
2. A count, rating, or follower number with no observation date.
3. An aggregator restating a record instead of the record itself.
4. A competitor's claim about the prospect.
5. Anything behind a login the client could not open themselves.
6. A page that failed to load. Record the failure. Do not cite it as evidence.

## The gates

Every fact clears the four gates in `research-sourcing` and lands in its fact
register with its tier from the table above. The three outcomes, cite, verify,
and gap, are defined there. The gap render for a prospect is the one
`prospect-dossier` specifies: "no public figure" or "not run" as words in the
cell, never an empty cell.

## Biases to avoid

1. A well-designed site is not evidence of a healthy business.
2. A quiet social account is a signal, not a verdict. Some owners simply do not
   post.
3. Do not reject a negative finding. A prospect with a stalled online presence
   is the prospect who needs the practice most.
4. Do not treat volume as depth. Ten tier 3 mentions do not equal one licence
   record.
5. Do not let a good story survive a failed gate.

## Handing off to the dossier

Once facts are admitted, `prospect-dossier` takes over: the internal dossier
with its points, scores, catch, and alternates, and the handoff document for
the prospect. Two of its rules depend directly on this skill:

- **Points versus scores.** A point is an admitted fact. A score is a judgement
  built on points. Never let an unadmitted fact become either.
- **The catch card.** The honest constraint on a prospect is usually something
  this skill found and could not fully verify. That is the card's content.

Rule 9 of `AGENTS.md` also applies to anything client-facing: do not name a
name rule 9 withholds.

## Provenance

First-party to the practice this template came from, written 2026-09-07. The
gate and tier structure is adapted from the content-curation rubric and source
registry of a research harness that scored papers for a skills repository.
Nothing of its content transferred, only its shape: tiers, exclusions, gates,
and required metadata.
