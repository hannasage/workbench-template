---
name: quarterly-planning
description: "How the research team drafts and refines a quarterly plan for the practice. Use when the owner asks for a quarterly plan, a 90-day plan, a quarterly review, or to refine an existing plan against new market findings. Covers the inputs the plan needs and who supplies each, the plan structure of one to three rocks with lead and lag measures, the scorecard of practice KPIs and where each benchmark comes from, the compliance calendar the practice fills in for its own jurisdiction, the review agenda, and the rule that the team drafts and the owner decides. Route market facts to competitor-research and what may be cited to research-sourcing."
---

# Quarterly planning

A quarterly plan is a short list of things the practice will finish in the
next ninety days, a scorecard that says whether it is on track, and a list of
decisions the owner made to get there. The team drafts it. The owner decides every
line.

`research-sourcing` governs every figure. Nothing about the practice's money,
clients, or capacity is assumed. It is supplied by the owner or read from the wiki
through `wiki-query`, and a figure that is neither is a gap.

## When to activate

- The owner asks for a quarterly plan or a 90-day plan.
- A quarter ends and the last plan needs a review.
- A `competitor-research` or `purchase-research` deliverable changes an
  assumption the current plan rests on, and the owner asks for the plan to be
  refined.

Do not activate to set targets. A revenue target, a rate, and a capacity
number come from the owner. The team can show what a target implies, never what it
should be.

## Inputs

| Input | Supplied by | If absent |
|---|---|---|
| The previous plan and its scorecard | `wiki-query`, or the owner | First plan: say so and start from the scorecard definitions below |
| Capacity: hours per week the owner can give the practice, given the full-time job | The owner, every quarter | Blocking. The plan cannot size anything without it |
| Pipeline: prospects, stage, expected value if the owner has one | The owner, or the wiki | Blocking for coverage math; the plan proceeds with coverage marked as a gap |
| Active clients and their share of revenue | The owner | Concentration cannot be computed; recorded as a gap |
| Market layer: rates, engagement shape, demand | `competitor-research` deliverable, or a fresh run | The plan cites no market figure and says why |
| Costs and purchases under consideration | `purchase-research` deliverable, or the owner | Omitted from the plan |
| Positioning statement and buyer | The owner, or the last plan | Recorded as a decision for the owner |

Capacity is the number the whole plan depends on. No published source studies
a practice run alongside a full-time job, so no benchmark stands in for
the owner's answer. The closest published figures, all for full-time fractional
practitioners, are 21 median billable hours per week across engagements
(Fractional Work Report 2026, n = 1,733) and 10 to 15 hours per client per
month (Frak 2024, attributed by secondary sources; the PDF was not retrievable
on 2026-09-11). They describe a different situation and the plan says so if it
cites them.

## The plan

### Rocks

One to three. EOS Worldwide's published guidance sets one to three rocks for
an individual and three to seven for a company, on the stated rationale that
ninety days is the maximum attention span for a priority (eosworldwide.com,
"What Are EOS Rocks?", retrieved 2026-09-11, (b)). A solo practice is an
individual for this purpose.

Each rock carries:

- **A verb and an object.** "Publish the rate card" beats "pricing work".
- **A done statement.** True or false on the last day of the quarter.
- **A lead measure and a lag measure.** The 12 Week Year's distinction, as
  described by LogRocket on 2023-10-02 (c): a lead indicator is the activity
  under the practice's control, a lag indicator is the result. "Two outreach
  conversations per week" leads; "one signed retainer" lags.
- **The hours it needs**, against the capacity the owner gave. Three rocks whose
  hours exceed the quarter's capacity is two rocks, and the plan says which
  one was cut and why.

### The scorecard

Reviewed weekly, in the EOS pattern of a fixed weekly meeting with a scorecard
review (eosworldwide.com, "What is the EOS Meeting Pulse?", retrieved
2026-09-11, (b)). Each KPI has a definition the practice fixed, a value, and
the benchmark's source or the statement that none exists.

