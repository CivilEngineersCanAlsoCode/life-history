# STAR Stories — Interview Narratives
## Satvik Jain | PM Interview Prep

---

# AMERICAN EXPRESS — CRR AML Modernization

---

## Version 1 — User-Centric Product Decisions

When I joined Amex to modernize their AML risk scoring engine, the organization's instinct was to replicate the existing 12-year-old system—Cadence—just faster and on cloud. My first call was to push back and spend the initial weeks purely in discovery before writing a single requirement.

I personally conducted 20+ UX research sessions with compliance analysts, managers, and MLRO officers. What I found changed our product direction. The main issues were lack of scalability, inefficient system, and legacy architecture—Cadence couldn't handle 30M+ daily transactions efficiently, rule changes took weeks to deploy across 40+ markets, and the monolithic design created operational bottlenecks. But a deeper insight emerged: analysts couldn't explain why a customer received a specific risk score. They were spending 12-15 minutes per alert just piecing together context from multiple screens before they could even begin an investigation.

Three assumptions I carried in proved wrong. First, analysts didn't want full automation—they wanted control and the ability to customize rules for their market's specific risks. Second, they cared less about individual score accuracy and more about consistency, explainability, and the ability to batch-review customer cohorts. Third, the five-dimension risk model didn't fit cleanly across all 40 markets—some jurisdictions needed custom dimensions.

These findings drove our three key capabilities. Asset Manager gave analysts self-serve control over the risk reference lists they'd previously had to route through Engineering—a 26-day cycle. Advanced Rule Configurations provided a visual, drag-and-drop rule builder so analysts could customize scoring logic without writing code. Sandbox Versioning let them test rule changes on historical customer cohorts without touching production.

Post-launch: time-to-investigation targeted from 12-15 minutes to under 4 minutes. Task completion rate went from 65% to 94%. Scoring latency dropped from 3-5 seconds to sub-2 seconds at 99th percentile.

**Key Details:** 20+ UX sessions | Scalability + explainability as core pain | 3 wrong assumptions corrected | Asset Manager, Advanced Rule Configurations, Sandbox Versioning | TTI 12-15 min→<4 min | Task Completion 65%→94%

**Anticipated Follow-ups:**
- How did you recruit participants for the research sessions?
- What did you do when your assumptions proved wrong?
- How did you prioritize which insights to act on?

---

## Version 2 — Prioritization and Trade-offs

When I took over as the first product owner for Amex's AML modernization, I inherited a scope of 10 Rally capabilities—all marked as critical by stakeholders. Engineering capacity: two scrum teams totaling 18 members, with aggressive quarterly SAFe PI cycles.

My first task was ruthless prioritization. I had to determine which of the 10 capabilities would ship in Phase 1 and which would defer to Phase 2. The output: 7 capabilities would ship in Phase 1 (CRR Framework & Configurability, Centralized Data Management, Governance & Authorization, Sandbox & Change Validation, Reporting & Notifications, Audit & Compliance Management, Customer Level Risk Scoring). Three were deferred to Phase 2: AI/ML Based Scoring, Integration with AML Ecosystem, and Entity Obligor & Onboarding API.

The hardest trade-off was Sandbox Versioning's depth. Compliance leadership loved it—a safe environment to test rule changes without touching production. But early testing showed lower predicted adoption compared to Asset Manager and Advanced Rule Configurations. I made the call to ship a lighter version of Sandbox Versioning while investing saved capacity into the rule builder UI—which had an 80% intimidation rate in its first prototype because it required analysts to write Boolean logic manually. We pivoted to a visual drag-and-drop builder in a 2-week UX redesign.

I also deliberately deferred advanced reporting, predictive analytics, and network analysis to Phase 2. These were Phase 1 asks from the analytics team. I framed it as: these features answer "what happened"—but Phase 1 needs to answer "what is the risk right now." That framing got buy-in without conflict.

Phase 1 delivered: 7 of 10 capabilities shipped, markets expanded from 5 to 40+, and I won Amex's Leadership Award + 6000 Blue Rewards within my first year.

**Key Details:** 10 Rally capabilities → 7 shipped Phase 1, 3 deferred | Sandbox Versioning lighter scope | Rule builder UX pivot (Boolean→drag-and-drop) | 5→40+ markets | Leadership Award + Blue Rewards

