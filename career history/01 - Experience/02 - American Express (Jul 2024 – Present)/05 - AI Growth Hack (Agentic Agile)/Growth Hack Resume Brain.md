# AI GROWTH HACK (AGENTIC AGILE) – RESUME BRAIN DUMP

**Project**: AI-Driven Backlog Grooming & Solutioning MVP → Agentic-Agile Framework  
**Company**: American Express  
**Role**: Senior Associate Product Manager  
**Duration**: Jul 2024 – Present  
**Hackathon**: Amex Growth Hack 2025 (8 weeks, 400+ global teams)  
**Ranking**: #33 out of 400+ teams  
**Team**: 6 people (1 PM, 2 Backend/ML Engineers, 1 Frontend Engineer, 1 Data Scientist, 1 DevOps)

---

## RAW PROJECT CONTEXT

### The Problem (Raw Notes)
- PMs in Growth spend 30-40% of time on **backlog grooming**, not strategy
- SAFe-structured teams (18 members) spend 4-8 hours per PI on grooming
- Manual work: parsing raw ideas into structured stories, story point estimation, acceptance criteria, finding duplicates, mapping dependencies
- One PM had 200+ stories with unclear duplicates and dependencies
- PMs can't hire more resources → only option is AI automation
- Pain is REAL: affects 150+ PMs across Amex

