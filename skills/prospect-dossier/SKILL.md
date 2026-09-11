---
name: prospect-dossier
description: "How the research team studies one prospect and produces two documents: an internal dossier for the owner and a handoff document they can give the prospect. Use when a brief names a business the practice might sell to. Covers what to research about the entity, its vertical, its public image, and its web presence; the audit checklist for a small business's online presence; the internal dossier's sections including the catch and the score; the handoff document's sections, tone, and what it never contains; and the rendering handoff to the brand skill. Route which facts may be cited to prospect-research, which carries the practice's regional source tiers and the four gates."
---

# Prospect dossier

A prospect run answers one question for the owner, "is this a business the
practice should pursue, and on what", and then produces a second document
that answers a different question for the prospect: "what does the public
see when it looks for you, and what could change".

`prospect-research` decides what may be written down and carries the tier
table for the practice's buyer: owner-operated specialty retail in Howard,
Carroll, Frederick, Baltimore, and Anne Arundel counties. This skill decides
what to look for and what the two documents look like. `research-sourcing`
binds wherever `prospect-research` is silent.

The dossier and handoff layout this skill sets is the example house standard.
Replace it with your own, or adopt it deliberately and say so in
`DECISIONS.md`.

## When to activate

- A brief names a prospect.
- The owner forwards a prospect's email or mentions a business they met.
- A prospect asks what the practice would do for them, before a proposal.

Do not activate for a business the wiki already holds a current dossier on.
Run `wiki-query` first and, if the dossier is current, refresh only the dated
snapshots.

## What to research

Five areas. Each yields facts for the register, and each fact clears the four
gates before it reaches either document.

### 1. The entity

From tier 1 records, as `prospect-research` lists them: registration and
status with the state, resident agent and principal office, property owner
where the storefront is, licences the vertical requires, county permits. The
business's own site for what it says it sells and how it takes an order.

Record what the records disagree on. A trading name that is not the
registered name, an address that differs between the registry and the
storefront, a licence in a different name: each is a finding and none is a
verdict.

### 2. The vertical

What the segment is and what it runs on. The tools its operators typically
use for ordering, inventory, and point of sale, from the operators' own sites
and job postings. The regulation the vertical carries, from the agency's own
page. The seasonality the vertical states about itself. Where the vertical's
own trade press is, with named reporters.

This section is written once per vertical and reused across prospects in it.
When the wiki holds a current concept page for the vertical, cite it and do
not rebuild it.

### 3. Public image

Dated snapshots only, in `prospect-research`'s tier 2 form.

- Google Business Profile: rating, review count, hours, last post, photo
  count, whether the owner responds to reviews, and the date observed.
- Other review platforms the vertical uses, with the same fields.
- Social accounts: which exist, follower counts, last post date, cadence over
  the last ninety days, whether posts are the owner's or a scheduler's.
- Press: local and trade, by named reporter and date.
- The one-star and five-star reviews, read, and what they say the business is
  known for. The mean is not read as a quality measure.

### 4. Web presence

The audit that becomes the spine of the handoff document. Every line is a
fact with a date and, where it is a measurement, a tool and a version.

| Check | What to record | How |
|---|---|---|
| Domain and hosting | Registrant visibility, registrar, expiry, TLS certificate validity and issuer, redirects from bare domain and www | The registry's WHOIS or RDAP, the browser's certificate view |
| The site exists and loads | Load time to interactive on a mobile profile, page weight, largest image | A published performance tool, named with its version and the date, run twice |
| Mobile | Renders at phone width, tap targets, text size, horizontal scroll | Emulated viewport, screenshots dated |
| Accessibility basics | Alt text present, contrast on the primary text, keyboard reach of the primary action, form labels | An automated checker, named, plus a manual pass on the three main pages |
| Search basics | Title and description tags, heading structure, structured data for a local business, sitemap, robots, canonical | Page source and a validator, named |
| Business facts | Name, address, phone, hours: present, and consistent with the Google Business Profile and the registry | Side by side, dated |
| The transaction | Can a customer order, book, or buy; on what platform; how many steps; does it work on a phone | Walk it to the last step before payment, dated |
| Contact | Form works, email address is on the site's domain, response received or not within a stated window | Send a test message only if the brief allows it |
| Content | Last update date, whether the news or blog is live or abandoned, whether prices or menus are current against the storefront | Dated |
| Ownership of the stack | Which platform built the site, who is credited, whether the owner can edit it | Page source, footer, the platform's own page |

