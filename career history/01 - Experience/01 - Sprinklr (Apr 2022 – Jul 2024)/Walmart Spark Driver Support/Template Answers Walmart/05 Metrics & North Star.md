

---

## 05. Metrics & North Star

Weak PMs speak impact. Strong PMs define formulas.

• What was your North Star metric?  
• Why that metric?  
• Leading indicators?  
• Lagging indicators?  
• How did you measure improvement?  
• Exact formula for 75% / 85% claims?  
• Retention definition?

**What was your North Star metric?**  
My north star metric was Time-to-Insight (TTI): the time from when an issue first becomes detectable in the ecosystem to when we produce an executive-ready RCA summary with clear ownership routing. Operationally, it’s the timestamp difference between “signal crosses detection threshold” and “RCA summary + recommended owner is ready to act.” This is the metric that directly measures whether we solved the real bottleneck: slow convergence on truth and accountability.

**Why that metric?**  
Because the business pain wasn’t just that issues existed; it was that issues kept repeating while teams took a week to align on root cause. If you compress time-to-insight, you compress the entire incident lifecycle: issues get contained earlier, repeat contacts drop, public escalations reduce, and internal teams spend less time debating and more time fixing. Time-to-insight is also a metric leadership understands because it connects directly to operational cadence; they want daily clarity, not weekly post-mortems.

**Leading indicators?**  
The most important leading indicators were adoption and trust signals that tell you early whether the workflow is working. We tracked cluster coverage (what percentage of incoming contacts were consistently classified and clustered), analyst acceptance and override rates (how often users agree with clusters and summaries versus editing or rejecting them), and routing effectiveness (acceptance versus bounce/reassignment). We also tracked usage patterns like daily active use among the target analyst group and consumption of end-of-day summaries by leadership. These leading signals predict whether the system will actually replace manual triage or remain a “reference dashboard.”

**Lagging indicators?**  
Lagging indicators were operational and business outcomes: reduction in repeat-contact rate for recurring issues, reduction in escalation frequency in public channels for the same themes, and improved time-to-resolution once an issue is routed. Depending on data availability, we also tracked driver experience or churn-risk proxies, because actual churn is multi-factor and often hard to attribute directly. The goal of lagging metrics was to show that faster insight translated into fewer repeated problems and lower operational cost/risk.

**How did you measure improvement?**  
We measured improvement using incident-based before/after comparisons across comparable issue types. For a set of real recurring issues, we captured baseline timestamps for when signals began, when RCA was confidently agreed and shared, and when ownership was assigned. Post-launch, we used system timestamps for detection, summary generation, and routing readiness. We compared medians rather than only means to avoid outlier distortion, and we validated that the same class of issues was being compared so the improvement wasn’t just cherry-picked.

**Exact formula for 75% / 85% claims?**  
The improvement formula is straightforward: Improvement % = (Baseline time − New time) / Baseline time × 100. For the RCA assistant, baseline RCA time-to-insight was roughly seven days and the new cadence was same-day; if you treat same-day as one day for measurement, (7 − 1) / 7 = 85.7%, which supports the ~85% reduction claim. For any 75% claim in a different context, the same formula applies; for example, reducing a task from 20 minutes to 5 minutes yields (20 − 5) / 20 = 75%. In interviews, I explicitly define the start and end timestamp points so the calculation is auditable, not rhetorical.

**Retention definition?**  
Retention can be defined at two levels: user retention of the product and business retention outcomes. For product retention, we define retention as the percentage of target users (ops analysts/support leaders) who use the assistant at least a defined frequency (e.g., weekly) across successive periods, typically measured as returning active users over time. For business retention, the ideal is driver retention—drivers active in period T who remain active in T+30/60/90 days—but when direct churn attribution isn’t available, we use retention proxies such as churn-risk segment movement and repeat-contact reduction for chronic issues. The key is to be explicit about which retention you measured and why.

---