**Anticipated Follow-ups:**
- How did stakeholders react when capabilities were deferred?
- What would you have done differently with the prioritization?
- How did you handle the analytics team's pushback on deferring reporting?

---

## Version 3 — Led Cross-Functional Team Without Authority

As the product owner for an 18-member team at Amex—organized into 2 scrum teams (Rule Configuration ~12 members, Rule Execution ~6 members) spanning engineers, data engineers, QA, UX design, and UX research—I had zero managerial authority. My job was to move this team fast enough to deliver 7 of 10 Rally capabilities within quarterly SAFe PI cycles.

The challenge wasn't technical. It was trust and alignment. Engineering leads were skeptical of the aggressive timeline. Compliance stakeholders feared the new system would generate different scores than Cadence, creating audit confusion. Legal teams in each market had 3-4 week review cycles that would have blown the timeline.

I operated on three fronts simultaneously.

With engineering, I moved product decisions from bi-weekly to weekly steering meetings, used feature flags to deploy incomplete features safely, and ran two parallel workstreams so the Rule Configuration and Rule Execution teams weren't blocking each other. I also pushed for analyst-in-the-loop beta testing monthly rather than annual go-live gates.

With compliance, I proposed parallel runs: CRR and Cadence scoring the same customers side-by-side for 2 months, with full transparency on differences. The divergence data actually became our strongest selling point—in the majority of cases where scores differed, CRR's score was more defensible because of explainable rule logic vs. Cadence's black-box output. The MLRO stopped being a skeptic and started presenting our work as a risk reduction initiative.

With legal, I built a review playbook—templates and pre-approved rule patterns—that compressed their review cycle from 3-4 weeks to 10 days, and switched them from sequential to parallel market reviews.

The result: Phase 1 shipped on time across 40+ markets, with compliance and legal teams as advocates rather than blockers. My VP recognized the cross-functional alignment specifically when nominating me for the Leadership Award.

**Key Details:** 18-member team, 2 scrum teams, no managerial authority | Parallel workstreams + feature flags + weekly steering | 2-month parallel runs with Cadence | Legal review: 3-4 weeks → 10 days | Leadership Award

**Anticipated Follow-ups:**
- What was your biggest failure leading this team?
- How did you handle an engineer who disagreed with your prioritization?
- How did you keep the team motivated on aggressive timelines?

---

## Version 4 — Delivered Measurable Business Impact

The AML risk scoring engine I was modernizing at Amex powered compliance decisions for 30M+ daily transactions across 40+ markets. The legacy system Cadence had critical problems: it couldn't explain risk scores, scoring latency was 3-5 seconds during peak hours (violating the sub-2-second onboarding SLA), and even minor compliance updates took weeks to deploy.

I led the product from discovery through launch. Through 20+ user research sessions, I identified the core gaps and drove the solution across 10 Rally capabilities, delivering 7 in Phase 1.

The numbers post-launch: time-to-investigation targeted from 12-15 minutes to under 4 minutes. Task completion rate jumped from 65% to 94%. Score interpretation error rate dropped from 18% to 2%. Scoring latency hit sub-2 seconds at 99th percentile. Markets expanded from 5 to 40+.

On the Asset Manager capability specifically: list update cycle time fell from 26 days to 3.2 days—an 84% improvement—through copy-on-write architecture enabling market customization without breaking enterprise consistency. Manual engineering workarounds dropped from 40 per month to 2 (95% reduction). 400+ assets promoted to production with zero production incidents and 99.95% uptime.

Beyond the analyst experience, the business impact was structural. We unlocked 5 high-compliance jurisdictions previously deemed too risky. Sub-2-second scoring accelerated customer onboarding with an 8% improvement in completion rates. The platform's audit logging and rule version control reduced regulatory risk—every score became defensible in an audit. ROI: breakeven in under 2 months.

Within my first year, I received Amex's Leadership Award + 6000 Blue Rewards.

**Key Details:** TTI: 12-15 min→<4 min | Task Completion 65%→94% | Score Errors: 18%→2% | Latency: 3-5s→<2s | Markets: 5→40+ | TTAU: 26 days→3.2 days | 400+ assets, 0 incidents | Leadership Award + Blue Rewards

**Anticipated Follow-ups:**
- How did you attribute the time reduction specifically to your changes?
- What metrics did you track during development vs. post-launch?
- What would you have done differently to drive even more impact?

