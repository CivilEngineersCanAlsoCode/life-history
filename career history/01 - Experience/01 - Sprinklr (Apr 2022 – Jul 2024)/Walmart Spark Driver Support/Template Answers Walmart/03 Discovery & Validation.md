
---


## 03. Discovery & Validation

This separates real PMs from feature executors.

• How did you validate the problem?  
• What assumptions were wrong?  
• What user research did you do?  
• What surprised you?  
• Why this solution vs alternatives?  
• What evidence gave you conviction?

**How did you validate the problem?**  
I validated the problem by grounding it in the real RCA workflow and real incidents, not opinions. First, I mapped the end-to-end process from “issue signal appears” to “root cause agreed” to “owner assigned,” and it became obvious the bottleneck was time-to-clarity and cross-team convergence, not a lack of dashboards. Then I backtracked a set of past driver issues and measured how long it took teams to move from early signals to an executive-ready conclusion; the baseline was roughly a week because signals were fragmented and alignment was manual. I also compared internal early signals versus public escalation timing to prove that fragmentation wasn’t just inconvenient—it directly delayed containment and amplified impact.

**What assumptions were wrong?**  
A key wrong assumption early was that identity linkage between internal support interactions and public posts would be clean and deterministic; in practice, public escalation is messy and often anonymous, so we needed probabilistic linkage and confidence gating instead of pretending we always knew the same “user.” Another wrong assumption was that social escalation volume would map cleanly to severity; in reality social channels are biased toward louder voices and region/language effects, so public signals had to be normalized and treated as one input, not the ground truth. A third wrong assumption was that producing insights would automatically drive action; we learned quickly that unless the product also solved routing and ownership clarity, the organization would still stall in meetings even with better analysis.

**What user research did you do?**  
The research was practical and workflow-driven. I did stakeholder interviews across the chain: ops analysts and support leaders to understand how they detect and investigate issues, and fix-owner teams (ops/product/engineering) to understand what information they need to act without pushing back. I reviewed the artifacts they already produced—weekly decks, issue trackers, escalation logs—to identify what was repeatedly missing and what was manually stitched together every time. I also ran prototype walkthroughs using real examples, asking users to complete tasks like “identify the top issues today” and “justify why this is a root cause,” and then iterated the information hierarchy and evidence presentation based on where they hesitated or mistrusted outputs.

**What surprised you?**  
The biggest surprise was that internal signals often exist much earlier than public escalation, but because they’re distributed across channels and teams, they’re invisible as a coherent pattern until it’s too late. Another surprise was that the slowest part of RCA wasn’t analysis; it was alignment—teams debating whether multiple complaints are one issue or many, and arguing about ownership boundaries. The third surprise was that trust and explainability mattered more than “fancier AI”; users didn’t want black-box answers, they wanted evidence snippets and confidence so they could defend the insight in front of leadership.

**Why this solution vs alternatives?**  
We chose unified signals plus unsupervised clustering and evidence-grounded summaries because the core need was discovery and speed under changing issue patterns. Keyword/rule-based monitoring was rejected as the primary approach because it’s brittle, noisy, and misses emerging issues when vocabulary shifts. A supervised classifier-only approach was not viable for an MVP because stable labels didn’t exist and taxonomy drift would create heavy maintenance and slow iteration. A dashboard-only approach improved visibility but didn’t reduce the RCA cycle time enough because humans still had to infer root cause and drive cross-team alignment. The chosen solution directly attacked the bottleneck: turn multi-source noise into a small set of actionable root-cause themes and route them into ownership.

**What evidence gave you conviction?**  
Conviction came from three types of proof. First, retrospective incident replays: when we ran historical issues through the unified and clustered view, we could surface coherent themes earlier than the manual process, showing the approach would compress time-to-clarity. Second, user acceptance evidence: analysts and leaders consistently preferred ranked theme summaries with evidence over raw dashboards, and fix-owner teams were more willing to engage when insights were accompanied by representative examples and quantified impact. Third, operational impact signals during pilots: manual triage time reduced, fewer “what’s happening?” alignment loops were needed, and the output format fit the end-of-day executive cadence, which is the practical test of whether a product will be adopted in an enterprise setting.

---
