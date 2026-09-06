# JOYLAB 7 Quality Gate V1.0

## Purpose
Judge whether a JoyLab article is a reusable knowledge asset, not merely publishable copy.

## Score: 100
- HOOK 10
- FACT 20
- WHY 10
- TRANSMISSION 15
- JUDGMENT 15
- SCENARIO 10
- NEXT 10
- KNOWLEDGE LINK 5
- SOURCE HYGIENE 5

## PASS threshold
- Total score >= 85
- AND every Hard Gate passes
- Otherwise decision = BLOCKED

## Hard Gates
1. HG-01 Fact/Opinion Separation: verified fact and interpretation must be distinguishable.
2. HG-02 Source Minimum: at least one credible source; time-sensitive claims require a current source.
3. HG-03 No Fabrication: no invented dates, numbers, quotes, entities, links, or causal claims.
4. HG-04 Transmission: at least 3 meaningful causal/impact steps for analysis content. Reviews/guides may use 2 steps if the mechanism is explicit.
5. HG-05 Judgment Evidence: JoyLab judgment must cite or point to evidence already established in the article.
6. HG-06 Scenario Conditions: scenarios must be conditional, not deterministic predictions.
7. HG-07 Next Checkpoint: at least one observable next checkpoint.
8. HG-08 Knowledge Connection: at least two nodes and one pillar.
9. HG-09 Sensitive Data: no customer PII, credentials, restricted company information, or private health/personal data in global/public records.
10. HG-10 Investment Safety: investment content must separate evidence, scenario, and action; no certainty language for market outcomes.

## Detailed scoring
### HOOK / 10
- 0: generic intro
- 5: topic-relevant question/tension
- 10: specific tension tied to reader decision

### FACT / 20
- 0: unsupported summary
- 10: several sourced facts but gaps exist
- 20: key claims sourced, dated, and numerically consistent

### WHY / 10
- 0: restates the event
- 5: one plausible cause
- 10: separates structural/industry/company/market causes where relevant

### TRANSMISSION / 15
- 0: absent
- 8: 2-step impact explanation
- 15: >=3-step mechanism with no obvious causal jump

### JUDGMENT / 15
- 0: no view or pure opinion
- 8: view present with partial support
- 15: view is explicit, bounded, and evidence-backed

### SCENARIO / 10
- 0: one-way forecast
- 5: alternatives without conditions
- 10: >=2 cases with observable conditions and outcomes

### NEXT / 10
- 0: vague conclusion
- 5: generic watch item
- 10: measurable checkpoint with timing/event trigger when known

### KNOWLEDGE LINK / 5
- 0: isolated post
- 3: nodes present
- 5: nodes + related/next content path

### SOURCE HYGIENE / 5
- 0: weak/unclear sourcing
- 3: credible secondary sourcing
- 5: primary/official sources used where available

## Decision rule
`PASS = score >= 85 AND all_hard_gates == true`

Scores never override a failed Hard Gate.

## Status flow
DRAFT -> REVIEW -> PASS -> PUBLISHED
DRAFT/REVIEW -> BLOCKED -> FIX -> REVIEW

## Gold Case policy
A Gold Case must:
- pass schema validation
- score >= 90
- pass every Hard Gate
- be manually inspected at least once before being used as an example for agents