---

## Version 5 — Innovation and Experimentation

In early 2025, Amex ran the Growth Hack—an 8-week company-wide innovation competition open to all teams globally with 400+ teams competing. I saw it as an opportunity to test something I'd been thinking about: whether AI could meaningfully accelerate the product management workflow itself.

The problem was real: PMs in Growth spent 30-40% of their time on backlog grooming—parsing raw ideas into structured stories, estimating story points, writing acceptance criteria, finding duplicates, mapping dependencies. SAFe-structured teams spent 4-8 hours per PI on grooming alone. This pain affected 150+ PMs across Amex.

I assembled a 6-person team (1 PM, 2 Backend/ML Engineers, 1 Frontend Engineer, 1 Data Scientist, 1 DevOps) and we built a multi-agent AI system for backlog grooming and solutioning—integrated with Jira. Four core agents: a Story Refinement Agent (raw input → structured SAFe stories with acceptance criteria), a Duplicate Detection Agent (embedding-based semantic similarity), a WSJF Prioritization Agent (Weighted Shortest Job First scoring with reasoning breakdown), and an Orchestrator Agent coordinating the workflow.

A key discovery from interviewing 8-10 PMs: they didn't want "fully autonomous AI writes stories." They wanted transparent augmentation—AI flags duplicates, suggests priorities, shows acceptance criteria drafts. The biggest surprise: duplicate detection was the deepest pain. PMs couldn't confidently tell if a story was genuinely new or just re-articulated.

We ranked #33 out of 400+ global teams. Automation coverage hit 87%, duplicate detection precision was 0.92, and beta PMs rated it 8.5/10 NPS. Post-launch, adoption grew from 5% to 35%, with realized time savings of 2.5 hours per PI per PM.

What I'm more proud of is what came after. I took that prototype and evolved it into an Agentic-Agile framework—expanding from 4 agents to a vision of 6+ agents covering sprint planning, risk analysis, and retrospective insights. My thesis: PMs will manage teams of AI agents the same way they manage human squads today.

**Key Details:** Growth Hack #33/400+ teams | 6-person team, 8 weeks | 4-agent multi-agent architecture | GPT-4, Jira integration | 87% automation coverage | 0.92 duplicate detection precision | 8.5/10 NPS | 2.5 hrs/PI saved | Agentic-Agile framework evolution

**Anticipated Follow-ups:**
- What were the limitations of your prototype?
- How did you handle LLM hallucination risk in a financial services context?
- What would it take to make this production-ready at enterprise scale?

---

## Version 6 — Stakeholder Communication

The hardest stakeholder moment in the AML modernization wasn't a conflict—it was managing fear. We were replacing a 12-year-old scoring system that represented institutional knowledge for 50+ compliance analysts. The reaction was predictable: distrust.

The MLRO—the person legally accountable for Amex's AML compliance—was my most critical stakeholder. Her concern was specific: what if the new system scored customers differently than Cadence? In an audit, that inconsistency becomes a liability.

My response was to make the comparison fully transparent. I proposed parallel runs—both systems scoring the same customers simultaneously for 2 months. I brought comparison data to our steering meetings every time, without hiding cases where scores diverged. Counterintuitively, the divergence data became our strongest selling point. In the majority of cases where scores differed, CRR's score was more defensible—better supported by explainable rule logic than Cadence's black-box output. The MLRO stopped being a skeptic and started presenting our work to the Chief Compliance Officer as a risk reduction initiative.

Market teams were a different challenge. They initially feared losing autonomy to enterprise governance. For the Asset Manager capability, I socialized the copy-on-write architecture through 4 regional sessions—demonstrating that market customization was preserved while enabling enterprise consistency. Turned skeptics into co-designers.

With engineering, they resisted the aggressive timeline for copy-on-write. Resolution: phased delivery (CRUD first, copy-on-write second, audit export third), reducing complexity per sprint while delivering safely.

The outcome: the MLRO, my VP, and market teams all became executive champions for the program. The roadmap didn't just get approved—it got protected from budget cuts. The project was framed as "non-discretionary risk mitigation" to the board.

**Key Details:** MLRO as critical stakeholder | 2-month parallel runs as transparency mechanism | Score divergence data as selling point | 4 regional sessions for copy-on-write buy-in | Phased delivery for engineering alignment | Stakeholder transformation: skeptics → champions

