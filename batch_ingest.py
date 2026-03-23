#!/usr/bin/env python3
"""
LifeOS Batch Ingest — Satvik's Career Stories
=============================================
Ingests all verified career stories into lifeos_vectors.
Each story → 8-12 atomic Q&A pairs → BGE embed → MongoDB.

Run:
  python3 batch_ingest.py [--dry-run] [--story N]
"""

import json
import subprocess
import sys
import uuid
import time
from datetime import datetime
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

# ── CONFIG ───────────────────────────────────────────────────────────────────
MONGO_URI = "mongodb://localhost:27017/?directConnection=true"
DB_NAME = "linkright"
COLLECTION = "lifeos_vectors"
BGE_MODEL = "BAAI/bge-base-en-v1.5"
RECORDED_DATE = "2026-03-23"

QA_PROMPT = """You are building a personal career knowledge base for Satvik Jain (IIT Delhi grad, Senior Product Manager).

From the career story below, generate {n} Q&A pairs for semantic vector search.

RULES (follow strictly):
1. Each question must be SIMPLE and SPECIFIC — one narrow thing only
2. Each answer must be SELF-CONTAINED — no "he/I/they" — always say "Satvik"
3. Answers must be FACTUAL, CONCISE (1-3 sentences), and independently useful
4. Cover: what happened, metrics/impact, skills used, people involved, lessons
5. Write in ENGLISH only
6. No overlap between Q&A pairs — each captures a different fact
7. Questions should be the kind a recruiter or Satvik himself would actually ask

Story:
{story}

Output ONLY valid JSON array, no markdown:
[
  {{"question": "...", "answer": "..."}},
  ...
]"""

