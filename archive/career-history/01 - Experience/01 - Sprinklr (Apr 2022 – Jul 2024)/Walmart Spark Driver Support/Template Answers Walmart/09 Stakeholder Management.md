

---

## 09. Stakeholder Management

No real product launches without friction.

• Biggest pushback?  
• Engineering constraint?  
• Sales overpromise?  
• Consultant resistance?  
• Political pressure?  
• How did you align conflicting incentives?

Give a real conflict story.

**Biggest pushback?**  
The biggest pushback was trust: “Can we rely on AI-generated RCA without embarrassing ourselves in front of leadership or the client?” Stakeholders were worried about false alarms, misidentified root causes, and reputational damage if an executive summary contained wrong conclusions. There was also pushback around ownership—teams were comfortable consuming insights, but less comfortable when the system started routing issues and implicitly assigning responsibility. That’s where friction shows up: insights are safe; accountability is political.

**Engineering constraint?**  
Engineering constraints were mainly around data unification reliability and latency. Joining internal support data with external social signals is messy—identity is not always available, timestamps can be inconsistent, and data pipelines can lag during spikes. There were also constraints around building this in an enterprise-safe way: role-based access, auditability, and making sure summaries don’t leak sensitive information. Engineering pushed back on anything that would create production risk, especially around “auto-routing” and “crisis scoring” without clear thresholds and monitoring.

**Sales overpromise?**  
Yes, classic enterprise risk: sales wanted a clean story like “fully automated RCA” and “predict crises accurately,” because it sells. The danger is that overpromising creates immediate trust loss if the model is uncertain or noisy in early phases. I managed this by tightening positioning: “assist and accelerate” rather than “replace humans,” and by defining clear scope boundaries for MVP—same-day summaries for top recurring issues with evidence, not complete automation of every issue across every region.

**Consultant resistance?**  
There was resistance from service/consulting teams because automation can feel like it reduces their perceived value or billable effort. They were also worried about flexibility—consultants prefer highly customizable workflows per client, while product needs scalable defaults. I handled this by reframing the product as leverage: consultants spend less time on repetitive analysis and more time on higher-value advisory, and by designing the system so outputs were editable and configurable rather than rigid.

**Political pressure?**  
Political pressure came from two directions: leadership wanted faster, “exec-ready” outputs, while operational teams feared being blamed when issues became visible and routed. Internally, different teams had different incentives—support wants faster closure, ops wants stable operations, product wants roadmap focus, and nobody wants surprise accountability. Externally, enterprise expectations amplify everything: a single wrong summary can become a credibility incident.

**How did you align conflicting incentives? (real conflict story)**  
The real conflict was about moving from “insights” to “action.” Leadership wanted automatic routing to the right team to cut cycle time, but several teams resisted because it created accountability and they feared false positives. The compromise I drove was a staged rollout with governance: we introduced routing in a “suggested owner” mode first, backed by evidence snippets and confidence scores, and tracked acceptance/reassignment rates. Only once routing accuracy and trust were proven did we tighten automation thresholds for high-confidence cases. In parallel, I aligned incentives by making success measurable for everyone: leadership got same-day visibility, analysts got time savings and clarity, engineering got safety gates and observability, and action teams got fewer noisy escalations because we filtered and prioritized before routing. This turned routing from “blame assignment” into “faster clarity with controlled risk,” which reduced political resistance and made adoption sustainable.

---