**Anticipated Follow-ups:**
- How did you handle a situation where a stakeholder disagreed with your recommendation?
- What would you have done if the parallel run data had shown CRR was less accurate?
- How did you manage upward communication when things went wrong?

---
---

# SPRINKLR — Use Case Hub, Walmart, Qatar

---

## Version 1 — User-Centric Product Decisions

When I started looking at why Sprinklr's Insights product had slow adoption despite being technically powerful, the answer wasn't in the product—it was in how people were asked to use it. Onboarding a new client required 4+ weeks of consultant involvement: manual keyword creation, manual dashboard configuration, manual theme setup. Users weren't failing because the product was bad; they were failing because the setup was designed for consultants, not customers.

I analyzed 1,500+ existing client dashboards across 15 industries to understand what the best-performing setups actually looked like—what questions executives were trying to answer, what data they needed surfaced automatically, and where the journey broke down. Three personas kept appearing: the analyst who needed raw data, the manager who needed trends, and the executive who needed a one-screen brief.

From that research, I built the framework that became the Use Case Hub's core: Listen → Learn → Act.

Listen: instead of manual keyword addition, hashtag inclusion, and executive handle tagging, I built an AI-powered entity generator. The user enters a brand name, and the system auto-generates keywords, handles, and hashtags by combining AI with Wikipedia enrichment. Still editable by the user, but the default was already accurate for most brands. Pre-built industry themes (sentiment, crisis, product mentions, executive mentions, campaign tracking) were pre-configured across 15 industries, so the system automatically created Topic → Themes → Data ingestion.

Learn: I built a template-based reporting engine with industry-specific and use-case-specific dashboard templates. When a client selected their brand, industry, and use case, the dashboard auto-populated—including 30 days of historical data backfill.

Act: I added smart alerts (threshold-triggered, routed to predefined executives) and scheduled reports (daily/weekly/monthly auto-delivered to leadership), so insights didn't sit in dashboards—they reached the right person automatically.

The result: client onboarding dropped from 4 weeks to approximately 1 week. Time-to-insight improved by 75%. The product went from consultant-dependent to genuinely self-serve for 1,500+ clients.

**Key Details:** 1,500+ dashboard analysis | 15 industries | 3 personas | Listen→Learn→Act framework | AI entity generator with Wikipedia enrichment | Template-based reporting engine | Smart alerts + scheduled reports | 4 weeks→1 week onboarding | 75% TTI improvement

**Anticipated Follow-ups:**
- How did you validate the Listen→Learn→Act framework before building it?
- What did you cut from the original scope?
- How did you handle clients whose industries weren't covered by your templates?

---

## Version 2 — Prioritization and Trade-offs

Building a 0→1 product at Sprinklr, I faced a prioritization problem that most PMs face but few talk about honestly: every stakeholder believed their use case was the most important one.

Sales wanted templates for their top enterprise verticals first. Customer Success wanted the Persona App—simplified UI for executive users—shipped before anything else because the full Sprinklr UI was overwhelming for executives and support tickets were high. Engineering wanted a phased rollout because the AI entity generator was architecturally complex. The VP wanted something shippable in 3 months.

My approach was to map everything against one question: what is the minimum we can ship that makes the self-serve promise feel real to a new client?

That forced a clear hierarchy. The AI entity generator and industry templates were non-negotiable—without them, the "automated setup" claim was hollow. The Persona App was important but not the entry point; a client needed to get value first before we optimized how they consumed it.

I made the call to sequence: templates and auto-setup first, Persona App second, advanced reporting third. I pushed back on Sales' request to prioritize their top enterprise verticals and instead picked the verticals with the most existing dashboard data—meaning our templates would be highest quality from day one.

The Persona App trade-off was the hardest. Customer Success was vocal. My argument: if we ship a simplified UI before clients trust the data they're seeing, we're making it easier to use a product people don't yet believe in. Fix the belief first, then the UI. CS reluctantly agreed.

We shipped in 3 months. Onboarding time dropped from 4 weeks to ~1 week. The Persona App followed in the next sprint—with pre-configured persona frameworks (Analyst, Manager, Executive) each with pre-defined permissions, optimized UI, simplified navigation, and custom dashboards. Deployment time fell from 5 hours to 1 hour (80% reduction).