# ── ALL 21 SOURCE STORIES ─────────────────────────────────────────────────────
STORIES = [
    {
        "id": "sprinklr-overview",
        "n_pairs": 8,
        "domain": "career",
        "category": "A",
        "event_date": "2022-04-25",
        "company": "Sprinklr",
        "tags": ["sprinklr", "career-timeline", "title-progression", "amer", "emea"],
        "text": """Satvik Jain joined Sprinklr on 25 April 2022 as a Product Implementation Consultant.
He was promoted to Senior Product Implementation Consultant in March 2023.
On 16 May 2024, he officially transitioned to Senior Product Analyst on the Sprinklr Insights Product team — a hard-won internal transition that required fighting through office politics.
He left Sprinklr on 30 July 2024 — total tenure: 2 years and 3 months.
Throughout his time, he worked primarily with AMER (Americas) and EMEA (Europe, Middle East, Africa) clients — all Fortune 100/500 brands.
On paper his final title was Senior Product Analyst, but in reality he was doing PM-level work from the start.
Sprinklr Insights products he mastered: Social Listening, Benchmarking, Media Insights, Product Insights, Location Insights, AI Studio, Data Engine, FPDI, Rule Engine, Sprinklr Engagement.
He did not have deep expertise in Sprinklr Service (case management) — only basic knowledge."""
    },
    {
        "id": "sprinklr-gold-medal",
        "n_pairs": 10,
        "domain": "achievement",
        "category": "A",
        "event_date": "2022-dd-mm",
        "company": "Sprinklr",
        "tags": ["gold-medal", "chi-score", "fortune-500", "recognition", "client-success"],
        "text": """Within his first 6 months at Sprinklr, Satvik achieved a Project CHI (Customer Health Index) score of 10/10 on 6 consecutive projects — all Fortune 100/500 brands across AMER and EMEA regions.
CHI is the rating a customer gives the implementation team about their experience (out of 10), shared with the success manager as feedback at project close.
This made Satvik globally famous within Sprinklr — he received the Gold Medal across all regions: APJ, EMEA, and AMER.
He also became the first consultant in his team to be a top performer across ALL Sprinklr Insights modules.
He received an appreciation email from the Director of Social Media of one of the top universities in the USA for being "deeply customer obsessed."
He also owned the Weekly Project Tracker for 150-200 projects across the AMER Theatre — an automated Excel tracker he built himself using formulas.
The first 6 client projects were: CircleK, Walgreens, Hyundai (Location Insights), AT&T, New York University (Benchmarking), New Balance Athletics (Social Listening).
He also worked on Costa Farms (Social Listening) and many other Fortune 100 brands.
His recognition from these achievements led to him being assigned to bigger and more impactful projects."""
    },
    {
        "id": "sprinklr-cgb-qatar",
        "n_pairs": 10,
        "domain": "career",
        "category": "A",
        "event_date": "2023-01-dd",
        "company": "Sprinklr",
        "tags": ["cgb-qatar", "sharek", "government", "nlp", "arabic", "32m-tcv", "largest-project"],
        "text": """From January 2023 to June 2023, Satvik worked on the CGB Qatar project — the largest project at Sprinklr at that time, worth $32 million TCV (Total Contract Value).
The project was to build a personalized iOS mobile app called "Sharek" for the Qatari government, enabling the Prime Minister's office to monitor citizen complaints across 40 ministries via NLP sentiment analysis.
Satvik delivered insights into governance issues in just 4 weeks.
He designed the Arabic localization, enforcing right-to-left UI adaptation, and built a smart alerts system for negative sentiment tracking, crisis monitoring, and executive monitoring.
Results: 7-day retention improved from 40% to 55%; time-to-insight reduced from 2 days to 2 hours.
This project directly led to Satvik connecting with VP Anish Singhal to express his desire to transition into product management."""
    },
    {
        "id": "sprinklr-walmart-rca",
        "n_pairs": 8,
        "domain": "career",
        "category": "A",
        "event_date": "2023-06-dd",
        "company": "Sprinklr",
        "tags": ["walmart", "gen-ai", "ml", "contact-center", "rca", "unsupervised-learning"],
        "text": """From June 2023 to December 2023, Satvik worked on the Walmart Spark Driver Support project at Sprinklr.
He built a Gen-AI Assistant that analyzed 100,000+ contact center calls for Walmart Spark (gig economy driver platform).
The solution used unsupervised ML clustering and correlation detection to identify root causes of driver support issues.
The system auto-routed mitigation actions to the engineering and fraud teams, reducing manual triage work.
This was a technically complex project involving large-scale NLP on unstructured call data."""
    },
    {
        "id": "sprinklr-use-case-hub",
        "n_pairs": 10,
        "domain": "career",
        "category": "A",
        "event_date": "2024-01-dd",
        "company": "Sprinklr",
        "tags": ["use-case-hub", "ai-reporting", "de-facto-pm", "adoption", "revenue", "maternity-leave"],
        "text": """From January 2024 to June 2024, Satvik led the Use Case Hub product at Sprinklr — acting as de facto PM while the PM, Surabhi Goyal, was on maternity leave.
He designed a 2-step user journey for an AI-Reporting automation product that delivered complete dashboards in under 10 seconds, with 30 days of historical data, auto-alerts, and scheduled exports — driving 15% revenue increase in the first 3 months (his first months as a new PM).
He improved Use Case Hub adoption from 35% to 85% by conducting usability and A/B tests, integrating the solution into the main dashboard creation journey.
He eliminated the 7-day manual configuration process and enabled self-service for SME clients with under $1M ARR.
His official title during this period was still Senior Product Implementation Consultant (title changed to Senior Product Analyst only on May 16, 2024), but his work was fully PM-level — a fact he later used confidently in his Amex interview."""
    },
    {
        "id": "sprinklr-ai-models",
        "n_pairs": 10,
        "domain": "career",
        "category": "A",
        "event_date": "2023-dd-mm",
        "company": "Sprinklr",
        "tags": ["ai-models", "nlp", "discord", "adobe", "rolex", "mars-foods", "blackrock", "data-engine", "classification", "sentiment"],
        "text": """During his time at Sprinklr, Satvik worked on custom AI model development for several major brands.
For Rolex and Mars Foods, Satvik built proper end-to-end AI pipelines including classification models, sentiment analysis models, intent detection models, and phrase-level NLP models.
For Discord and Adobe, Satvik built custom AI models tailored to their social media and enterprise needs.
For Blackrock (in conjunction with Adobe) and Walmart, Satvik worked extensively on the Sprinklr Data Engine — creating data pipelines and AI-driven analytics.
Satvik was the only person in all of Sprinklr who had done Data Engine implementation work for both Blackrock and Walmart simultaneously.
This AI model work — classification, sentiment, intent, and phrase-level NLP — is highly relevant to the current AI era, and Satvik built it before AI became mainstream.
He worked primarily with AMER and EMEA clients throughout his tenure."""
    },
    {
        "id": "sprinklr-pavitar-incident",
        "n_pairs": 10,
        "domain": "personal",
        "category": "A",
        "event_date": "2022-12-dd",
        "company": "Sprinklr",
        "tags": ["workplace-trauma", "toxic-leadership", "pavitar-singh", "cto", "resilience", "public-humiliation"],
        "text": """In December 2022, Sprinklr's CTO Pavitar Singh began reviewing projects after someone at the annual sales event told him the implementation team was underperforming.
In a meeting with 40 directors and VPs, Pavitar gave brutal public feedback to Satvik — who had only 6-8 months of experience at that point.
Satvik was deeply hurt. After the meeting, he started crying, and in the next meeting he became quiet and shaken — it was his first real experience of workplace trauma and toxic leadership.
He then went to VP Anish Singhal to ask how leadership handles such feedback styles. Anish said: "Just move on, don't take it to heart."
The context: December 2022 was when everyone was on PTO and Satvik was managing 16 projects as backup. A minor miss happened on the Snapchat project — Satvik had proactively flagged the issue but his support consultant never followed through on the reminder, causing a customer input to be missed. This miss was used in the review.
After this incident, Satvik understood that upper leadership at Sprinklr was deeply toxic in its feedback style."""
    },
    {
        "id": "sprinklr-karthik-bn",
        "n_pairs": 10,
        "domain": "mentorship",
        "category": "A",
        "event_date": "2023-dd-mm",
        "company": "Sprinklr",
        "tags": ["karthik-bn", "true-leadership", "mentor", "people-leader", "sacrifice", "q2"],
        "text": """Karthik BN was Satvik's second manager at Sprinklr, and one of the most important people in Satvik's career.
After the Pavitar Singh incident, a Monday review call happened where Satvik and Karthik became misaligned on the Snapchat miss. The impression was created in front of VP Anish Singhal that it was Satvik's fault and Karthik was defending him.
Anish Singhal fired Karthik BN because of this.
The same day Karthik told Satvik about his promotion, Karthik also submitted his resignation.
Karthik joined Q2 under his previous leader Sanjeev Kalra.
Despite not being at fault, Karthik had taken the bullet for Satvik — he always shielded Satvik from the heat that came from upper leadership.
Satvik's reflection: "Galti na hote huye bhi, he took the bullet for me."
Karthik taught Satvik how to be a people leader — how to protect your team, how to take accountability, and what true leadership means.
Satvik still meets Karthik whenever he visits Bangalore.
Karthik is one of the three mentors Satvik credits for making him who he is today."""
    },
    {
        "id": "sprinklr-pulit-sharma",
        "n_pairs": 10,
        "domain": "mentorship",
        "category": "A",
        "event_date": "2024-dd-mm",
        "company": "Sprinklr",
        "tags": ["pulit-sharma", "mentor", "selfless-leadership", "pm-transition", "brother", "gurgaon"],
        "text": """Pulit Sharma was Satvik's third manager at Sprinklr and became like a brother to him.
Ironically, Pulit was appointed by the antagonist director Satyam Chugh — making him Satyam's one inadvertently good decision.
When it came time for Satvik's transition into the Product Management team, Pulit postponed his own opportunity and let Satvik go first.
He put Satvik ahead of himself.
Pulit taught Satvik how to be both a people leader AND a product leader — the most complete mentorship Satvik received at Sprinklr.
Satvik still meets Pulit regularly in Gurgaon.
Pulit is one of the three people Satvik credits with making him who he is: Keerthi Rondla (taught mentorship), Karthik BN (taught people leadership), and Pulit Sharma (taught people + product leadership)."""
    },
    {
        "id": "sprinklr-keerthi-mentorship",
        "n_pairs": 8,
        "domain": "mentorship",
        "category": "A",
        "event_date": "2022-04-dd",
        "company": "Sprinklr",
        "tags": ["keerthi-rondla", "first-manager", "mentor", "customer-success", "teaching", "hyderabad"],
        "text": """Keerthi Rondla was Satvik's first manager at Sprinklr and the person who taught him the fundamentals of customer-facing work.
She taught Satvik: how to communicate with customers, how to handle objections, how to train and teach other people the right way, and how to be a mentor.
Satvik also had a mentor named Kshitij Mundhada — his first project's lead consultant who eventually transitioned to a Customer Success Manager role. Kshitij mentored Satvik on the CircleK project (Social Listening + Benchmarking), and when Kshitij moved to CSM, Satvik took over leading CircleK. The client trusted Satvik more than the CSM due to his deep product knowledge and excellent work.
Satvik still meets Keerthi when he visits Hyderabad. Kshitij is also still in touch.
These relationships — Keerthi, Karthik, Pulit — are the three people Satvik credits for his career success."""
    },
    {
        "id": "sprinklr-satyam-revenge",
        "n_pairs": 10,
        "domain": "career",
        "category": "A",
        "event_date": "2024-05-dd",
        "company": "Sprinklr",
        "tags": ["satyam-chugh", "office-politics", "pm-transition", "revenge", "resilience", "amex"],
        "text": """Satyam Chugh was the director who replaced Karthik BN's position and became Satvik's manager at Sprinklr.
Satyam was a skilled political operator who rose through office politics and later became a Product Management Director.
He deliberately blocked Satvik's internal transition to Product Management — not for Satvik's benefit, but because he wanted to keep Satvik in implementation doing his work.
Satyam manipulated Satvik by saying "the product team is too toxic, don't go there" — while secretly planning his own move to product management.
He took all the onsite opportunities (Qatar, Riyadh, USA) for himself on company expenses, never giving Satvik a chance.
When Satvik finally got into PM via Pulit's support (Insights team), Satyam tried again — pulled Satvik to his advocacy team by dangling another PM opportunity.
Satvik, now fully understanding Satyam's pattern, played it smart: he pretended "Insights is boring" and joined Satyam's advocacy team.
But he had already spent 3 months carefully observing his PM Surabhi Goyal's full product management process, learned everything, and got his official title change to Senior Product Analyst on May 16, 2024.
The moment Satvik joined Satyam's advocacy team — American Express made him an offer.
Satvik took the Amex offer and left Sprinklr on July 30, 2024 — giving Satyam the exact feeling of being "left out" that Satyam had imposed on Satvik for years.
Satvik's philosophy: "Int ka jawaab paththar se dete hain sahi time aane par" (answer stone with stone at the right time)."""
    },
    {
        "id": "amex-overview-anuj",
        "n_pairs": 10,
        "domain": "career",
        "category": "A",
        "event_date": "2024-08-dd",
        "company": "American Express",
        "tags": ["amex", "anuj-kathwariya", "safe-agile", "user-stories", "rally", "18-person-team", "micromanagement"],
        "text": """Satvik joined American Express in August 2024 as Senior Associate Product Manager (also called Senior APM / Senior Associate Digital Product Management).
His first manager was Anuj Kathwariya — a kind, good-natured man but a poor individual contributor as a PM, and a heavy micromanager.
Anuj taught Satvik the fundamentals he hadn't learned at Sprinklr: Rally (Agile tracking tool), how to write user stories from scratch, SAFe Agile methodology.
The irony: Satvik had given his Amex interview with full confidence despite only having 5 days of official PM title experience at Sprinklr. He was confident because in reality he had done PM-level work for 2+ years.
Anuj started delegating Feature-level work (which in SAFe is the PM's responsibility) to Satvik.
Satvik's response: instead of complaining, he built direct visibility with his Director, explained the situation, and took full ownership of the CRR (Customer Risk Rating) Modernization project himself.
Anuj effectively became a figurehead while Satvik ran the show.
Satvik later led a team of 18 developers — becoming a trusted leader by influence, giving feedback, motivating and inspiring people."""
    },
    {
        "id": "amex-crr-tech",
        "n_pairs": 10,
        "domain": "career",
        "category": "A",
        "event_date": "2024-dd-mm",
        "company": "American Express",
        "tags": ["crr", "customer-risk-rating", "aml", "bigquery", "python", "pyspark", "kotlin", "modernization", "roadmap"],
        "text": """Satvik led the CRR (Customer Risk Rating) Modernization project at American Express — a 3-year roadmap he designed himself.
CRR is a system used in Anti-Money Laundering (AML) risk scoring. The old system ran on a legacy tool called Cadence (POD = Point of Departure).
Four major problems being solved: (1) Speed of scoring — old scoring was too slow; (2) UI/UX — outdated interface; (3) Configurability — hard to configure; (4) Audit & Reporting — weak tracking and reporting.
Technical solutions: 
  - Speed: Migrated from Python/PySpark/Mainframe database code to cloud tables via BigQuery, with event-based scoring triggers
  - New app: Built on Kotlin using latest Amex-aligned design standards and best-in-class architecture (POA = Point of Arrival)
  - Configurability: Reduced friction in configuration workflow
  - Audit: Improved depth of analysis, versioning, and reporting automation
Satvik designed the full 3-year roadmap. His manager helped strategically align it with the data roadmap (since CRR requires account and customer data for scoring).
He led 7 Program Increments (PIs) from PI 24.5 to PI 26.1."""
    },
    {
        "id": "amex-crr-pivots",
        "n_pairs": 10,
        "domain": "career",
        "category": "A",
        "event_date": "2025-dd-mm",
        "company": "American Express",
        "tags": ["crr", "strategic-pivot", "data-quality", "aml", "regulatory", "data-standardization"],
        "text": """The CRR Modernization project at American Express went through 3 major strategic pivots in 1.5 years:

Pivot 1 (end of PI 25.2): Originally planned to release with all modernized features by 2027. Then leadership changed scope — first deliver all existing Cadence (POD) features via lift-and-shift, validate scores, and decommission POD before moving to the new POA architecture. MVP1 scope became: POD lift-and-shift + score validation.

Pivot 2 (PI 25.5): AML investigation flagged higher risks in a regulatory audit. CRR product priority was reduced. New delivery target: 2028.

Pivot 3 (current, starting PI 26.2): Data quality issues — the underlying account and customer data used to calculate CRR scores was found to be unreliable. Leadership shut down CRR roadmap for at least PI 26.2 and 26.3. Satvik's focus completely shifted to data strategy: data translation, standardization, derivation, and categorization — building the data layer that CRR scoring needs.

This data work is expected to last 6-9 months minimum.

Satvik's role transformed from product roadmap execution to data strategy architect — working directly with 1100+ datapoints across 34 product portfolios."""
    },
    {
        "id": "amex-leadership-recognition",
        "n_pairs": 10,
        "domain": "achievement",
        "category": "A",
        "event_date": "2025-dd-mm",
        "company": "American Express",
        "tags": ["leadership-in-action", "g3l2", "g1l2", "blue-reward", "growthHack", "recognition", "rakly"],
        "text": """During his time at American Express, Satvik earned multiple significant recognitions:

1. Leadership in Action Award — received after taking full ownership of CRR Modernization and driving it autonomously. Also received G3L2 performance rating.

2. GrowthHack Competition (January 2025): Satvik finished rank 21 out of 400+ teams by building Rakly — a Slack bot that uses AI to help product managers groom user stories. The same idea later evolved into Shipquick (his open-source tool). Importantly, the same idea was later productionized by another Amex team — validation that the concept had real value.

3. G1L2 performance rating — achieved in 2025, higher than the previous G3L2. Multiple Blue Rewards from VP and Director for strong delivery.

4. Appreciation from RTE (Release Train Engineer) and Agile Champions for excellent backlog quality.

5. Became a trusted leader with 18 developers — led by influence, gave constructive feedback, motivated and inspired team members.

6. Gave an AI product demo to the VP of AI at American Express.

7. Supported the integration of Evan AI agent (by vendor Workfusion) in the financial screening space — negative news and media triage use case."""
    },
    {
        "id": "amex-strategic-visibility",
        "n_pairs": 8,
        "domain": "career",
        "category": "A",
        "event_date": "2025-03-dd",
        "company": "American Express",
        "tags": ["strategic-communication", "vp-gregory-liss", "workload", "pie-chart", "ownership", "visibility"],
        "text": """At a critical moment at American Express, Satvik was once again doing both the PM and PO (Product Owner) roles simultaneously without the corresponding title or support.
Instead of complaining, Satvik sent a strategic message to VP Gregory A. Liss acknowledging a deadline miss, taking full personal responsibility, and visually demonstrating the workload imbalance with a pie chart showing CRR was 55.8% of the total portfolio workload (DAM 20.9%, other areas 7% each).
He set his own internal deadlines — harder than official ones: Features by May 1, User Stories by May 15 for PI 25.3.
The subtext: one person cannot sustainably carry 55.8% of a portfolio's workload while doing PM+PO both.
VP Gregory Liss responded by hiring a Senior Product Manager, who joined in June.
After that, Satvik focused fully on flawless execution and strategic tradeoff management.
Satvik's pattern: never complain, always take ownership, use data to make systemic problems visible."""
    },
    {
        "id": "gogogo-investment",
        "n_pairs": 6,
        "domain": "career",
        "category": "A",
        "event_date": "2024-09-12",
        "company": "GoGoGo",
        "tags": ["gogogo", "angel-investment", "startup", "ride-hailing", "gig-economy", "investor"],
        "text": """On September 12, 2024, Satvik made his first angel investment in GoGoGo — a ride-hailing and gig economy platform focused on driver welfare.
The co-founders are Avinash Kumar and Gagan Sawhney (ex-McKinsey, Bain backgrounds).
Satvik is an investor and occasionally serves as partial Founder's Office / Chief of Staff for GoGoGo.
This investment gave Satvik constant exposure to early-stage startup thinking, fundraising, and operations — experience he applies to building LinkRight.
Satvik's role is passive investor primarily; he is not operationally involved in day-to-day GoGoGo decisions."""
    },
    {
        "id": "contentstack-sukha-freelance",
        "n_pairs": 8,
        "domain": "career",
        "category": "A",
        "event_date": "2024-11-dd",
        "company": "Contentstack / Sukha Education",
        "tags": ["contentstack", "sukha-education", "freelance", "ai-pm", "ngo", "strategy-consultant"],
        "text": """From November 2024 to June 2025, Satvik freelanced as an AI Product Manager for Contentstack — a headless CMS company.
This gave him hands-on experience with AI product management outside his Amex role, exposure to different product development environments, and additional income.

From January 2025 to May 2025, Satvik worked with Sukha Education as a Strategy Consultant.
Sukha Education is an NGO focused on education.
This role gave Satvik experience in social impact strategy and nonprofit sector consulting — aligned with his long-term vision of building the Jain Group of Companies with social impact as a core pillar."""
    },
    {
        "id": "linkright-entrepreneurship",
        "n_pairs": 10,
        "domain": "career",
        "category": "A",
        "event_date": "2025-07-dd",
        "company": "LinkRight",
        "tags": ["linkright", "entrepreneurship", "solopreneur", "ai-platform", "github", "product-building"],
        "text": """In July 2025, Satvik started building LinkRight — his AI Transformation Platform and his most ambitious project to date.
LinkRight's vision: "Turn any complex life goal into a structured, AI-executed transformation."
Core formula: Complex Goal → SAFe Breakdown → Vector Context Pull → Agent Execution → Beads Tracking → Outcome.
Satvik initially tried to build a team but struggled with finding the right co-founders and developers. He chose solopreneurship — building everything himself.
As of March 2026, Satvik has 25 repositories on GitHub and 250+ contributions in the last year — a testament to consistent execution despite setbacks.
He has experienced multiple failures building LinkRight — wrong tech choices, scope creep, team dynamics, pivot after pivot.
Satvik's approach: solve his own problems first (job search, content, career management), then productize for others.
LinkRight modules built: Sync (career transformation), Flex (LinkedIn content), LifeOS (AI Second Brain), AutoFlow (workflow automation), Squick (SDLC), LRB (module builder).
His long-term vision: build the "Jain Group of Companies" over 40-50 years — diversified, socially impactful, inspired by Ratan Tata. Dream: billionaire."""
    },
    {
        "id": "iit-delhi-background",
        "n_pairs": 8,
        "domain": "education",
        "category": "A",
        "event_date": "2018-dd-mm",
        "company": "IIT Delhi",
        "tags": ["iit-delhi", "civil-engineering", "education", "jee-advanced", "cgpa", "college"],
        "text": """Satvik Jain graduated from IIT Delhi with a degree in Civil Engineering, achieving a CGPA of 6.43.
He cleared JEE Advanced to get into IIT Delhi — a highly competitive national entrance exam.
The JEE Advanced experience involved a blackout story — Satvik has shared that he went through an extreme high-pressure situation during the exam, demonstrating his resilience.
Despite being a Civil Engineering graduate, Satvik chose not to work in Civil Engineering — he pivoted to product management and technology.
He declined a job offer from PwC after IIT to bet on himself and explore entrepreneurship.
He also declined admissions/opportunities from Masters Union and MBA programs to pursue entrepreneurship instead.
He has 5 years of classical vocal training — an unusual achievement for an IIT graduate.
Satvik mentored his sister Sanika to IIT — she is now an SDE2 at Oracle. He also mentored a laid-off colleague from zero to an APM role at Next Wave."""
    },
    {
        "id": "personal-resilience",
        "n_pairs": 8,
        "domain": "personal",
        "category": "A",
        "event_date": "2010-dd-mm",
        "company": None,
        "tags": ["resilience", "father", "canara-bank", "family", "mental-strength", "jain-group"],
        "text": """Satvik lost his father in 2010 when he was 11 years old. His father was a Canara Bank manager who died by suicide.
His father was deeply invested in Satvik's holistic development — abacus, music, travel, academics. He was loving and present.
After his father's death, Satvik became the "man of the family" overnight at age 11.
He rarely lets himself think about his father because it makes him cry — the love is still very much there.
In his first year at IIT Delhi, Satvik experienced depression after being ghosted by someone he loved, going into complete social isolation. He recovered through his roommate Samarth and his current girlfriend (6+ years together, planning to marry in 2027).
At Sprinklr, he experienced burnout.
Despite all this — loss, depression, burnout, professional setbacks — Satvik has a resilience that is almost hard to believe.
His inspiration is Ratan Tata. His vision: build the Jain Group of Companies over 40-50 years — diversified, socially impactful, people-developing.
He has a sister, Sanika, who is an SDE2 at Oracle — he mentored her to IIT."""
    },
]

