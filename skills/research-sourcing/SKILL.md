---
name: research-sourcing
description: "What a research role may write down, for any subject. Use whenever a fact is bound for a notes file, a comparison, a plan, a recommendation, or any document the owner or a client will read. Covers the three source tiers and three quality labels, the four gates a fact clears before it is cited, the fact register schema, how vendor content, surveys, user reviews, and legal or tax pages are handled, and how a gap or a disagreement is recorded. Route prospect-specific sources for the practice's buyer segment to prospect-research, which carries its own tier table and points here for the gates."
---

# Research sourcing

This skill decides what may be written down. The subject skills decide what
to look for, and `research-operations` decides where it goes.

`prospect-research` carries a tier table built for the practice's buyer segment
and points here for the gates. On which source settles a prospect
question, that skill wins. On what a fact must clear, this one binds every
subject the research team touches, prospects included.

## The controlling rule

**Never carry a fact from training memory into a deliverable.** `AGENTS.md`
rule 4, no exception. A price, a rate, a survey figure, a statute, a spec, a
date, a name: retrieved this session or not written.

**A missing figure is a finding.** Rule 5. When the number does not exist
publicly, the notes say so and the deliverable says so. Never estimate into a
gap, never average a range to fill one, never reconstruct a URL that was not
fetched.

## Source tiers

A tier says what a source can settle.

### Tier 1: records of authority

Settles a question on its own.

- A government record or page: a statute, a regulation, an agency bulletin, a
  registry entry, a labor statistics table.
- A standards body's own page for its own standard.
- An operator's own documentation for its own product: a spec sheet, a pricing
  page, a changelog, a published test method.
- A court ruling, from the court or a law report.

A vendor's page is tier 1 for what the vendor sells, charges, and specifies.
It is tier 3 for what the vendor says about the market, its competitors, or
what buyers should want.

Verify the domain. A lookalike site styled as a registry is not a registry. If
the domain is not the agency's, the standards body's, or the operator's, it is
not tier 1 whatever it looks like.

### Tier 2: observed and dated

Settles a question when it is named and dated.

- A survey or dataset that states its sample size and its method.
- A lab test with a published methodology and a version.
- A dated snapshot: a rating and review count, a follower count, a price seen
  on a page, a job posting.
- Local or trade press with a named reporter and a date.
- An academic paper, cited by journal, year, and authors.

Every tier 2 figure is a snapshot. Write the date beside it or do not write
it.

A survey that states its n but not its sampling method is tier 2 with a
caveat, and the caveat travels with the figure. A survey published by a firm
that sells the thing surveyed is tier 2 with a caveat, and so is that one.

### Tier 3: leads only

Points at a question. Never answers one.

- Aggregator directories and comparison sites.
- Undated listicles and "best of" roundups.
- Forum threads and social posts.
- Vendor marketing about the market.
- A secondary source restating a figure from a primary source it names.
- An encyclopedia article.

Follow a tier 3 lead to the tier 1 or tier 2 source it points at, or drop it.
When the primary source cannot be retrieved, the figure may appear in the
notes as "attributed by <secondary> to <primary>, primary not retrieved", and
it does not reach the deliverable as a cited fact.

### Tier 1, first-party: measured on this disk

Settles a question about this practice's own tree, and nothing else.

A first-party measurement is a figure a role produced by running a command
here: a byte count, a file count, a directory size, a commit date. The tree is
the record of authority for itself, so the measurement is tier 1 for what it
measured. It carries label (a), because it is data from the organization that
produced it and the command is its stated method.

Three conditions, all of them:

- The notes record the exact command, verbatim, so anyone can re-run it. A
  figure with no command is not admissible at any tier, and the fact-checker
  fails it as not reproducible.
- The notes record the date the command ran. Like every tier 2 figure, this
  one is a snapshot: write the date beside it or do not write it.
- The source line names the path measured, not a URL. There is nothing to
  fetch.

A first-party measurement is never a published constant. It is true of one
tree at one moment, and the next edit changes it. Never carry one into a later
run without re-measuring, and never cite one as a fact about anything outside
this disk.

## Quality labels

Beside the tier, each source line carries a label that says what kind of
document it is. The two are independent: a tier 2 survey is (a), a tier 1
statute is (b), a tier 3 blog is (c).