**Key Details:** Clear sequencing rationale | Templates → Persona App → Reporting | Vertical selection by data quality | Onboarding 4 weeks→1 week | Persona deployment 5 hrs→1 hr (80% reduction) | 3 persona frameworks

**Anticipated Follow-ups:**
- How did you handle the CS pushback on the Persona App delay?
- What would you have done differently?
- How did you decide which verticals to prioritize?

---

## Version 3 — Led Cross-Functional Team Without Authority

The Walmart Spark Driver Support project was my most technically complex work at Sprinklr—and I had no formal authority over anyone involved.

The problem was real: Walmart's driver support team had thousands of complaints flowing through internal channels (calls, chats, tickets) and simultaneously escalating publicly on Reddit and X. Root cause identification took approximately 7 days because investigation was manual and siloed. A 7-day RCA loop meant the same issue generated repeat contacts for a full week, escalated publicly before the organization had clarity, and triggered leadership fire drills.

I led the solution definition from scratch. The team spanned business, sales, data scientists, and engineering—none of whom reported to me. My job was to create enough clarity and momentum that everyone moved in the same direction.

I started with the data unification logic—defining how internal support data and public social data would be joined using SQL-based backends with common keys (User ID, timestamps) to create a unified "total contacts" metric giving true ecosystem visibility. I designed the L1/L2/L3 issue taxonomy so data scientists had a classification structure to work with, rather than discovering this need mid-build.

When data scientists proposed a supervised learning approach for clustering, I pushed back based on the problem constraints: we didn't have clean labeled training data, and the issue categories were still evolving. I advocated for unsupervised ML clustering—semantically group complaints by similarity, then label the clusters. This let us start generating insights before the taxonomy was finalized.

With engineering, I kept scope tight by focusing the POC on the RCA engine first—unsupervised clustering, automated summarization, and crisis probability scoring—deferring auto-routing and predictive crisis scoring to phase two. This let us demonstrate value quickly.

The POC converted into a $1.2M ARR deal for Sprinklr. Time-to-insight dropped from 7 days to same-day—an 85% improvement. Support shifted from reactive investigation to proactive containment.

**Key Details:** Cross-functional team: business, sales, data science, engineering | SQL data unification | L1/L2/L3 taxonomy design | Supervised vs. unsupervised ML decision | Unsupervised clustering + automated summarization + crisis probability scoring | $1.2M ARR | 85% TTI improvement (7 days→same day)

**Anticipated Follow-ups:**
- How did you manage conflict between data scientists and engineering on approach?
- What was the biggest technical risk in this project?
- How did you keep the POC scope tight under stakeholder pressure?

---

## Version 4 — Delivered Measurable Business Impact

Walmart's driver support team was operating reactively. Complaints from thousands of drivers came through internal call logs, chats, and tickets—but also simultaneously escalated on Reddit and X, visible to the public before internal teams even knew the issue existed. Root cause identification took approximately 7 days, by which point repeat contacts had piled up and reputational damage was done.

I led the product definition for a GenAI-powered Insight Assistant that unified both data streams. The core architecture: a SQL-based backend joining internal support data with public social escalations using shared keys, creating a single "total contacts" metric that gave true ecosystem visibility—something neither data source provided alone.

On top of this unified dataset, I defined the AI layer: unsupervised ML clustering to group semantically similar complaints into root-cause themes, automated summarization to surface top recurring issues, and crisis probability scoring to flag emerging problems before they became public.

The business impact was twofold. Operationally: time-to-insight dropped from 7 days to same-day—an 85% reduction. Support teams shifted from reactive investigation to proactive containment, enabling end-of-day executive-ready issue summaries instead of weekly cadence RCA. Commercially: the POC converted directly into a $1.2M ARR deal, positioning Sprinklr as an AI-powered intelligence layer for enterprise support operations—not just a social listening tool.

That commercial outcome mattered beyond the number. It validated that the product I'd defined wasn't a feature—it was a new business category for Sprinklr: monetizable AI infrastructure.

**Key Details:** Unified internal + social data architecture | Unsupervised ML clustering | Crisis probability scoring | L1/L2/L3 issue taxonomy | TTI: 7 days→same day (85%) | $1.2M ARR deal conversion

**Anticipated Follow-ups:**
- How did you isolate the $1.2M ARR attribution to this feature specifically?
- What happened after the POC—did you track post-launch metrics?
- What would have happened if the unsupervised clustering produced poor quality clusters?

