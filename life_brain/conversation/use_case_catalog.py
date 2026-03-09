"""
Use Case Catalog — 40+ conversation templates across 7 life domains.

Data-driven catalog with semantic descriptions for embedding-based matching.
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class UseCaseCategory(str, Enum):
    """Seven life domains for guided conversations."""
    CAREER = "career"           # 12 use cases
    RELATIONSHIPS = "relationships"  # 7 use cases
    HEALTH = "health"           # 6 use cases
    FINANCE = "finance"         # 5 use cases
    PERSONAL_GROWTH = "personal_growth"  # 6 use cases
    CREATIVITY = "creativity"   # 3 use cases
    MEMORY = "memory"           # 2 use cases


@dataclass
class UseCase:
    """A single guided conversation use case."""

    use_case_id: str              # e.g., "C1", "R1", "H1"
    title: str                    # e.g., "Interview Prep: Technical Interviews"
    category: UseCaseCategory     # Domain
    description: str              # Long-form semantic description (for embedding)
    expert_assigned: str          # Expert persona (e.g., "Satya", "Richard")
    keywords: List[str]           # Keywords for fallback matching
    difficulty_level: str         # "beginner", "intermediate", "advanced"
    estimated_duration_min: int   # Time needed (minutes)
    prerequisite_uc: Optional[str] = None  # Prior use case if any


class UseCaseCatalog:
    """Manages 40+ use case catalog across 7 categories."""

    def __init__(self):
        """Initialize catalog with all 40+ use cases."""
        self.use_cases: List[UseCase] = self._build_catalog()
        self._by_id = {uc.use_case_id: uc for uc in self.use_cases}
        self._by_category = {}
        for uc in self.use_cases:
            if uc.category not in self._by_category:
                self._by_category[uc.category] = []
            self._by_category[uc.category].append(uc)

    def _build_catalog(self) -> List[UseCase]:
        """Build complete 40+ use case catalog."""
        return [
            # === CAREER (12) ===
            UseCase(
                use_case_id="C1",
                title="Interview Prep: Technical Interviews",
                category=UseCaseCategory.CAREER,
                description="Prepare for technical coding interviews. Cover algorithm problems, system design, behavioral questions. Get tips from interviewer experts.",
                expert_assigned="Satya",
                keywords=["interview", "coding", "algorithm", "leetcode", "technical"],
                difficulty_level="intermediate",
                estimated_duration_min=45,
            ),
            UseCase(
                use_case_id="C2",
                title="Interview Prep: Behavioral Questions",
                category=UseCaseCategory.CAREER,
                description="Master behavioral interview questions using STAR method. Tell compelling stories about your achievements, challenges, and learnings.",
                expert_assigned="Satya",
                keywords=["behavior", "star", "story", "experience", "achievement"],
                difficulty_level="beginner",
                estimated_duration_min=30,
            ),
            UseCase(
                use_case_id="C3",
                title="Career Planning: Next Move Strategy",
                category=UseCaseCategory.CAREER,
                description="Develop a strategic plan for your next career move. Evaluate companies, roles, compensation, growth opportunities, and culture fit.",
                expert_assigned="Indra",
                keywords=["career", "planning", "strategy", "next move", "job change"],
                difficulty_level="intermediate",
                estimated_duration_min=50,
            ),
            UseCase(
                use_case_id="C4",
                title="Salary Negotiation: Getting Your Worth",
                category=UseCaseCategory.CAREER,
                description="Learn to negotiate compensation effectively. Understand market rates, build your case, handle counteroffers, and close strong.",
                expert_assigned="Chris",
                keywords=["salary", "negotiation", "compensation", "equity", "package"],
                difficulty_level="advanced",
                estimated_duration_min=40,
            ),
            UseCase(
                use_case_id="C5",
                title="Leadership Skills: Managing Up & Down",
                category=UseCaseCategory.CAREER,
                description="Develop leadership skills including delegation, feedback, conflict resolution, and stakeholder management.",
                expert_assigned="Andy",
                keywords=["leadership", "management", "delegation", "feedback", "team"],
                difficulty_level="intermediate",
                estimated_duration_min=55,
            ),
            UseCase(
                use_case_id="C6",
                title="Project Execution: Shipping at Scale",
                category=UseCaseCategory.CAREER,
                description="Execute large-scale projects from conception to launch. Cover planning, resource allocation, risk management, and delivery.",
                expert_assigned="Jeff",
                keywords=["project", "execution", "shipping", "scale", "delivery"],
                difficulty_level="advanced",
                estimated_duration_min=60,
            ),
            UseCase(
                use_case_id="C7",
                title="Startup Basics: Building from Scratch",
                category=UseCaseCategory.CAREER,
                description="Start your own company. Cover idea validation, fundraising, team building, product-market fit, and growth strategy.",
                expert_assigned="Reed",
                keywords=["startup", "founder", "fundraising", "venture", "build"],
                difficulty_level="advanced",
                estimated_duration_min=75,
            ),
            UseCase(
                use_case_id="C8",
                title="Personal Brand: Visibility & Influence",
                category=UseCaseCategory.CAREER,
                description="Build your personal brand through writing, speaking, networking, and strategic visibility to expand opportunities.",
                expert_assigned="Reed",
                keywords=["brand", "visibility", "influence", "speaking", "writing"],
                difficulty_level="intermediate",
                estimated_duration_min=35,
            ),
            UseCase(
                use_case_id="C9",
                title="Work-Life Balance: Avoiding Burnout",
                category=UseCaseCategory.CAREER,
                description="Maintain healthy balance between career ambitions and personal life. Set boundaries, manage stress, sustain energy.",
                expert_assigned="Esther",
                keywords=["burnout", "balance", "stress", "wellness", "boundaries"],
                difficulty_level="beginner",
                estimated_duration_min=25,
            ),
            UseCase(
                use_case_id="C10",
                title="Technical Debt: Long-term Thinking",
                category=UseCaseCategory.CAREER,
                description="Manage technical debt and architectural decisions. Balance shipping fast with building foundations that scale.",
                expert_assigned="Richard",
                keywords=["technical", "debt", "architecture", "design", "foundation"],
                difficulty_level="advanced",
                estimated_duration_min=50,
            ),
            UseCase(
                use_case_id="C11",
                title="Productivity: Deep Work & Focus",
                category=UseCaseCategory.CAREER,
                description="Maximize your productivity with deep work, focus blocks, environment design, and elimination of distractions.",
                expert_assigned="Andy",
                keywords=["productivity", "focus", "deep work", "efficiency", "time"],
                difficulty_level="beginner",
                estimated_duration_min=30,
            ),
            UseCase(
                use_case_id="C12",
                title="Career Transition: Changing Domains",
                category=UseCaseCategory.CAREER,
                description="Transition to a new industry or domain. Leverage transferable skills, build credibility, overcome imposter syndrome.",
                expert_assigned="Indra",
                keywords=["transition", "change", "domain", "pivot", "new"],
                difficulty_level="intermediate",
                estimated_duration_min=45,
            ),

            # === RELATIONSHIPS (7) ===
            UseCase(
                use_case_id="R1",
                title="Relationships: Deep Connections",
                category=UseCaseCategory.RELATIONSHIPS,
                description="Build meaningful, lasting relationships. Develop empathy, vulnerability, active listening, and authentic connection.",
                expert_assigned="Esther",
                keywords=["relationship", "connection", "empathy", "vulnerability", "friendship"],
                difficulty_level="beginner",
                estimated_duration_min=35,
            ),
            UseCase(
                use_case_id="R2",
                title="Family Dynamics: Understanding Your System",
                category=UseCaseCategory.RELATIONSHIPS,
                description="Understand your family system, generational patterns, and improve family relationships with awareness and compassion.",
                expert_assigned="Esther",
                keywords=["family", "parents", "siblings", "dynamics", "patterns"],
                difficulty_level="intermediate",
                estimated_duration_min=50,
            ),
            UseCase(
                use_case_id="R3",
                title="Conflict Resolution: Hard Conversations",
                category=UseCaseCategory.RELATIONSHIPS,
                description="Handle conflict constructively. Master difficult conversations, clear communication, and find win-win solutions.",
                expert_assigned="Chris",
                keywords=["conflict", "difficult", "conversation", "resolution", "communication"],
                difficulty_level="intermediate",
                estimated_duration_min=40,
            ),
            UseCase(
                use_case_id="R4",
                title="Boundaries: Saying No with Grace",
                category=UseCaseCategory.RELATIONSHIPS,
                description="Set healthy boundaries in personal and professional relationships. Say no, protect energy, and maintain respect.",
                expert_assigned="Brené",
                keywords=["boundaries", "no", "limits", "protection", "respect"],
                difficulty_level="beginner",
                estimated_duration_min=30,
            ),
            UseCase(
                use_case_id="R5",
                title="Dating & Romance: Finding Your Person",
                category=UseCaseCategory.RELATIONSHIPS,
                description="Navigate dating and romance. Understand attachment styles, red flags, healthy relationships, and compatibility.",
                expert_assigned="Esther",
                keywords=["dating", "romance", "love", "partner", "attachment"],
                difficulty_level="intermediate",
                estimated_duration_min=45,
            ),
            UseCase(
                use_case_id="R6",
                title="Networking: Building Professional Networks",
                category=UseCaseCategory.RELATIONSHIPS,
                description="Build authentic professional networks. Develop genuine relationships, ask for help, and create mutual value.",
                expert_assigned="Reed",
                keywords=["networking", "connections", "professional", "community", "reach"],
                difficulty_level="intermediate",
                estimated_duration_min=35,
            ),
            UseCase(
                use_case_id="R7",
                title="Loneliness & Isolation: Finding Community",
                category=UseCaseCategory.RELATIONSHIPS,
                description="Address loneliness and find community. Build a tribe, overcome social anxiety, create belonging.",
                expert_assigned="Esther",
                keywords=["lonely", "isolation", "community", "tribe", "belong"],
                difficulty_level="beginner",
                estimated_duration_min=40,
            ),

            # === HEALTH (6) ===
            UseCase(
                use_case_id="H1",
                title="Fitness: Building a Sustainable Practice",
                category=UseCaseCategory.HEALTH,
                description="Create a sustainable fitness routine. Cover goal setting, habit formation, recovery, and long-term health.",
                expert_assigned="Andrew",
                keywords=["fitness", "exercise", "gym", "workout", "health"],
                difficulty_level="beginner",
                estimated_duration_min=30,
            ),
            UseCase(
                use_case_id="H2",
                title="Nutrition: Eating for Energy",
                category=UseCaseCategory.HEALTH,
                description="Optimize nutrition for energy and longevity. Understand metabolics, choose foods, build eating habits.",
                expert_assigned="Andrew",
                keywords=["nutrition", "diet", "eating", "food", "metabolism"],
                difficulty_level="beginner",
                estimated_duration_min=35,
            ),
            UseCase(
                use_case_id="H3",
                title="Sleep: Mastering Rest & Recovery",
                category=UseCaseCategory.HEALTH,
                description="Improve sleep quality and quantity. Understand circadian rhythm, sleep hygiene, and recovery protocols.",
                expert_assigned="Andrew",
                keywords=["sleep", "rest", "recovery", "energy", "circadian"],
                difficulty_level="beginner",
                estimated_duration_min=25,
            ),
            UseCase(
                use_case_id="H4",
                title="Mental Health: Anxiety & Depression",
                category=UseCaseCategory.HEALTH,
                description="Address anxiety and depression. Learn coping strategies, when to seek help, and building resilience.",
                expert_assigned="Brené",
                keywords=["anxiety", "depression", "mental", "health", "therapy"],
                difficulty_level="intermediate",
                estimated_duration_min=45,
            ),
            UseCase(
                use_case_id="H5",
                title="Meditation & Mindfulness: Inner Peace",
                category=UseCaseCategory.HEALTH,
                description="Develop meditation and mindfulness practice. Reduce stress, increase focus, find inner peace.",
                expert_assigned="Sadhguru",
                keywords=["meditation", "mindfulness", "peace", "consciousness", "awareness"],
                difficulty_level="beginner",
                estimated_duration_min=30,
            ),
            UseCase(
                use_case_id="H6",
                title="Chronic Pain: Living Well With It",
                category=UseCaseCategory.HEALTH,
                description="Manage chronic pain without losing quality of life. Strategies, tools, and mindset shifts for resilience.",
                expert_assigned="Andrew",
                keywords=["pain", "chronic", "management", "relief", "living"],
                difficulty_level="intermediate",
                estimated_duration_min=50,
            ),

            # === FINANCE (5) ===
            UseCase(
                use_case_id="F1",
                title="Investing Basics: Building Wealth",
                category=UseCaseCategory.FINANCE,
                description="Start investing and build long-term wealth. Cover stocks, ETFs, index funds, diversification, and compound growth.",
                expert_assigned="Warren",
                keywords=["investing", "stocks", "etf", "wealth", "compound"],
                difficulty_level="intermediate",
                estimated_duration_min=50,
            ),
            UseCase(
                use_case_id="F2",
                title="Personal Finance: Budgeting & Cash Flow",
                category=UseCaseCategory.FINANCE,
                description="Master personal finance with budgeting, expense tracking, and cash flow management.",
                expert_assigned="Warren",
                keywords=["budget", "finance", "spending", "cash", "management"],
                difficulty_level="beginner",
                estimated_duration_min=30,
            ),
            UseCase(
                use_case_id="F3",
                title="Debt Management: Paying It Down Smart",
                category=UseCaseCategory.FINANCE,
                description="Manage debt strategically. Understand interest, prioritize payoff, avoid traps, rebuild credit.",
                expert_assigned="Warren",
                keywords=["debt", "loan", "credit", "interest", "payoff"],
                difficulty_level="intermediate",
                estimated_duration_min=35,
            ),
            UseCase(
                use_case_id="F4",
                title="Real Estate: Buying Your First Home",
                category=UseCaseCategory.FINANCE,
                description="Navigate home buying. Cover mortgages, down payments, locations, inspection, negotiation.",
                expert_assigned="Warren",
                keywords=["real estate", "home", "mortgage", "property", "buy"],
                difficulty_level="intermediate",
                estimated_duration_min=60,
            ),
            UseCase(
                use_case_id="F5",
                title="Retirement Planning: Your Future Self",
                category=UseCaseCategory.FINANCE,
                description="Plan for retirement. Cover savings targets, withdrawal strategies, tax-advantaged accounts, and life design.",
                expert_assigned="Warren",
                keywords=["retirement", "401k", "ira", "savings", "future"],
                difficulty_level="advanced",
                estimated_duration_min=55,
            ),

            # === PERSONAL GROWTH (6) ===
            UseCase(
                use_case_id="P1",
                title="Self-Discovery: Know Yourself",
                category=UseCaseCategory.PERSONAL_GROWTH,
                description="Discover your values, strengths, and purpose. Reflect on identity, beliefs, and what truly matters.",
                expert_assigned="Sadhguru",
                keywords=["self", "identity", "values", "purpose", "discover"],
                difficulty_level="beginner",
                estimated_duration_min=40,
            ),
            UseCase(
                use_case_id="P2",
                title="Goal Setting: Meaningful Targets",
                category=UseCaseCategory.PERSONAL_GROWTH,
                description="Set meaningful goals aligned with your values. Cover vision, objectives, OKRs, and progress tracking.",
                expert_assigned="Andy",
                keywords=["goal", "target", "objective", "okr", "vision"],
                difficulty_level="intermediate",
                estimated_duration_min=45,
            ),
            UseCase(
                use_case_id="P3",
                title="Confidence Building: Belief in Yourself",
                category=UseCaseCategory.PERSONAL_GROWTH,
                description="Build genuine confidence through competence, reflection, and overcoming self-doubt.",
                expert_assigned="Brené",
                keywords=["confidence", "belief", "imposter", "strength", "courage"],
                difficulty_level="intermediate",
                estimated_duration_min=35,
            ),
            UseCase(
                use_case_id="P4",
                title="Resilience: Bouncing Back from Failure",
                category=UseCaseCategory.PERSONAL_GROWTH,
                description="Build resilience to handle setbacks and failures. Learn from adversity and grow stronger.",
                expert_assigned="APJ",
                keywords=["resilience", "failure", "bounce back", "adversity", "growth"],
                difficulty_level="intermediate",
                estimated_duration_min=40,
            ),
            UseCase(
                use_case_id="P5",
                title="Learning Mastery: Acquiring New Skills",
                category=UseCaseCategory.PERSONAL_GROWTH,
                description="Master the art of learning new skills effectively. Cover deliberate practice, learning systems, and knowledge retention.",
                expert_assigned="Richard",
                keywords=["learning", "skill", "practice", "mastery", "education"],
                difficulty_level="intermediate",
                estimated_duration_min=50,
            ),
            UseCase(
                use_case_id="P6",
                title="Life Purpose: Finding Meaning",
                category=UseCaseCategory.PERSONAL_GROWTH,
                description="Find your life purpose and meaningful direction. Align career with values and make impact.",
                expert_assigned="Sadhguru",
                keywords=["purpose", "meaning", "impact", "direction", "life"],
                difficulty_level="advanced",
                estimated_duration_min=60,
            ),

            # === CREATIVITY (3) ===
            UseCase(
                use_case_id="K1",
                title="Writing: Finding Your Voice",
                category=UseCaseCategory.CREATIVITY,
                description="Develop your writing voice and practice regularly. Cover storytelling, clarity, and sharing your ideas.",
                expert_assigned="Naval",
                keywords=["writing", "voice", "storytelling", "content", "blog"],
                difficulty_level="beginner",
                estimated_duration_min=40,
            ),
            UseCase(
                use_case_id="K2",
                title="Creativity: Unlocking Innovation",
                category=UseCaseCategory.CREATIVITY,
                description="Unlock creative potential through ideation, experimentation, and reducing perfectionism.",
                expert_assigned="Naval",
                keywords=["creativity", "innovation", "idea", "creation", "art"],
                difficulty_level="intermediate",
                estimated_duration_min=45,
            ),
            UseCase(
                use_case_id="K3",
                title="Artistic Expression: Making Things",
                category=UseCaseCategory.CREATIVITY,
                description="Explore artistic pursuits. Music, painting, sculpture, or other creative outlets for expression.",
                expert_assigned="Naval",
                keywords=["art", "music", "paint", "create", "express"],
                difficulty_level="beginner",
                estimated_duration_min=35,
            ),

            # === MEMORY (2) ===
            UseCase(
                use_case_id="M1",
                title="Life Review: Capturing Your Story",
                category=UseCaseCategory.MEMORY,
                description="Document your life story. Capture memories, lessons learned, family history, and legacy.",
                expert_assigned="APJ",
                keywords=["memory", "story", "history", "legacy", "capture"],
                difficulty_level="beginner",
                estimated_duration_min=60,
            ),
            UseCase(
                use_case_id="M2",
                title="Future Visioning: 10-Year Plan",
                category=UseCaseCategory.MEMORY,
                description="Envision your ideal future 10 years out. Design your life with intention and clarity.",
                expert_assigned="Indra",
                keywords=["future", "vision", "plan", "10-year", "design"],
                difficulty_level="intermediate",
                estimated_duration_min=75,
            ),
        ]

    def get_by_id(self, use_case_id: str) -> Optional[UseCase]:
        """Get use case by ID."""
        return self._by_id.get(use_case_id)

    def get_by_category(self, category: UseCaseCategory) -> List[UseCase]:
        """Get all use cases in a category."""
        return self._by_category.get(category, [])

    def get_all_by_difficulty(self, level: str) -> List[UseCase]:
        """Get all use cases at a difficulty level."""
        return [uc for uc in self.use_cases if uc.difficulty_level == level]

    def get_all(self) -> List[UseCase]:
        """Get all use cases."""
        return self.use_cases

    def get_by_category_sorted(self) -> dict:
        """Get all use cases sorted by category."""
        result = {}
        for cat in UseCaseCategory:
            result[cat.value] = self.get_by_category(cat)
        return result