| Label | Means |
|---|---|
| (a) | A survey, dataset, methodology document, or first-party measurement from the organization that produced it, with n and method stated where it is a survey and the command stated where it is a measurement |
| (b) | A standard, a statute, a regulation, a government page, a court ruling, a textbook, or a peer-reviewed paper |
| (c) | Practitioner opinion, journalism, vendor marketing, a secondary roundup, a forum |

A (c) source may carry the only available account of something. Cite it as
what it is: "<person> states", "<vendor> claims", never as a fact about the
world.

## The four gates

Every fact clears all four before it is cited. One failure and it does not
enter the deliverable.

| Gate | Pass | Fail |
|---|---|---|
| G1 Retrieved | Fetched this session, retrieval date recorded | Recalled, inferred, assumed, or read from a search snippet only |
| G2 Attributable | A named source a reader can open and check | "Studies show", "public records indicate", with nothing named |
| G3 Current | Carries a date, or the source states its own refresh cadence | Undated, or older than the claim implies |
| G4 Load-bearing | Changes what the owner would decide, quote, or advise | True but decorative |

G1 means the page body, not the search result. A snippet is a lead.

G4 is the gate that keeps a deliverable short. A fact that passes G1 to G3 and
fails G4 goes in the notes and stays out of the document.

## Four outcomes, never two

| Outcome | Condition | What the deliverable does |
|---|---|---|
| Cite | All four gates pass | States the fact with source and date |
| Verify | G1 and G2 pass, G3 is doubtful | States the fact, names the date it was true, says it needs re-checking before use |
| Not re-confirmed | A prior run recorded it, and this run did not re-fetch it | Names the figure, names the run that recorded it, and says plainly that this run did not re-retrieve it |
| Gap | Any gate fails, or nothing was found | States what was looked for and that it does not exist publicly or could not be retrieved |

The gap is a real outcome with a real sentence in the deliverable. It is not a
footnote and it is not silence.

A figure carried forward from an earlier run is neither cited, nor verified,
nor a gap: it exists, somebody wrote it down, and nobody checked it this time.
Calling it a gap overstates the absence and calling it verified overstates the
check. A prior run's figure is a lead until it is re-retrieved, and this row is
how a deliverable says so.

## The source line

Under every finding in a notes file:

```
Source: <publisher>, "<title>", <published date or "undated">, <URL>, retrieved YYYY-MM-DD, tier <1|2|3>, quality (<a|b|c>)
```

A retrieval that failed:

```
Source: <publisher>, "<title>", <URL>, retrieval failed YYYY-MM-DD (<error>), not cited
```

A failed retrieval is recorded because it proves the question was asked. It is
never cited as evidence, and the deliverable never presents it as a source.

A first-party measurement:

```
Source: first-party measurement, path <path measured>, command `<command>`, measured YYYY-MM-DD, tier 1, quality (a)
```

The command is the source. Without it the line is not a source at all.

## The fact register

Every fact that may reach the deliverable gets an entry in the notes file. The
fact-checker works from this register and from nothing else.

```yaml
- id: F1
  claim: ""
  value: ""
  source_name: ""
  source_url: ""
  source_tier: 1 | 2 | 3
  quality: a | b | c
  published_on: ""       # or "undated"
  retrieved_on: ""
  observed_on: ""        # when the fact was true, if different from retrieval
  retrieval_status: retrieved | partial | failed
  gate_notes: ""         # any gate that was close, any caveat that travels with the figure
  used_in: ""            # the deliverable section, or "notes only"
```

`retrieval_status: failed` means the fact does not go in. Keeping the row is
the point.

**The id is namespaced to the notes file, never bare.** Prefix every id with a
short slug for the file it lives in, so `ringc-F1` and `pricing-F1` are two
facts and not one. Bare `F1` is refused. When more than one specialist writes
into the same run folder, the `fact-checker` reads every register and writes
one `CHECK.md`, and a bare id cannot address a fact once a run has more than
one specialist in it.

For a first-party measurement, `source_name` is `first-party measurement`,
`source_url` is the path measured, `observed_on` is the date the command ran,
`retrieval_status` is `retrieved`, and `gate_notes` carries the command
verbatim. The fact-checker re-runs it from there, so a register row with no
command cannot be checked.

## Handling particular kinds of source