---

## Version 5 — Innovation and Experimentation

The problem with Sprinklr's Insights onboarding wasn't a UX problem—it was a knowledge transfer problem. Setting up a topic correctly required knowing your brand's relevant keywords, competitor handles, industry hashtags, and executive names. Most clients didn't have this knowledge organized. Manual keyword addition, manual hashtag inclusion, manual executive handle tagging, manual theme classification—every step required consultant involvement, and each new client took 4+ weeks to onboard.

My hypothesis: if we could automate the knowledge gathering, we could remove the consultant entirely.

I designed an AI-powered entity generator—a module where a user enters their brand name, and the system automatically generates a starter set of keywords, social handles, and hashtags. The approach combined Sprinklr's existing AI capabilities with Wikipedia API enrichment: brand name → entity extraction → social signal mapping. The output was editable, but it was already accurate for most brands out of the box.

Then I layered pre-built industry themes on top: sentiment, crisis, product mentions, executive mentions, and campaign tracking—pre-configured across 15 industries. The system automatically created Topic → Themes → Data ingestion, making the entire setup flow automated.

This was experimental—no one at Sprinklr had tried to automate topic creation this way. I had to convince engineering it was worth building before I had proof it worked. My argument: our biggest cost in sales cycles was the 4-week setup dependency. If we could cut that to under a week, we'd expand our addressable market to clients who couldn't afford or wait for a consultant.

The experiment worked. Onboarding time dropped from 4 weeks to approximately 1 week. The AI entity generator became the entry point of the entire Use Case Hub flow—the first thing every new client touched. Time-to-insight improved by 75%.

**Key Details:** AI entity generator: brand name→keywords/handles/hashtags auto-generated | Wikipedia API enrichment | Pre-built industry themes across 15 industries | Hypothesis-driven approach before proof existed | 4 weeks→1 week onboarding | 75% TTI improvement

**Anticipated Follow-ups:**
- What was the failure mode if the AI entity generator got things wrong?
- How did you test this before shipping to all clients?
- What would you have done if engineering had said no?

---

## Version 6 — Stakeholder Communication

The Qatar government project (Citizen Governance Bot—CGB) was unlike anything I'd worked on before. Our stakeholders weren't product managers or business analysts—they were government officials, and our user was the Prime Minister's Office.

The core need: monitor citizen sentiment in real time, detect emerging issues, track ministry performance, and understand public dissatisfaction across 4 intelligence streams—media monitoring with AI image recognition, social listening, mystery shopper/survey data, and a unified complaints system (social, helpline, chat, escalations). All streams had to be unified into one centralized intelligence layer.

I acted as Product Owner, owning the unified reporting architecture, 21 executive display screens designed for ministers (not analysts), the Prime Minister's mobile app customization, and Arabic localization.

The stakeholder challenge was layered. Government officials had very specific expectations—the displays needed to be optimized for glanceable insight with color-coded risk levels, alert prioritization, and executive readability. The mobile app needed to strip the full Sprinklr product down to simplified navigation and custom dashboards matching Qatar Government's visual identity. And Arabic right-to-left UI had to work natively.

I flagged early that machine translation wasn't sufficient for Arabic—it distorted gender context, had professional tone inconsistencies, and missed cultural nuances. I brought this to the VP as a scope addition, not a complaint, and we brought in native Arabic consultants for a full Arabic-first redesign.

For government stakeholders with unpredictable availability, I designed for asynchronous engagement: visual update walkthroughs instead of formal meetings, flagged decisions needing their input, and made it easy to respond on their schedule.

The impact: achieved 5-10 minute executive time-to-insight (our North Star—decision-grade clarity within one executive sitting), improved retention by 15%, and increased executive engagement. The project became part of Sprinklr's broader engagement with the State of Qatar.

**Key Details:** Government stakeholders, Prime Minister's Office | 4 unified intelligence streams | 21 executive display screens | Mobile app customization | Arabic localization from scratch with native consultants | Async stakeholder engagement | 5-10 min TTI | 15% retention improvement

**Anticipated Follow-ups:**
- How did you handle feedback from the government that contradicted your design judgment?
- What was the hardest cultural or localization decision you made?
- What would have broken if you hadn't caught the machine translation issue early?