### Initial Discovery Conversations
- Interviewed 8-10 PMs across Growth and adjacent teams
- Key insight: PMs don't want "fully autonomous AI writes stories." They want "AI flags duplicates, suggests priorities, shows acceptance criteria drafts"
- **Surprise**: Duplicate detection is a HUGE problem. PMs can't tell if a story is genuinely new or just re-articulated
- **Insight**: WSJF scoring (SAFe's Weighted Shortest Job First) is culturally complex—every team has slightly different mental model. Imposing strict algorithm without context creates friction

### Competitive Landscape Scan
- **Jira AI** (Atlassian's new LLM assistant): Chat-based story summarization, natural language search. Strong UI integration, weak at systematic duplicate detection or WSJF.
- **Linear AI**: Triage for engineering, not PM backlog grooming.
- **GitHub Copilot**: Code-focused, not product.
- **Existing PM tools** (Monday.com, Asana): Generic AI, no domain understanding of SAFe/WSJF.
- **Conclusion**: Build internal because Amex needs SAFe-native, compliance-aware tool that external vendors can't provide.

---

## SOLUTION DESIGN (Raw)

### Architecture Decision: Multi-Agent Orchestration
Why? 
- Single monolithic agent: harder to test, less interpretable
- Rule-based automation: brittle, can't handle semantic nuance
- **Multi-agent (CHOSEN)**: specialized agents, clear contracts, composable, testable, transparent to users

### Four Core Agents in MVP
1. **Story Refinement Agent**: Raw input → structured story (title, description, 3-5 acceptance criteria, story points estimate)
   - Uses chain-of-thought prompting
   - Apply SAFe story format ("As a [role], I want [capability], so that [benefit]")
   - Generate testable acceptance criteria (behavior-focused, not implementation-focused)

2. **Duplicate Detection Agent**: Semantic similarity detection
   - Embedding-based (OpenAI embeddings)
   - Cosine similarity scoring
   - Threshold: 0.75 = "question for PM", 0.85 = "likely duplicate"
   - Conservative approach (favor recall over precision)

3. **WSJF Prioritization Agent**: Business value prioritization
   - WSJF formula: (Business Value + Time Criticality + Risk Reduction) / Job Size
   - Feature engineer each component from story text
   - Output: score + reasoning breakdown
   - Key risk: bias/drift over time

4. **Orchestrator Agent**: Coordinate workflow
   - Route outputs to right agents
   - Present unified recommendation to PM
   - Coordinate across ceremonies (future)

### LLM Choice: GPT-4 (not GPT-3.5)
Why?
- GPT-3.5: generated coherent but nonsensical acceptance criteria (hallucination)
- GPT-4: better semantic reasoning about business context
- Cost tradeoff: GPT-4 more expensive, but better quality justifies cost
- Future optimization: fine-tune smaller model (Llama 2) on Amex data

### Prompt Engineering Approach
- Few-shot prompting: 5-6 exemplar stories to anchor expected format/tone/depth
- Explicit guardrails: "Don't mention implementation details like 'use Redis cache'"
- Chain-of-thought: "First extract intent, then apply SAFe format, then generate acceptance criteria"
- Iteration loops: tested with pilot PMs, refined based on feedback

### Did NOT use RAG initially
- RAG = Retrieval-Augmented Generation (query knowledge base before generating)
- MVP decision: too much infrastructure work
- Future enhancement: RAG would ground story generation in Amex-specific patterns (past decisions, templates, context)

---

## MVP DEVELOPMENT – 8 WEEK SPRINT (Raw Timeline)

### Week 1-2: Architecture & Prototyping
- Team sync on vision: "Multi-agent orchestration, end-to-end story workflow, SAFe-native"
- Decided on GPT-4, OpenAI embedding model, AWS Lambda for serverless inference
- Built first prototype of Story Refinement Agent
- Set up Jira integration skeleton

### Week 2-3: Core Features
- Deployed Duplicate Detection Agent with embedding similarity
- Built Jira connector to fetch backlog
- Simple web UI for story input

### Week 3-4: Prioritization
- Feature-engineered WSJF components (business value, time criticality, risk reduction, job size)
- Integrated WSJF agent into orchestrator
- First internal tests

### Week 4-5: Quality & Beta Testing
- Recruited 3 volunteer PMs for beta
- Feedback: "Show confidence scores on duplicates," "Let me override WSJF with custom weights," "Show reasoning breakdown"
- Iterated rapid-fire (daily fixes)

### Week 5-6: Extended Features & Risk Mitigation
- Dependency detection agent (simple, conservative version)
- Sprint planning recommendations (basic)
- Error handling, timeouts, fallback to rule-based logic
- Load testing with 500+ simulated stories

### Week 6-7: Production Hardening
- Audit trail logging (every AI decision, PM override)
- Output validation (sanity checks on hallucinations)
- API rate-limiting handling, caching strategy
- Monitoring setup

### Week 7-8: Demo & Polish
- Hackathon presentation preparation
- User guide documentation
- Gathered PM testimonials
- Final polishing

### Features That Made MVP
✓ Story Refinement (raw text → structured story with acceptance criteria)  
✓ Duplicate Detection (with confidence scores)  
✓ WSJF Prioritization (with component breakdown)  
✓ Jira Integration (read backlog, write drafts)  
✓ Web UI (story input + recommendation display)  

### Features Cut (Ruthless Prioritization)
✗ Retrospective insight generation (week 4 cut to focus on core)  
✗ Natural language explanation of WSJF (would require extra LLM pass, latency hit)  
✗ Confluence integration for runbooks (out of scope)  
✗ Fine-tuning GPT-4 on Amex data (too much infrastructure)  
✗ Automated dependency mapping across 10+ teams (risky, only tested with 3 teams)

---

## METRICS & SUCCESS MEASUREMENT

### Hackathon Success Metrics (What We Hit)
- **Automation Coverage**: 87% (target: >80%) – % of stories system could process
- **Duplicate Detection Precision**: 0.92 (target: >0.85)
- **Duplicate Detection Recall**: 0.78 (conservative, favor false negatives)
- **WSJF Scoring Accuracy**: Calibrated against 5 experienced PM ground truth
- **Time-to-Recommendation**: 2.3 seconds median (acceptable for user workflow)
- **User Satisfaction**: NPS 8.5/10 from 3 beta PMs ("Would definitely use in production")
- **Rubric Score**: 35/40 (excellent for AI complexity)
- **Final Ranking**: #33 out of 400+ global teams

### Post-Launch Metrics (Tracking Now)
- **Adoption Rate**: 35% of Growth PMs in early rollout (target: 80% by Q2)
- **Realized Time Savings**: 2.5 hours/PI per PM (50-60% of theoretical 60-70%)
- **Story Quality Improvement**: 15% fewer acceptance criteria gaps, 20% faster point convergence
- **Velocity Signal**: Early data suggests 8-12% higher story throughput (small sample, need more)
- **Adoption Curve**: Week 1-4 (beta), Week 5-8 (soft launch), Week 9+ (organic growth)

### North Star Metric
**PM Productivity Gain**: Reduction in backlog grooming time per PI as % of PM working hours  
Target: 60-70% reduction (recover 36-56 FTE-hours/week of PM capacity across organization)

---

## BUSINESS CASE (RAW CALCULATIONS)

### Cost-Benefit
- **Baseline**: 150 PMs × 30-40% time on grooming = 60-80 FTE-hours/week
- **With AI** (60-70% reduction): Recover 36-56 FTE-hours/week
- **Value of recovered capacity**: 36-56 hrs/week × 50 weeks/year × [VERIFY: PM fully-loaded annual cost] ÷ 2000 work-hours = **[VERIFY: annual value of recovered PM capacity]**
- **Cost**: MVP build (6 people, 8 weeks) ~$250K, ongoing (1-2 engineers) ~[VERIFY: ongoing annual cost]
- **ROI**: [VERIFY: ROI %] on [VERIFY: annual cost base]
- **Payback**: 6-8 weeks

### PM Productivity Multiplier
Beyond time savings, freed capacity enables:
- Deeper customer discovery (user research, interviews)
- Faster iteration cycles (sprint planning time 4-6 hrs → 1-2 hrs)
- Better upfront story quality (fewer rework cycles)
- Faster experimentation (hypothesis-driven prototyping)

---

## STAKEHOLDER MANAGEMENT – WHO TO CONVINCE

### Executive Leadership (CPO, VP Product)
**Pain point**: Cost, risk, ROI  
**Message**: "60-70% backlog grooming time reduction → [VERIFY: annual value of recovered PM capacity] on $200K cost"  
**Proof**: #33 ranking in 400+ team competition; phased rollout plan with go/no-go gates  
**Result**: ✓ Got budget and executive air cover

### Engineering Leadership
**Pain point**: Maintenance burden, respect for technical constraints  
**Message**: "Tool surfaces recommendations; engineers retain authority over feasibility"  
**Approach**: Built clear APIs, appointed senior engineer as design stakeholder, showed non-disruptive integration  
**Result**: ✓ Engineering bought in; became advocates

### Product PMs (End-Users) – MOST COMPLEX
**Pain point**: Job security, AI trust, creative flexibility  
**Approach**:
- Transparency: Show AI reasoning, confidence scores, side-by-side comparisons
- Gradual adoption: 1-week beta with volunteers, no forced adoption
- Messaging: "Co-pilot, not replacement. You make final calls. AI automates boring parts."
- Champions: Trained 2-3 PM evangelists who could speak credibly to peers
- Feedback loops: Weekly check-ins, rapid iteration based on feedback
- Testimonials: Documented success stories ("Saved me 3 hours last sprint")

**Result**: ✓ Adoption grew from 5% → 35% in 8 weeks post-launch

### Compliance & Governance – LONGEST APPROVAL CYCLE
**Pain points**: Data privacy, audit trail, hallucination risk, model transparency  
**Our approach**:
- **Data handling**: Stripped sensitive identifiers before sending to OpenAI; got Legal sign-off
- **Audit trail**: Every AI decision, PM override logged
- **Output validation**: Spot-checking for compliance violations
- **Governance board**: Monthly oversight with Compliance, Risk, Legal, Product
- **Transparency**: Honest about limitations ("AI can hallucinate, PMs must never blindly trust")

**Result**: ✓ Established data residency policy; flagged as requirement for enterprise rollout

---

## FAILURE MODES & MITIGATION (Raw Risk List)

### Critical Risks
1. **LLM Hallucination** (HIGH)
   - Symptom: AI generates false acceptance criteria or misunderstands business terms
   - Example: "Multi-language translation" for "See transaction history"
   - Mitigation: Output validation rules, few-shot anchoring, human spot-check in MVP phase, <5% hallucination rate bar

2. **WSJF Bias & Drift** (HIGH)
   - Symptom: AI systematically overscores certain story types (e.g., cost stories vs. CX stories)
   - Mitigation: Calibration study vs. PM ground truth, temporal monitoring, explicit hand-coded weights reflecting Amex strategy

3. **Duplicate Detection False Negatives** (HIGH)
   - Symptom: Two engineers build the same feature unknowingly
   - Mitigation: Embedding model choice (financial services trained), multi-signal detection (similarity + tags + team), feedback loop on PM overrides

4. **Duplicate Detection False Positives** (MEDIUM)
   - Symptom: "Faster search" vs. "Better search" flagged as duplicate; PM wastes time reviewing
   - Mitigation: Conservative threshold (0.75), confidence scoring, PM override with explanation

5. **Adoption Resistance** (MEDIUM-HIGH)
   - Symptom: PMs try once, find it buggy, revert to manual process; adoption plateaus at 20%
   - Mitigation: Ruthless UX focus, integration into Jira workflow, PM champions, rapid iteration cycles, success metrics sharing

6. **Catastrophic Scale Failure** (CRITICAL but LOW PROBABILITY)
   - Symptom: OpenAI API goes down during sprint planning; 50+ PMs blocked
   - Mitigation: Graceful degradation (fallback to rule-based), async processing with queuing, caching, multi-model strategy

---

## PERSONAL LEADERSHIP ROLE

### What I Owned (6-Person Team)
1. **Vision & Strategy** – Problem definition, pivot to broader Agentic-Agile platform, "augmentation not automation" philosophy
2. **Stakeholder Translation** – Between engineers (want elegant architecture) and PMs (want time savings now)
3. **Discovery & Requirements** – Interviewed 8-10 PMs, synthesized pain, prioritized roadmap
4. **Metrics Definition** – North star, leading indicators, measurement methodology
5. **Prioritization Under Pressure** – Weekly "cut feature" meetings; made calls on what to sacrifice (e.g., cut retrospective insights week 4)
6. **Compliance & Risk Navigation** – Primary contact with Legal, InfoSec, Audit for data privacy and governance
7. **Post-Hackathon Adoption** – Stayed engaged post-launch, recruited pilots, gathered feedback, built PM community

### What Fails Without Me
- **Strategic clarity under ambiguity**: Problem was fuzzy; I crystallized it. Another PM might have built only duplicate detection (missing broader platform opportunity).
- **Stakeholder trust**: Took months to build relationships. When I said "cut this," people trusted it. New PM wouldn't have that.
- **Persistence through iteration**: After hackathon, tool had bugs, adoption was slow. Lesser PM might have declared victory and moved on. I stayed engaged, evolved it.

### Replaceable
- Technical architecture: Engineers were capable
- Prompt engineering: Data scientist could have done this
- UI design: Frontend engineer was strong

---

## KEY INSIGHTS & LEARNINGS

### Discovery Learnings
- PMs don't want fully autonomous AI; they want transparent augmentation
- Duplicate detection is the deepest pain (not story generation)
- WSJF is culturally nuanced; can't impose algorithm without context

### Technical Learnings
- LLM hallucination is real but addressable (validation rules, few-shot anchoring)
- Explainability is non-negotiable in enterprise (vs. Jira AI which can be black-box)
- Confidence scores matter more than accuracy (PM trusts uncertain flag over false-positive certainty)
- Fallbacks are essential (if LLM fails, system gracefully degrades to rule-based)

### Product Learnings
- Metrics make ideas sticky (when we showed "2.5 hours saved," adoption accelerated)
- Adoption is 50% of the work (shipping is easy; getting users is hard)
- PM champions are more effective than top-down messaging
- Feedback loops drive improvement (every PM override is data)
- Trust building requires repeated communication and transparency
- Domain language matters ("WSJF," "PI," "acceptance criteria" vs. generic "score," "priority")

### Organizational Learnings
- Small autonomous teams ship fast (6 people, 8 weeks > large committee)
- Governance isn't bottleneck at fintech; it's advantage (compliance builds trust vs. competitors)
- Concrete problems convert better than vision ("4-8 hours grooming per PI" vs. "AI transformation")
- Compliance integration can be done alongside shipping (not gating factor if approached early)

---

## AGENTIC-AGILE FUTURE VISION (Post-MVP)

### Current MVP Scope
- Backlog grooming only
- Single team
- 4 agents (Story Refinement, Duplicate Detection, WSJF, Orchestrator)

### Post-Hackathon Evolution
PMs asked for more: "Sprint planning?" "Retrospectives?" "Risk analysis?"  
**Insight**: Entire Agile ceremony workflow is ripe for agent orchestration.

### Agentic-Agile Platform (6+ Agents)
1. **Backlog Grooming Agent** (MVP, evolved)
2. **Sprint Planning Agent** (new) – Recommends story selection, flags overcommit, predicts sprint risk
3. **Risk Analysis Agent** (new) – Scans for dependency count, compliance flags, technical debt, new team member uncertainty
4. **Retrospective Insights Agent** (new) – Analyzes sprint data (velocity, bugs, incidents), generates actionable insights (not just "what went well")
5. **Orchestrator Agent** (evolved) – Coordinates agents, surfaces holistic recommendations
6. **Incident Triage Agent** (future) – Maps production incidents back to backlog, recommends definition-of-done additions

### Long-Term Vision (2-3 Years)
- **Across SAFe hierarchy**: Team (current) → Program → Portfolio
- **Across product lifecycle**: Discovery (synthesize customer feedback) → Development → Launch (release planning) → Post-Launch (monitoring, adoption)
- **Cross-functional intelligence**: Engineer data (incidents, tech debt) + Product data (feedback, NPS) + Design data (usability) + Business data (revenue) = holistic recommendations
- **Example**: Retro correlates team velocity with design velocity, business priorities, customer impact

### Competitive Moat
1. **Domain data**: Every PM interaction = proprietary Amex prioritization pattern. Competitors can't access.
2. **Integrated deployment**: Baked into SAFe, Jira, HRIS, governance. High switching cost.
3. **Trust & adoption**: Rolling out gradually, building champions, creating community. By time competitors offer similar, Amex teams deeply embedded.
4. **Regulatory expertise**: Our agents understand AML, FCPA, sanctions, Dodd-Frank. External vendors don't have this.

---

## RAW QUOTABLE MOMENTS

- "We didn't build an autonomous system; we built an augmentation system."
- "The biggest surprise was the duplicate detection problem. PMs couldn't confidently say what was new."
- "WSJF is context-sensitive. Imposing a strict algorithm creates friction. We had to anchor the model with explicit Amex strategy."
- "Hallucination is second-order risk. First-order risk is adoption. Best technical system is useless without PM trust."
- "Compliance isn't a bottleneck at a fintech. It's a competitive advantage."
- "In a 6-person team, the PM is connective tissue, not the cleverest person."
- "Metrics make ideas sticky. When we said '2.5 hours saved,' adoption accelerated."
- "Start with concrete pain, not vision. 'Backlog grooming takes 4-8 hours per PI' resonates. 'AI transformation platform' is vaporware."
- "Small autonomous teams move fast. Large committees move slow."
- "Every PM override is data. We captured all of it and used it to improve the model."

---

## REMAINING OPEN QUESTIONS / FOLLOW-UP ITEMS

### Technical
- [ ] Fine-tuning smaller model (Llama 2) on Amex data to reduce GPT-4 dependency
- [ ] Implementing RAG for story generation grounding in Amex context
- [ ] On-premises inference deployment for data residency requirement
- [ ] Multi-model strategy (GPT-4 for complex reasoning, smaller model for simpler tasks)

### Product
- [ ] Extending to sprint planning agent (week 1 post-launch priority)
- [ ] Risk analysis agent for flagging high-dependency stories
- [ ] Retrospective insights agent (most requested feature post-launch)
- [ ] Integration with Slack/Teams for async workflows
- [ ] Performance monitoring dashboard for teams using tool

### Organizational
- [ ] Expanding beyond Growth to Risk, Operations, Cards divisions
- [ ] Community of practice for PM teams (knowledge sharing, best practices)
- [ ] Training program for new team adopters
- [ ] Governance board processes (monthly review, audit of AI recommendations)

### Commercial
- [ ] Potential to commercialize as B2B SaaS for financial services
- [ ] License model (on-premises deployment, data residency compliance)
- [ ] IP valuation of multi-agent orchestration architecture

---

## PROJECT STATISTICS

| Metric | Value |
|--------|-------|
| **Ranking** | #33 / 400+ teams |
| **Team Size** | 6 people |
| **Hackathon Duration** | 8 weeks |
| **LLM Used** | GPT-4 |
| **MVP Agents** | 4 |
| **Future Agents** | 6+ |
| **Automation Coverage** | 87% |
| **Duplicate Detection Precision** | 0.92 |
| **Duplicate Detection Recall** | 0.78 |
| **Time-to-Recommendation** | 2.3s |
| **User Satisfaction (NPS)** | 8.5/10 |
| **Hackathon Rubric Score** | 35/40 |
| **Post-Launch Adoption Rate** | 35% |
| **Realized Time Savings** | 2.5 hrs/PI per PM |
| **Theoretical Max** | 60-70% reduction |
| **Annual Value Potential** | [VERIFY: annual value] |
| **Annual Cost** | [VERIFY: annual cost] |
| **ROI** | 85-90% |
| **Payback Period** | 6-8 weeks |

---

Last updated: March 4, 2025  
Prepared for: Interview readiness, storytelling, strategic context
