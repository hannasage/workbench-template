---
name: purchase-research
description: "How the research team evaluates a purchase for the practice: hardware, software, a subscription, a service, or any recurring business cost. Use when a brief asks what to buy, whether to buy, or which option fits. Codifies the review process the team adopted from published testing organizations, analyst methods, structured decision methods, and government procurement guidance: a decision statement, musts and weighted wants fixed before any product is looked at, candidate discovery with stated inclusion criteria, evidence graded by how it was measured, a total cost of ownership model with an exit line, a weighted matrix with a sensitivity check, adverse consequences for the finalists, and a recommendation as named variants. Carries the hardware criteria for running large language models locally. Route what may be cited to research-sourcing."
---

# Purchase research

A purchase decision is a requirements document that happens to end with a
product name. The requirements come first, the products second, the scores
third, and the choice is the owner's.

`research-sourcing` governs every fact. A specification comes from the
operator's own page. A measurement comes from a published test with a
published method. A price is dated. A user rating is a snapshot with known
bias.

## When to activate

- A brief asks which product, service, subscription, or supplier to choose.
- A brief asks whether a cost is worth carrying, or whether to replace one.
- `quarterly-planning` needs a cost line settled.

Do not activate for a purchase the owner has already made. That is a
`wiki-ingest` of the invoice.

## Where the method comes from

The process below is assembled from methods that publish how they work. Each
step names its origin so a reader can check it. Retrieved 2026-09-11.

| Element | Origin | What was taken |
|---|---|---|
| Decision statement, musts, wants, adverse consequences | Kepner-Tregoe decision analysis, as published by Kepner-Tregoe (2021-02, (a)) and summarized by ValueBasedManagement.net (c) | Musts decide who plays, weighted wants decide who wins, finalists get a consequence review |
| Must, should, could, will not | MoSCoW, Agile Business Consortium (2026-05-28, (a)); origin Dai Clegg, 1994 | The vocabulary for requirements when a client is in the room |
| Weighted criteria and the datum | Pugh, "Concept selection: a method that works", 1981, via Wikipedia (c) | Score against a baseline; the known weakness that many minor criteria can outweigh a must |
| Use-case weighting | Gartner Critical Capabilities FAQ (a): three to seven use cases, 1 to 5 scale, weights per use case | Score per use case when the practice has more than one |
| Evidence grading | Consumer Reports rating methods (2025-11-13, (a)); Notebookcheck rating criteria v8 (2024, (a)); RTINGS (headers only, (a), body not retrievable); SPEC CPU 2017 run rules (b) | Lab measurement with a published method outranks everything else; scores from different method versions do not compare |
| Total cost of ownership | Gartner, "Defining Gartner Total Cost of Ownership" (2005, G00131837, (a)); UK HMG "Total Cost of Ownership: things to consider" (2011, (b)); New Zealand Government Procurement TCO guide (2013, (b)) | Direct and indirect costs; acquisition, operation, end of life; exit and transition costs in the model |
| Net present value and payback | Texas Southern University capital budgeting handout (b) | Discount capital purchases; payback ignores what comes after payback |
| Contract terms | US GSA cloud buying guidance (2026-08-07, (b)); GOV.UK "Define your purchasing strategy" (2026-09-03, (b)); Tropic (2026-03-16) and Vendr (2024-12-02), both vendor content (c) | Data exit price, non-proprietary export, break clauses, no automatic extension, renewal notice windows, price caps, true-ups |
| Review bias | Hu, Pavlou, Zhang, CACM 2009 (b); FTC Endorsement Guides FAQ (2025-07-15, (b)); FTC Consumer Reviews and Testimonials Rule Q&A (2025-05-01, (b)); G2 and TrustRadius scoring pages (a) | User ratings are J-shaped; affiliate and sample relationships must be disclosed; platforms decay and down-weight reviews, and say how |
| Reliability and repair | Backblaze Drive Stats (2026-02-12 and 2024-05-02, (a)); Puget Systems reliability report (2026-01-30, (a)); iFixit repairability scores (a) | Failure data needs sample thresholds and confidence intervals; repairability is scored and versioned |
| Local inference hardware | llama.cpp README and llama-bench README (a); NVIDIA "Mastering LLM Techniques: Inference Optimization" (2023-11-17, (a)); vLLM distributed serving docs v0.9.0 (a); Apple MLX unified memory docs (a) | Memory capacity and bandwidth dominate generation; compute dominates prompt processing; multi-GPU rules |