| KPI | Definition | Benchmark and its source, as of 2026-09-11 |
|---|---|---|
| Billable utilization | Billable hours divided by the capacity hours the owner stated | No solo benchmark with a data basis exists. SPI Research reports 66.4% for firms of 500+ (via Deltek, 2026-07-30, (a)). Toggl states 60% as a starting point with no data (c). The plan uses the owner's own target |
| Effective hourly rate | Revenue in the quarter divided by all hours worked, billable or not | No published benchmark found. The plan tracks the trend against the practice's own prior quarters |
| Pipeline coverage | Value of qualified open opportunities divided by the quarter's revenue target | SPI reports 175% of quarterly bookings for firms (a). Clari derives required coverage as one divided by win rate (2026-06-19, (c)). The plan states which it uses |
| Proposal win rate | Proposals won divided by proposals sent, trailing four quarters | SPI reports 48.1% bid-to-win for firms (a). Weiss claims 60 to 80% with conceptual agreement, unsupported (c) |
| Client concentration | Largest client's share of revenue | Projectworks names 20 to 25% for a single client as a common threshold, without a source (2026-06-03, (c)). Recorded as a practitioner threshold |
| Referral share | Share of new conversations that came from a referral or a former employer | Consulting Success (n = 2,800+): over half of first clients came from a former employer. Fractional Work Report 2026: 94% won clients through referrals. Both (a) with the n stated |
| Cash items | Whatever the owner chooses to track: receivables ageing, deposit share, late payments | No consultant-specific runway benchmark was found. Not in the plan unless the owner supplies the figures |

The scorecard never carries a figure the practice did not measure or the owner did
not supply. A KPI with no value is shown with "not measured" and the plan's
first rock is often to measure it.

### The compliance calendar

> FILL: every row of the table below, against your own agencies' pages.

**This table is empty on purpose.** Tax, filing, and classification rules are
jurisdiction-specific and they move. A calendar carried from another practice
would be a set of confident false statements, which is the exact failure
`research-sourcing` exists to prevent. Fill it in once, against your own
agencies' pages, then re-check each entry on the agency's page before any plan
cites it. `prompts/setup.md` covers the first fill.

Every entry states what the source says and cites it with a quality label from
`research-sourcing`. The plan states that the entries are reporting, not advice.

| Item | What the source says, as of YYYY-MM-DD | Source |
|---|---|---|
| The annual entity filing | Its deadline, its fee, whether it is owed when the entity was dormant, and whether an extension exists | |
| Sales or use tax on the services sold | Whether the practice's services are taxable, from what date, and who remits | |
| Worker classification | The rule that governs contractor versus employee where the practice operates | |
| Insurance renewal | Which policies are held and when each renews. The owner supplies the dates | |
| Standing agreements | Any employment, invention-assignment, outside-work, or confidentiality terms that bind the practice's hours, equipment, or subject matter | |

The last row is a standing constraint, not a date. The plan names it once and
every rock respects it. A row the practice has not researched shows "not
checked", never a guess.

### Decisions

The plan closes with the decisions the owner made to adopt it, each as a line
the main session can carry to `DECISIONS.md` if they want it logged: what was
chosen, instead of what, because of what.

## The review

Held at the quarter's end, before the next plan is drafted. The agenda adapts
EOS's published quarterly agenda (eosworldwide.com, "What is the EOS Meeting
Pulse?", (b)):

1. Review the previous quarter: each rock, done or not done, and the
   scorecard's last reading against its first.
2. Review the positioning statement and the buyer. Still true, or changed.
3. Read the market layer if a `competitor-research` run landed this quarter.
   Name what it changes.
4. List the issues: everything that got in the way, and everything that
   surfaced that has no owner.
5. Draft the next quarter's rocks against the capacity the owner gives for it.
6. Name the decisions the draft needs from the owner.

The team prepares steps 1 to 5 as a draft. Step 6 is where the draft stops and
the owner starts.

## Refining an existing plan

When a research deliverable lands mid-quarter:

1. Read the current plan.
2. Name every assumption in it that the deliverable touches, with the line in
   the plan and the finding in the deliverable.
3. For each, state the options: keep the rock, change the rock, drop the rock.
   Do not choose.
4. Update the scorecard's benchmark column only where the deliverable
   supplies a better-sourced benchmark, and say what replaced what.

The plan is one file, updated in place. A refined plan carries an `updated`
date and a one-line change note under the frontmatter. No versioned copies.

## Output

The deliverable is a `plan`, in the `research-operations` format. Its
`Findings` section is, in order: capacity and inputs as supplied, the rocks,
the scorecard, the compliance calendar, the review notes when this is a
review. `Decisions for the owner` carries every open choice with named options.
`Gaps` carries every input that was not supplied and every benchmark that does
not exist.

## The rules that never bend

- The team drafts. The owner decides every rock, every target, every rate.
- No revenue, rate, or capacity figure is assumed, estimated, or carried from
  memory.
- No benchmark enters the scorecard without its source and its caveat.
- The employer constraint is named in every plan.
- Tax and legal rows are reporting, never advice, and the plan says so.