# ── CORE FUNCTIONS ─────────────────────────────────────────────────────────
_model = None

def get_model():
    global _model
    if _model is None:
        print("Loading BGE model...", flush=True)
        _model = SentenceTransformer(BGE_MODEL)
        print("BGE model loaded.", flush=True)
    return _model

def embed(text: str) -> list:
    model = get_model()
    vec = model.encode(f"Represent this sentence: {text}", normalize_embeddings=True)
    return vec.tolist()

def generate_qa(story_text: str, n: int) -> list:
    prompt = QA_PROMPT.format(story=story_text.strip(), n=n)
    result = subprocess.run(
        ["claude", "--print"],
        input=prompt, capture_output=True, text=True, timeout=90
    )
    if result.returncode != 0:
        raise RuntimeError(f"Claude error: {result.stderr[:200]}")
    raw = result.stdout.strip()
    start = raw.find("[")
    end = raw.rfind("]") + 1
    if start == -1:
        raise ValueError(f"No JSON in response: {raw[:200]}")
    return json.loads(raw[start:end])

def insert_docs(docs: list):
    client = MongoClient(MONGO_URI)
    coll = client[DB_NAME][COLLECTION]
    result = coll.insert_many(docs)
    client.close()
    return len(result.inserted_ids)

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    dry_run = "--dry-run" in sys.argv
    specific = None
    for arg in sys.argv:
        if arg.startswith("--story="):
            specific = int(arg.split("=")[1]) - 1

    stories_to_run = STORIES if specific is None else [STORIES[specific]]

    print(f"\n{'='*60}")
    print(f"LifeOS Batch Ingest — {len(stories_to_run)} stories")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE INSERT'}")
    print(f"{'='*60}\n")

    get_model()  # pre-load

    total_vectors = 0
    total_errors = 0

    for i, story in enumerate(stories_to_run):
        story_id = uuid.uuid4().hex[:12]
        print(f"\n[{i+1}/{len(stories_to_run)}] {story['id']}")
        print(f"  Domain: {story['domain']} | Date: {story['event_date']} | Pairs: {story['n_pairs']}")

        try:
            qa_pairs = generate_qa(story["text"], story["n_pairs"])
            print(f"  Claude generated: {len(qa_pairs)} Q&A pairs")

            if dry_run:
                for j, qa in enumerate(qa_pairs[:3]):
                    print(f"  Sample [{j+1}] Q: {qa['question'][:70]}")
                    print(f"           A: {qa['answer'][:80]}")
                print(f"  [DRY RUN — not inserting]")
                continue

            docs = []
            for qa in qa_pairs:
                vec = embed(qa["answer"])
                doc = {
                    "_id": f"lifeos-{story_id}-{uuid.uuid4().hex[:8]}",
                    "question": qa["question"],
                    "answer": qa["answer"],
                    "story_id": story_id,
                    "story_slug": story["id"],
                    "domain": story["domain"],
                    "category": story["category"],
                    "event_date": story["event_date"],
                    "recorded_date": RECORDED_DATE,
                    "company": story.get("company"),
                    "tags": story.get("tags", []),
                    "embedding": vec,
                    "embedding_model": BGE_MODEL,
                    "embedding_dims": 768,
                    "verified": True,
                    "version": 1,
                    "created_at": datetime.utcnow()
                }
                docs.append(doc)

            inserted = insert_docs(docs)
            total_vectors += inserted
            print(f"  ✅ Inserted {inserted} vectors")

        except Exception as e:
            print(f"  ❌ Error: {e}")
            total_errors += 1
            time.sleep(2)
            continue

        time.sleep(1)  # rate limit buffer

    print(f"\n{'='*60}")
    print(f"DONE: {total_vectors} vectors inserted | {total_errors} errors")

    # Final count
    client = MongoClient(MONGO_URI)
    count = client[DB_NAME][COLLECTION].count_documents({})
    client.close()
    print(f"Total in lifeos_vectors: {count}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
