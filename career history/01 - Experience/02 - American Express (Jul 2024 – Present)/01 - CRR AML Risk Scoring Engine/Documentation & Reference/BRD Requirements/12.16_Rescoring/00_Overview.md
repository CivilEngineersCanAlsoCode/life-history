# BRD 12.16 — Rescoring Capabilities

## Status
In Development

## Target Timeline
26.3 (Rule Execution Team)

## Bead Reference
career-context-4oq

## Business Requirement
Rescore customer population.

## Purpose
Apply framework/data changes.

## Expected Outcome
Real-time risk distribution understanding.

## Coaching Context

### How Rescoring Works in CRR 2.0:
- **Rule Execution Team** handles the actual scoring/rescoring of customer populations
- CRR team defines the framework (rules, weights, configurations); Rule Execution Team runs them against customer data
- Communication: CRR → PubSub/RTF event → Rule Execution Team → scoring results back

### Rescoring Triggers:
1. **Daily delta:** Customer profile data changes (new customer, attribute update) → daily batch rescoring at 7pm MST
2. **Monthly full:** Transactional and time-based data updates → monthly full population rescore
3. **Framework update:** When sandbox changes are promoted to production → immediate rescore of affected population
4. **Simulation:** Sandbox simulation is essentially a "what-if" rescore against production data snapshot

### Time-Based Flag Connection:
- Risk elements with **time-based flag** = data changes monthly (e.g., transaction patterns)
- Performance optimization: skip re-running these rules during daily delta, only run in monthly cycle
- This directly connects to 12.16.1 (monthly vs daily rescoring split)

### Performance Target:
- **SLA:** 10M accounts in ~2 hours (85% improvement over Cadence)
- Vendor POC benchmark: 10M accounts in 5 hours — CRR 2.0 targets better

## Sub-Requirements

| Sub-Req | Title | Status | Coaching Notes |
|---------|-------|--------|----------------|
| 12.16.1 | Automated Rescoring Frequency | In Development | Monthly full + daily delta; time-based flag optimization; Rule Execution Team Target 26.3 |
| 12.16.2 | Framework Update Rescoring | In Development | Triggered by production promotion; rescore at time of implementation |

## Interview Notes
- Both sub-requirements In Development, owned by Rule Execution Team (Target 26.3)
- Currently only daily batch at 7pm MST exists — monthly full rescoring is the gap
- Performance SLA (10M in ~2 hours) directly tested via sandbox simulation benchmarks