Two things the sources do not publish, and the process does not pretend they
do: Gartner's default criterion weights, and any consumer testing
organization's per-category formula. Where a placement or a score is cited,
its unpublished weighting is stated as unpublished.

## The process

### Step 1: the decision statement

One sentence with an action and a result. "Choose a workstation that runs the
practice's coding agents locally" is a decision statement. "Look at GPUs" is
not.

Then the context the statement sits in, from the brief or from the owner:

- Who uses it, how often, for what.
- What it replaces, if anything, and what that costs today.
- The time horizon the cost model covers.
- The constraints that are not negotiable: space, power circuit, noise,
  operating system, data residency, the employer's equipment rules.
- The budget. If the brief does not state one, it is a question for the owner
  with options, not an assumption. The research proceeds and the
  recommendation shows what each budget band buys.

### Step 2: requirements, before any product is named

**Musts** are pass or fail. A candidate that fails one is out, and the notes
say which one.

**Wants** are weighted. Weights are set now, written down, and not changed
after scoring starts. A weight changed after the scores are in is a finding
about the analyst.

Use MoSCoW words when the requirement will be shown to a client: must have,
should have, could have, will not have this time.

When the practice has more than one use for the thing, write the use cases
(three to seven, in Gartner's practice) and weight the wants per use case.

Write the requirements in a table with a column that says where each one
came from: the brief, the owner, a constraint, or the analyst's proposal. An
analyst-proposed requirement is a question for the owner until they confirm it.

### Step 3: candidates

State the inclusion criteria before searching, and record every candidate
considered, including the ones excluded and why. A comparison that shows only
the finalists hides the search.

Where candidates come from, by tier:

- Tier 1: the operators' own catalogues and spec pages.
- Tier 2: testing organizations that publish a method (Consumer Reports,
  Notebookcheck, RTINGS, GamersNexus, Which?, Puget Systems for reliability),
  and analyst grids for software (Gartner, Forrester, G2, TrustRadius,
  Capterra), cited as opinions with a method.
- Tier 3: forums, roundups, and marketplace search, as leads.

Include the datum: the option of doing nothing, or keeping what the practice
has. Every score is relative to it.

### Step 4: evidence, per criterion

Score nothing without evidence, and grade the evidence. Highest first.

1. **A measurement with a published method.** A lab test that states its
   procedure, its version, and its sample handling. Scores from different
   method versions do not compare; Notebookcheck states this outright when it
   changes versions. A benchmark run states its repetitions and its variance:
   llama-bench repeats five times by default and reports the standard
   deviation; SPEC's run rules require reproducibility and full disclosure.
2. **The operator's own specification.** A spec sheet, a datasheet, a
   documented limit. Tier 1 for the number, and only the number.
3. **Reliability data with stated thresholds.** Backblaze publishes its
   inclusion thresholds and prefers confidence intervals under 1% before
   trusting a lifetime failure rate. Puget Systems states its data covers its
   own builds and its own definition of failure. Cite the threshold with the
   figure.
4. **Analyst placement.** A quadrant or wave position, with its date and its
   method page. The weights are client-only or unpublished, and the citation
   says so.
5. **User ratings.** A dated snapshot with count, platform, and the platform's
   stated weighting policy. The mean is biased (J-shaped distribution, Hu,
   Pavlou, and Zhang, 2009). Read the distribution, the recent reviews, and
   the one-star reasons. Note incentives: G2 down-weights incentivized
   reviews, Gartner Peer Insights includes them, and the FTC permits them only
   when not conditioned on sentiment.
6. **Vendor claims about performance.** Recorded as claims. A vendor's
   benchmark is evidence that the vendor ran a benchmark.

A criterion with no evidence above level 6 is scored "no evidence" and
counts as zero for the candidate. It is not scored from the analyst's
impression.

Sample caveats travel with the evidence. A reviewer's unit may be
manufacturer-supplied; Consumer Reports, Which?, and RTINGS state they buy at
retail for that reason. No retrieved source quantifies the variance between
review units and retail units, so the notes record the source of the test
unit when the testing organization states it.

### Step 5: cost

One model per candidate, over the horizon Step 1 set, in three blocks. The
categories follow the New Zealand and UK government guides and Gartner's
direct-and-indirect split.

**Acquisition.** Purchase price or first-year subscription, delivery,
installation, licences, integration, migration from what it replaces,
training time at the practice's own hourly value, warranty extensions.

**Operation.** Renewals with the escalation the contract allows, support
tiers, consumables, energy, space, insurance if any, the practice's own hours
to run and maintain it, downtime as Gartner's indirect cost.

**End of life.** Exit fees, data export at the contract's data exit price,
migration to the successor, disposal, resale value as a negative cost.

Energy is computed, not guessed: measured or rated power draw, times hours of
use the owner states, times the electricity rate from the practice's own bill or
the state average from the U.S. Energy Information Administration, dated.

For a capital purchase, show payback and net present value at a discount rate
the owner sets, and say what payback ignores: everything after the payback date,
the time value of money, and the risk of the cash flows.

For a subscription, show monthly and annual, per-seat and usage tiers, and the
cost at the growth the owner expects. Show the exit line separately. A
subscription whose export is proprietary has an exit cost that the price page
does not show.

### Step 6: contract terms, for anything with a contract

Checked and recorded per candidate. Origins: GSA, GOV.UK, Tropic, Vendr, as
cited above.

| Term | What to record |
|---|---|
| Renewal | Automatic or not; notice window in days (30, 60, and 90 all appear); GOV.UK's stance is no automatic extension and a break clause at two years at most |
| Price escalation | The cap, if any; Tropic reports uncapped language of 5% to 25% in the market and recommends 3% to 5% |
| Seats and usage | How seats are counted, true-up cadence, overage rate, rollover of unused volume |
| Data exit | Export format, whether it is non-proprietary, the data exit price, the deletion commitment |
| Security posture | SOC 2 Type 2 report available, its period; ISO/IEC 27001:2022 certificate; for a hosted service, whether the report can be obtained under NDA |
| Support | What the tier includes, response times, what triggers a charge |
| Liability and IP | Who owns what the practice puts in, and what the service produces |
| Termination | For cause, for convenience, and what happens to data on each |

### Step 7: the matrix

Rows are candidates including the datum. Columns are wants with their weights.
Each cell is a score with its evidence grade and a link to the fact register
entry. Musts appear above the matrix as a pass-or-fail table, not inside it,
so that wants cannot sum past a failed must.

Then the sensitivity check: change each weight by one step up and down and
report whether the ranking of the top three changes. A ranking that flips on
one weight is reported as fragile, and the weight it flips on is a decision
for the owner. Rank reversal when a candidate is added or removed is the known
weakness of pairwise methods (Belton and Gear, 1983; Tu and Wu, 2023), and
the matrix is re-checked when the candidate set changes.

### Step 8: adverse consequences

For the top two or three, list what could go wrong if chosen, each with a
probability (high, medium, low) and a severity (high, medium, low), in
Kepner-Tregoe's form. Sources for each: a known defect, a vendor's viability
signal, a supply constraint, a contract term, a dependency on the employer's
rules, a skill the practice does not have.

### Step 9: trial

If a trial, return window, or proof of concept is available, say so and what
it would settle. Government sources retrieved on 2026-09-11 prescribe no
proof-of-concept duration; the notes record that as a gap rather than
inventing one.

### Step 10: the recommendation

Named variants, never one answer. At minimum:

- The lowest total cost of ownership that passes every must.
- The highest weighted score that passes every must.
- The datum, with what doing nothing costs over the horizon.

Where the two leaders differ, say on which criterion and by how much. Where a
budget band changes the answer, show the answer per band.

The choice is the owner's. The deliverable ends with the decision, the variants,
and what each one gives up.

## Hardware criteria

Applied in Steps 2 and 4 when the purchase is a machine.

| Criterion | How it is evidenced |
|---|---|
| Performance for the practice's workload | A published benchmark that matches the workload, with method version and repetitions; or the practice's own run of the same benchmark on a trial unit |
| Thermal and acoustic | Delta over ambient at steady state, in a stated ambient; noise at a stated distance or in a chamber; noise-normalized thermals where the source provides them (GamersNexus method, updated 2026-08-04) |
| Power | Rated draw from the spec sheet, and measured draw from a published test where one exists. No primary source for a wall-power measurement procedure was retrieved on 2026-09-11; record which kind of figure is used |
| Reliability | Published failure data with its sample thresholds and its definition of failure; warranty term and what it covers |
| Repairability and upgrade path | iFixit score with its rubric version; memory, storage, and GPU expansion; parts pairing restrictions; right-to-repair coverage in the state of purchase |
| Sample source | Whether the testing organization bought at retail or received a unit |

## Local inference hardware

The practice's coding agents and automations run models locally when the
purchase is a homelab. What matters, as the operator documentation states it:

- **Memory capacity** bounds the model. A model's weights at a given
  quantization plus the key-value cache must fit in accelerator memory, or
  llama.cpp's hybrid mode spills to system memory at a speed cost. The KV
  cache per token is 2 times layers times heads times head dimension times
  bytes per value (NVIDIA, 2023-11-17). Quantization to 8, 6, 5, 4, 3, 2, or
  1.5 bits reduces the footprint (llama.cpp README).
- **Memory bandwidth** bounds token generation. Decode is memory-bound: the
  rate at which weights and cache move to the compute dominates latency
  (NVIDIA). The llama.cpp Apple Silicon table records generation scaling with
  bandwidth and prompt processing scaling with compute (discussion #4167,
  updated 2026-08-25).
- **Compute** bounds prompt processing. Prefill saturates the accelerator
  (NVIDIA). A coding agent that re-reads large contexts is prefill-heavy, and
  the benchmark must report prompt processing separately from generation, as
  llama-bench does with its `pp` and `tg` tests.
- **Multi-accelerator scaling** follows vLLM's rule: a model that fits one
  device needs no parallelism; one that fits one machine uses tensor
  parallelism across devices; only a model that fits no single machine needs
  pipeline parallelism across nodes, and then the interconnect is the
  criterion. The interconnect between devices in one machine is a spec-sheet
  fact and a must when tensor parallelism is the plan.
- **Unified memory** on Apple silicon gives the CPU and GPU one pool (Apple
  MLX docs), which changes the capacity criterion: the pool is the ceiling,
  not a discrete accelerator's memory.
- **Concurrency.** Batching raises throughput (NVIDIA). An automation that
  serves several agents at once is scored on throughput at that batch size,
  not on single-stream generation speed.
- **Power, cooling, and noise** are musts in a home, and they are measured
  criteria, not impressions. Where no measured figure exists for a
  configuration, the notes say so.

A benchmark figure for local inference names: the model and its quantization,
the prompt and generation lengths, the batch size, the software and its
commit or version, the repetitions, and the variance. A figure without those
is a lead.

## Bias controls

- Read the disclosure. A review site earning affiliate commissions must say
  so near the recommendation (FTC Endorsement Guides). Record whether it does,
  and whether the test unit was bought or supplied.
- Weight a review by its method, not its reach. A forum consensus is tier 3.
- Prefer the review that publishes what it measured over the one that
  publishes what it concluded.
- Re-check a score's method version. A product scored under an old version is
  not comparable to one scored under the new.
- Treat a "state of the market" report from a seller as vendor content, and
  say so where it is cited.
- Record the date on every price. Prices on 2026-09-11 are not prices on the
  day the owner buys.

## Output

The deliverable is a `recommendation`, in the `research-operations` format.
Its `Findings` section is, in order: the decision statement and context, the
requirements table with musts and weighted wants, the candidate list with
exclusions, the evidence and the matrix with its sensitivity check, the cost
model per finalist, the contract terms table where there is a contract, the
adverse consequences, the trial note, and the variants. `Decisions for
the owner` carries the budget question if it was open, every fragile weight, and
the choice itself. `Gaps` carries every criterion with no evidence, every
price that could not be retrieved, and every method detail the sources do not
publish.

## The rules that never bend

- Requirements and weights are written before a product is named, and never
  changed after scoring.
- A score without evidence is zero, not a guess.
- Every price and every spec is dated and sourced.
- The cost model always has an exit line.
- The recommendation is variants. The choice is the owner's.
