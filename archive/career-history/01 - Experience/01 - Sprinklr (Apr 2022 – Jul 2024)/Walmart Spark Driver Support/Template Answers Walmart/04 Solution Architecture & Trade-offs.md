

---


## 04. Solution Architecture & Trade-offs

This is where strong PMs stand out.

• Why this architecture?  
• What were 2–3 alternative approaches?  
• What trade-offs did you accept?  
• What did you deliberately NOT build?  
• What was technically risky?  
• What scalability risks existed?

If you can’t articulate trade-offs, interviewer will doubt ownership.

**Why this architecture?**  
I chose this architecture because the goal wasn’t “better analytics,” it was to compress the full RCA cycle into a same-day operational loop. The only way to do that was a layered system that mirrors how decisions get made: ingest signals from internal support and public escalations, unify them into a single ecosystem view, detect recurring themes through clustering, generate an evidence-backed summary that executives can consume quickly, and then convert insight into action through routing and case creation. If any layer is missing—especially the action/routing layer—you don’t actually reduce time-to-clarity; you just create another dashboard that still requires manual interpretation and cross-team meetings.

**What were 2–3 alternative approaches?**  
One alternative was keyword/rule-based monitoring and dashboards. It’s fast to ship and cheap, but it’s brittle, produces high noise, and breaks as soon as vocabulary changes or new issue patterns emerge; it also doesn’t discover unknown unknowns. A second alternative was a supervised classification-first approach, but that requires stable labeled data and continuous maintenance as categories drift, which is hard in dynamic support environments; it also tends to force everything into predefined buckets and can miss emerging themes early. A third alternative was unification-only analytics, where internal and external data are combined into one reporting view, but without clustering and workflow routing the bottleneck remains: humans still have to infer root cause and coordinate ownership, so cycle time doesn’t compress meaningfully.

**What trade-offs did you accept?**  
I accepted a deliberate trade-off between speed-to-value and perfect accuracy by designing the system to be recall-oriented at detection and precision-oriented at action. In early detection, we would rather surface a potential emerging issue than miss it, but when it comes to routing or executive summaries, false positives destroy trust, so we gated automation behind confidence thresholds and required evidence snippets to justify claims. I also traded off “fully autonomous AI” for explainability and governance, because in enterprise settings trust is more important than novelty. Finally, I traded off perfect identity matching across public and internal signals for time-to-ship by using time-window and probabilistic linking with explicit confidence, rather than pretending we can deterministically connect every post to an internal record.

**What did you deliberately NOT build?**  
For MVP, I deliberately did not build auto-remediation or fully automated resolution because the blast radius is high if the system is wrong and governance wasn’t mature yet. I also did not build deep causal graphs or long-horizon forecasting because they add complexity and don’t directly remove the immediate bottleneck of time-to-clarity. I avoided building a fully customizable taxonomy management UI initially; instead we started with a curated L1/L2/L3 taxonomy that was stable enough to ship, then planned configurability once usage patterns stabilized. I also did not aim for perfect cross-channel identity resolution in MVP because it’s expensive and not necessary to deliver the “top issues + why + impact + owner” outcome.

**What was technically risky?**  
The riskiest technical areas were clustering coherence and drift, and trust in GenAI summaries. Unstructured support text and social posts are noisy, full of slang and partial context, and clustering can fragment or merge themes incorrectly if thresholds aren’t tuned. On the GenAI side, hallucination risk is existential in enterprise: one incorrect executive summary can kill adoption, so the summarization layer had to be constrained and evidence-grounded with confidence gating. Data latency was another risk: the product promise was same-day summaries, so ingestion and processing needed to be reliable under spikes. Privacy and access control were also risky because support logs can contain sensitive information and outputs must be governed tightly.

**What scalability risks existed?**  
At scale, the first risk is compute and latency: embeddings, clustering, and summarization can become expensive and slow during volume spikes, so batching, caching, and threshold gating are required to keep unit economics and SLAs stable. The second risk is noise explosion from social data and the tendency for clusters to drift as new topics emerge, which can degrade quality unless drift is monitored and thresholds are tuned continuously. The third risk is multi-tenant and governance complexity in an enterprise platform: strict tenant isolation, RBAC, audit trails, and client-specific taxonomies and routing mappings become mandatory, and any leakage or misconfiguration is catastrophic. Finally, language and regional diversity can introduce systematic blind spots if the system isn’t designed for multilingual and region-normalized behavior.


---