A check that cannot be run is recorded as not run, with the reason. It is not
scored.

### 5. Signals

Hiring, expansion, a second location, a new product line, a change of hours,
a change of ownership. From the business's own posts, job boards, the
registry's filing history, and local press. Each dated.

## The internal dossier

Audience: the owner. One file, `dossier.md`, in the `research-operations`
deliverable format with `audience: owner`. Its `Findings` section is:

1. **The business in one paragraph.** What it is, where, since when per the
   registry, what it sells per its own site.
2. **Points.** The admitted facts from the five areas, each with source and
   date. A point is a fact.
3. **Scores.** The analyst's judgement built on points, labelled as
   judgement: fit with the practice's offer, size of the visible gap, reach
   of the owner, urgency signals. Each score names the points it rests on.
   Never a score without points under it.
4. **The catch.** The one honest constraint on this prospect. Usually the
   thing the research found and could not fully verify: a licence in
   question, a site that is being rebuilt, an owner who is selling, a
   platform that locks the business in. There is always one. A dossier with
   no catch was not read hard enough.
5. **Alternates.** Two or three businesses in the same vertical and counties
   that surfaced during the run, each with one line and the reason it is an
   alternate. Not researched; listed so the next run has a start.
6. **What the practice could offer.** Options, not a proposal. Each option
   names the points that make it relevant and the capacity it would need.
   No price unless the owner supplied a rate card.

`Decisions for the owner` carries: pursue or not, which offer to lead with, and
whether the handoff document goes out. `Gaps` carries every check not run and
every record not found.

## The handoff document

Audience: the prospect. One file, `handoff.md`, with `audience: client`. It is
the part of the research the prospect can use whether or not they hire the
practice, and it is written so that giving it away costs the practice nothing
it would not say in the first meeting.

### What it contains

1. **Cover.** The business's name, the date, "Prepared by the practice".
   Nothing else.
2. **What was looked at.** The scope in three sentences: the public records,
   the online presence, the dates. So the reader knows the limits.
3. **What the public sees.** The web presence audit, as findings the owner
   can check themselves. Each line: the check, what was found, the date. Where
   a measurement is cited, the tool. Plain language: "the site takes nine
   seconds to load on a phone", not a score.
4. **What is working.** Findings the owner should keep. This section is not
   optional and not padding; a document that only lists faults reads as a
   sales pitch and gets read as one.
5. **Where the gaps are.** Findings the owner can act on, in the order of
   what a customer meets first. Each gap names what a customer experiences,
   not what a developer would fix.
6. **What could change.** Two or three named options, each described by what
   the customer would experience afterwards. No prices unless the owner set them.
   No timelines.
7. **Sources.** Every record and every measurement, with its date, so the
   owner can open each one.

### What it never contains

- The scores, the catch, the alternates, or any judgement of the owner.
- A fact about the owner as a person, their finances, their staff, or their
  disputes.
- Anything that was behind a login, or from a competitor's account of them.
- Any name rule 9 withholds, by name or by description.
- A fact that did not clear the four gates.
- "You" and "your" where the business's name reads as well. Name the
  business. The register is authoritative and declarative, which is what a
  public-writing standard asks for.
- Buzzwords and empty claims. If the workbench installs a copy standard, it
  binds this document and names the patterns to cut.

### Tone

The owner is the expert on their business. The document is the expert on
what the public sees. It says what it found, in the order a customer would
meet it, and it stops. It does not persuade. The findings do that or they do
not.

## Rendering

Both files are markdown and both are canonical. When the owner wants the handoff
document as a branded artifact, that is a delivery pipeline task for
`interface-builder`, under the workbench's brand skill if one is installed,
with `handoff.md` as its specification. The research team does not render.

Layout conventions the render follows:

- One page per section, the audit as a table with the check, the finding,
  and the date as its three columns.
- A gap is stated in text, never signalled by colour alone.
- "No public figure" and "not run" appear as words in the cell, never as an
  empty cell.
- Sources are a numbered list at the end, matched by number in the body.

## The rules that never bend

- Every fact in either document clears the four gates in `prospect-research`.
- A point is a fact. A score is a judgement built on points, and it is
  labelled.
- The handoff document carries nothing that would embarrass the practice if
  the prospect showed it to a competitor.
- No price, no timeline, and no promise in the handoff document unless the owner
  supplied them.
- Nothing about the owner as a person.