**Surveys.** Record n, the fielding date, the method, and who paid for it. A
publisher that reports different figures for what appears to be the same
survey on two pages gets both figures recorded and a line under
`Disagreements`. Do not pick one.

**Vendor content.** Label it. A pricing page is tier 1 for the price. A "state
of the market" report from a firm that sells into that market is tier 2 with a
caveat when it states n and method, and tier 3 when it does not.

**User reviews and ratings.** Record the platform, the count, the rating, and
the observation date. Do not treat a mean rating as a measure of quality: the
distribution of online reviews is J-shaped, with purchasing bias and
under-reporting bias, which makes the mean a biased estimator. Source: Hu,
Pavlou, and Zhang, "Why Do Online Product Reviews Have a J-Shaped
Distribution?", Communications of the ACM 52(10), 2009. Note whether reviews
were incentivized. Prefer platforms that state how they weight recency and
incentives, and record that policy beside the figure.

**A page that looks like a survey and is not.** A title with the word survey in
it, a respondent count, and figures laid out as findings are presentation, not
method. Before treating any figure as measured, find the sentence that states
how it was measured. Where the page does not state one, the figure is a named
opinion, label (c), whatever the page calls itself. Read the whole page before
labelling it: the disclaimer is usually below the figures, not above them.

**A source about a different population.** A survey can be current, well
sourced, and still be about somebody other than the buyer in the brief. An
enterprise procurement study and a mid-market technology study are not evidence
about a ten-person retailer, however good their method is. Two rules. Label the
population beside the finding, in the same sentence, naming who the respondents
actually were. Then say whether the finding is being carried across as evidence
or as a hypothesis, and never let the second quietly become the first. Where no
source exists for the briefed population, that is a gap, and a study of a
different population never fills it.

**Analyst reports.** A Gartner, Forrester, IDC, or G2 position is a tier 2
opinion with a published method and unpublished or client-only weights. Cite
the placement, the document date, and the method page. Never cite a placement
as a measurement.

**Legal, tax, and compliance pages.** Government first: the agency, the
statute, the bulletin. Law-firm commentary is (c) and is cited as commentary.
Every such finding is reporting, never advice, and the deliverable says so in
one sentence where the finding appears. Check the current status of a rule
before citing it: a rule that was proposed, stayed, vacated, or rescinded is
cited with that status.

**Pages that update in place.** Record both the published date and the
updated date when the page shows them. Record the date the page was last
modified when that is all it shows. An encyclopedia article is "living" and
tier 3.

**Paywalled or login-gated content.** If the reader of the deliverable could
not open it, do not cite it. If it is the only source, record it in the notes
as a lead and the deliverable records a gap.

## Search discipline

1. Go to the record of authority first. A registry, an agency, an operator's
   own site. Search engines find the page; they do not settle the question.
2. Read the page, not the snippet. G1 requires the body.
3. Find the date. A page with no date and no refresh cadence is G3 doubtful.
4. When a secondary source names a primary source, fetch the primary. Cite the
   primary. If the primary fails, say so.
5. Stop when the next source stops changing the answer. Five sources that
   agree on a figure are one finding, not five.
6. Record what was looked for and not found before moving on. The gap list is
   written during the search, not reconstructed after it.

## Biases to watch

1. A well-produced page is not evidence of a well-run business, a good
   product, or a true claim.
2. Volume is not depth. Ten tier 3 mentions do not equal one tier 1 record.
3. A good story does not survive a failed gate.
4. The first figure found anchors every figure after it. Record the range
   before recording the number.
5. A source that agrees with the requester's hope gets the same gates as one
   that does not. Rule 6.
6. A number with no date is a number with no meaning.

## Disagreements

When two credible sources conflict, the notes record both, the tier and label
of each, and what the conflict turns on: definition, date, sample, or
publisher interest. The deliverable states the disagreement and does not
resolve it unless a tier 1 source settles it. A disagreement that changes the
answer is a decision for the owner.

## Provenance

First-party to the practice this template came from, written 2026-09-11. The
gates, outcomes, and register began in `prospect-research` and were
consolidated here, so one rule set covers every research subject. The quality
labels follow an (a), (b), (c) scheme. The J-shaped distribution finding is
cited above. The first-party tier was added after a run registered
measurements of this repository that no tier described.
