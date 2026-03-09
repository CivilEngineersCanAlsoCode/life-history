

---


## 12. UX & Product Thinking

• How did you reduce cognitive load?  
• Why your chosen user journey?  
• What usability metrics did you track?  
• How did you validate design?  
• What did users initially struggle with?

**How did you reduce cognitive load?**  
We reduced cognitive load by turning a messy, high-volume text firehose into a small number of decisions the user can make quickly. Instead of showing raw tickets and social posts, the interface surfaced a ranked list of “top recurring issues” with three things users actually need: a short plain-language summary of the theme, evidence snippets that justify why the system thinks it’s real, and an impact estimate (volume, regions, trend). We also made outputs structured and consistent—same fields every time—so users don’t have to re-learn the UI each day. The key principle was: compress ambiguity. The analyst shouldn’t be doing pattern discovery manually; they should be validating and acting.

**Why your chosen user journey?**  
The journey was designed to match how ops teams actually work: detect, understand, decide, route. So the flow was intentionally “Listen → Learn → Act.” First, we show what’s spiking and what’s new (detection). Next, we show why it’s happening and how big it is (cluster summary + evidence). Finally, we give the action step (create case / route owner) so insight turns into execution. We avoided a purely exploratory analytics journey because that would push users back into manual interpretation and meetings, which was the original bottleneck. This product was built for operational cadence, not curiosity browsing.

**What usability metrics did you track?**  
We tracked usability in terms of speed, confidence, and actionability. The core metrics were time-to-find top issues (how quickly an analyst can identify the top 3–5 themes), time-to-validate a cluster (how long it takes to decide “this is real”), and time-to-route (how quickly an issue moves from insight to an owner). We also tracked adoption signals like daily/weekly active usage for the target user group, executive summary open/consumption rate, and routing acceptance versus reassignment rate. In enterprise, a key usability metric is also trust: how often users override, edit, or ignore the system’s suggested summary and owner.

**How did you validate design?**  
We validated design through iterative walkthroughs with the primary user group using real data, not mock data. Early prototypes were tested by asking analysts to complete real tasks: “Identify the top issues today,” “Explain why issue X is happening,” and “Decide who should own it.” We used their feedback to simplify the information hierarchy, reduce unnecessary navigation, and add the exact evidence they needed to trust the output. We also validated with leadership by testing the end-of-day executive summary format—whether it was readable in minutes and whether it drove the right questions and decisions. The design loop was anchored on: does this reduce meetings and manual triage, or does it just look pretty?

**What did users initially struggle with?**  
Users initially struggled with trust and interpretation—especially around clustering and confidence. They would ask, “Why are these grouped together?” and “How sure are we that this is the real root cause?” Another early struggle was fear of false positives: analysts didn’t want to escalate something that later looked wrong. That led us to emphasize explainability (evidence snippets, representative examples, and clear labeling), and to introduce confidence gating and a manual review path for high-risk items. Users also struggled when too many clusters were shown; we solved that by prioritizing and ranking ruthlessly so the UI always starts with a small set of the most impactful themes.


---
