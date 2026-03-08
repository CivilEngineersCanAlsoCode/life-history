"""
Use Case Catalog — 40+ structured scenarios for guided conversation.

Each use case:
- ID: Unique identifier (e.g., "C1", "R5", "F3")
- Title: Human-readable name
- Expert: Primary expert persona
- Category: Domain category
- Description: What this use case covers
- Keywords: For semantic matching
- Question bank: Opening questions to guide user
"""

from typing import Dict, List, Any, Optional

# 40+ Use Cases organized by domain
USE_CASES: Dict[str, Dict[str, Any]] = {
    # ──── 🎯 CAREER ────
    "C1": {
        "id": "C1",
        "title": "Interview Prep - Behavioral",
        "expert": "satya_nadella",
        "category": "career",
        "domain": "career",
        "description": "Prepare for behavioral interview questions with STAR stories",
        "keywords": ["interview", "behavioral", "STAR", "tell me about", "example"],
        "questions": [
            "Tell me about a time you had to learn something completely new.",
            "Give an example of when you showed empathy at work.",
            "Describe a situation where you had to change your approach.",
            "Tell me about a project where you grew as a person.",
        ]
    },
    "C2": {
        "id": "C2",
        "title": "Interview Prep - Technical",
        "expert": "richard_feynman",
        "category": "career",
        "domain": "career",
        "description": "Prepare technical interview: explain concepts clearly, first-principles thinking",
        "keywords": ["technical interview", "system design", "explain", "architecture"],
        "questions": [
            "Explain the most complex system you've built to a 5-year-old.",
            "Walk me through your most difficult technical problem.",
            "How would you design this system from first principles?",
            "What was the hardest technical challenge you faced?",
        ]
    },
    "C3": {
        "id": "C3",
        "title": "Interview Prep - System Design",
        "expert": "jeff_bezos",
        "category": "career",
        "domain": "career",
        "description": "System design interview: scale, architecture, working backwards",
        "keywords": ["system design", "scale", "architecture", "API", "database"],
        "questions": [
            "Design a system to handle X. Work backwards from customer need.",
            "How would you scale this for 10x more users?",
            "What are the key metrics for this system?",
            "Walk me through your trade-offs.",
        ]
    },
    "C4": {
        "id": "C4",
        "title": "Resume Crafting",
        "expert": "apj_abdul_kalam",
        "category": "career",
        "domain": "career",
        "description": "Build a compelling resume that tells your story",
        "keywords": ["resume", "CV", "portfolio", "achievements", "impact"],
        "questions": [
            "What are your 3-5 biggest professional achievements?",
            "What impact did your work have on the business?",
            "How did you demonstrate leadership in your role?",
            "What metrics define success in your projects?",
        ]
    },
    "C5": {
        "id": "C5",
        "title": "Salary Negotiation",
        "expert": "warren_buffett",
        "category": "career",
        "domain": "career",
        "description": "Prepare for salary negotiation with data and confidence",
        "keywords": ["salary", "negotiation", "offer", "compensation", "raise"],
        "questions": [
            "What's your current salary and benefits package?",
            "What are you looking for in your next role?",
            "How do you evaluate your market value?",
            "What's your walk-away number?",
        ]
    },
    "C6": {
        "id": "C6",
        "title": "Performance Review Prep",
        "expert": "andy_grove",
        "category": "career",
        "domain": "career",
        "description": "Prepare for performance review with OKRs and achievements",
        "keywords": ["performance", "review", "OKR", "goals", "feedback"],
        "questions": [
            "What OKRs did you set this period?",
            "Which goals did you exceed, and how?",
            "What's one area where you need to improve?",
            "What support do you need to level up?",
        ]
    },
    "C7": {
        "id": "C7",
        "title": "Career Planning & Pivots",
        "expert": "naval_ravikant",
        "category": "career",
        "domain": "career",
        "description": "Plan your career trajectory or explore a pivot",
        "keywords": ["career", "pivot", "planning", "growth", "next role"],
        "questions": [
            "Where do you want to be in 5 years?",
            "What's holding you back from your next goal?",
            "What skills do you need to build?",
            "Why are you considering a pivot?",
        ]
    },
    "C8": {
        "id": "C8",
        "title": "Job Search Strategy",
        "expert": "reid_hoffman",
        "category": "career",
        "domain": "career",
        "description": "Build a strategic job search leveraging your network",
        "keywords": ["job search", "networking", "LinkedIn", "opportunities"],
        "questions": [
            "What's your target role and company?",
            "Who in your network could introduce you?",
            "What's your unique value proposition?",
            "How will you stand out to recruiters?",
        ]
    },
    "C9": {
        "id": "C9",
        "title": "Project Documentation",
        "expert": "narayana_murthy",
        "category": "career",
        "domain": "career",
        "description": "Document your project for portfolio and interviews",
        "keywords": ["project", "documentation", "portfolio", "case study"],
        "questions": [
            "What problem did your project solve?",
            "Who were your users/stakeholders?",
            "What was your role and impact?",
            "What metrics measure success?",
        ]
    },
    "C10": {
        "id": "C10",
        "title": "Learning & Skill Dev",
        "expert": "richard_feynman",
        "category": "career",
        "domain": "career",
        "description": "Learn new skills effectively using Feynman technique",
        "keywords": ["learning", "skill", "growth", "course", "mastery"],
        "questions": [
            "What skill do you want to master?",
            "Can you explain it simply to someone else?",
            "What gaps appear when you try?",
            "How will you practice and measure progress?",
        ]
    },
    "C11": {
        "id": "C11",
        "title": "Leadership Stories",
        "expert": "apj_abdul_kalam",
        "category": "career",
        "domain": "career",
        "description": "Capture and refine your leadership moments",
        "keywords": ["leadership", "stories", "influence", "vision", "team"],
        "questions": [
            "Tell me about a time you inspired a team.",
            "How did you build trust with your team?",
            "What's your leadership philosophy?",
            "Describe a moment where you pivoted direction.",
        ]
    },
    "C12": {
        "id": "C12",
        "title": "Team/Manager Dynamics",
        "expert": "andy_grove",
        "category": "career",
        "domain": "career",
        "description": "Navigate team conflicts and manager relationships",
        "keywords": ["team", "manager", "conflict", "communication", "feedback"],
        "questions": [
            "How would you describe your manager?",
            "What's one conflict you've had with a teammate?",
            "How do you give and receive feedback?",
            "What team structure works best for you?",
        ]
    },

    # ──── 💛 RELATIONSHIPS ────
    "R1": {
        "id": "R1",
        "title": "Conflict Resolution",
        "expert": "esther_perel",
        "category": "relationships",
        "domain": "relationships",
        "description": "Navigate and resolve relationship conflicts",
        "keywords": ["conflict", "argument", "resolution", "partner", "communication"],
        "questions": [
            "What's the core of this conflict?",
            "What are both perspectives here?",
            "What do you each need to feel heard?",
            "How can you reconnect after this?",
        ]
    },
    "R2": {
        "id": "R2",
        "title": "Difficult Conversations",
        "expert": "chris_voss",
        "category": "relationships",
        "domain": "relationships",
        "description": "Prepare for and handle difficult conversations",
        "keywords": ["difficult", "conversation", "negotiate", "empathy", "listen"],
        "questions": [
            "What makes this conversation difficult?",
            "What outcome do you want?",
            "What do you think they want?",
            "How will you create psychological safety?",
        ]
    },
    "R3": {
        "id": "R3",
        "title": "Romantic Relationship",
        "expert": "devdutt_pattanaik",
        "category": "relationships",
        "domain": "relationships",
        "description": "Explore romantic relationships through narrative lens",
        "keywords": ["love", "partner", "relationship", "dating", "connection"],
        "questions": [
            "What's the story you're telling about this relationship?",
            "What patterns do you see repeating?",
            "What do you truly desire?",
            "How has this relationship shaped you?",
        ]
    },
    "R4": {
        "id": "R4",
        "title": "Family Issues",
        "expert": "ratan_tata",
        "category": "relationships",
        "domain": "relationships",
        "description": "Work through family dynamics and values",
        "keywords": ["family", "parents", "siblings", "expectations", "values"],
        "questions": [
            "What family patterns do you want to break?",
            "How do your values differ from your family's?",
            "What does family mean to you?",
            "How do you balance duty and choice?",
        ]
    },
    "R5": {
        "id": "R5",
        "title": "Friendship Dynamics",
        "expert": "brene_brown",
        "category": "relationships",
        "domain": "relationships",
        "description": "Build and maintain meaningful friendships",
        "keywords": ["friendship", "friend", "betrayal", "connection", "loyalty"],
        "questions": [
            "What makes a good friend for you?",
            "How do you maintain friendships?",
            "What happened in this friendship?",
            "How can you repair this?",
        ]
    },
    "R6": {
        "id": "R6",
        "title": "Professional Networking",
        "expert": "reid_hoffman",
        "category": "relationships",
        "domain": "relationships",
        "description": "Build strategic professional relationships",
        "keywords": ["networking", "professional", "connection", "mentor", "ally"],
        "questions": [
            "Who are your key professional relationships?",
            "How do you add value to others?",
            "What kinds of relationships do you want to build?",
            "How will you stay in touch?",
        ]
    },
    "R7": {
        "id": "R7",
        "title": "Boundaries & Saying No",
        "expert": "brene_brown",
        "category": "relationships",
        "domain": "relationships",
        "description": "Set healthy boundaries and practice assertiveness",
        "keywords": ["boundaries", "no", "assertiveness", "respect", "expectations"],
        "questions": [
            "Where do you struggle to set boundaries?",
            "What makes it hard to say no?",
            "What boundaries do you need now?",
            "How will you communicate this?",
        ]
    },

    # ──── 💪 HEALTH ────
    "H1": {
        "id": "H1",
        "title": "Fitness Planning",
        "expert": "andrew_huberman",
        "category": "health",
        "domain": "health",
        "description": "Design sustainable fitness protocols",
        "keywords": ["fitness", "exercise", "training", "workout", "goals"],
        "questions": [
            "What's your current fitness level?",
            "What are your fitness goals?",
            "How much time can you commit?",
            "What motivates you?",
        ]
    },
    "H2": {
        "id": "H2",
        "title": "Mental Wellness",
        "expert": "brene_brown",
        "category": "health",
        "domain": "health",
        "description": "Address stress, anxiety, and emotional wellbeing",
        "keywords": ["mental", "stress", "anxiety", "wellbeing", "therapy"],
        "questions": [
            "How are you feeling right now?",
            "What's causing stress?",
            "How do you typically cope?",
            "What support do you need?",
        ]
    },
    "H3": {
        "id": "H3",
        "title": "Sleep Optimization",
        "expert": "andrew_huberman",
        "category": "health",
        "domain": "health",
        "description": "Optimize sleep for energy and health",
        "keywords": ["sleep", "insomnia", "circadian", "rest", "recovery"],
        "questions": [
            "How's your sleep currently?",
            "When do you naturally wake/sleep?",
            "What disrupts your sleep?",
            "What are your sleep goals?",
        ]
    },
    "H4": {
        "id": "H4",
        "title": "Nutrition",
        "expert": "andrew_huberman",
        "category": "health",
        "domain": "health",
        "description": "Build healthy eating habits and nutrition knowledge",
        "keywords": ["nutrition", "diet", "food", "health", "energy"],
        "questions": [
            "How's your current diet?",
            "What are your nutrition goals?",
            "What challenges you?",
            "What does a typical day of eating look like?",
        ]
    },
    "H5": {
        "id": "H5",
        "title": "Energy Management",
        "expert": "sadhguru",
        "category": "health",
        "domain": "health",
        "description": "Manage energy and build inner vitality",
        "keywords": ["energy", "fatigue", "vitality", "inner", "consciousness"],
        "questions": [
            "When do you have most energy?",
            "What drains your energy?",
            "How's your inner state?",
            "What would true vitality feel like?",
        ]
    },
    "H6": {
        "id": "H6",
        "title": "Medical Tracking",
        "expert": "andrew_huberman",
        "category": "health",
        "domain": "health",
        "description": "Track health metrics systematically",
        "keywords": ["medical", "tracking", "metrics", "health", "data"],
        "questions": [
            "What health metrics matter to you?",
            "How will you track them?",
            "What's your baseline?",
            "What changes will you measure?",
        ]
    },

    # ──── 💰 FINANCE ────
    "F1": {
        "id": "F1",
        "title": "Budgeting",
        "expert": "warren_buffett",
        "category": "finance",
        "domain": "finance",
        "description": "Build sustainable budget and spending habits",
        "keywords": ["budget", "spending", "money", "expenses", "frugal"],
        "questions": [
            "What's your monthly income and expenses?",
            "Where does money typically disappear?",
            "What's your biggest expense category?",
            "How can you live below your means?",
        ]
    },
    "F2": {
        "id": "F2",
        "title": "Investment Strategy",
        "expert": "warren_buffett",
        "category": "finance",
        "domain": "finance",
        "description": "Build long-term wealth through investing",
        "keywords": ["investment", "stocks", "portfolio", "wealth", "compound"],
        "questions": [
            "What's your investment knowledge?",
            "What's your risk tolerance?",
            "What are your investment goals?",
            "How much can you invest monthly?",
        ]
    },
    "F3": {
        "id": "F3",
        "title": "Salary & Compensation",
        "expert": "charlie_munger",
        "category": "finance",
        "domain": "finance",
        "description": "Understand and optimize your compensation package",
        "keywords": ["salary", "compensation", "benefits", "stock", "bonus"],
        "questions": [
            "What's your total compensation?",
            "How does it compare to market?",
            "What's negotiable?",
            "What are you optimizing for?",
        ]
    },
    "F4": {
        "id": "F4",
        "title": "Big Purchases",
        "expert": "charlie_munger",
        "category": "finance",
        "domain": "finance",
        "description": "Make smart decisions on major financial commitments",
        "keywords": ["purchase", "house", "car", "investment", "decision"],
        "questions": [
            "What are you thinking of purchasing?",
            "Why do you need it?",
            "What are the alternatives?",
            "What would the \"newspaper test\" say?",
        ]
    },
    "F5": {
        "id": "F5",
        "title": "Financial Goals",
        "expert": "rakesh_jhunjhunwala",
        "category": "finance",
        "domain": "finance",
        "description": "Set and achieve meaningful financial goals",
        "keywords": ["goals", "wealth", "financial", "freedom", "target"],
        "questions": [
            "What's your financial dream?",
            "How much do you want to have?",
            "By when?",
            "What's your plan to get there?",
        ]
    },

    # ──── 🧠 PERSONAL GROWTH ────
    "P1": {
        "id": "P1",
        "title": "Habit Building",
        "expert": "andrew_huberman",
        "category": "personal_growth",
        "domain": "personal_growth",
        "description": "Build sustainable habits using neuroscience",
        "keywords": ["habit", "routine", "behavior", "discipline", "consistency"],
        "questions": [
            "What habit do you want to build?",
            "Why does it matter?",
            "How will you start small?",
            "What's your trigger?",
        ]
    },
    "P2": {
        "id": "P2",
        "title": "Goal Setting",
        "expert": "elon_musk",
        "category": "personal_growth",
        "domain": "personal_growth",
        "description": "Set moonshot goals from first principles",
        "keywords": ["goal", "vision", "ambition", "moonshot", "dream"],
        "questions": [
            "What's your biggest dream?",
            "Why haven't you achieved it yet?",
            "What would success look like?",
            "What's your first step?",
        ]
    },
    "P3": {
        "id": "P3",
        "title": "Journaling",
        "expert": "brene_brown",
        "category": "personal_growth",
        "domain": "personal_growth",
        "description": "Use journaling for self-discovery and reflection",
        "keywords": ["journaling", "reflection", "writing", "insight", "growth"],
        "questions": [
            "What do you want to understand?",
            "How do you typically reflect?",
            "What patterns emerge?",
            "What will you do differently?",
        ]
    },
    "P4": {
        "id": "P4",
        "title": "Learning Plans",
        "expert": "richard_feynman",
        "category": "personal_growth",
        "domain": "personal_growth",
        "description": "Design effective learning strategies",
        "keywords": ["learning", "study", "mastery", "skill", "knowledge"],
        "questions": [
            "What do you want to learn deeply?",
            "How do you learn best?",
            "What's your learning goal?",
            "How will you measure progress?",
        ]
    },
    "P5": {
        "id": "P5",
        "title": "Identity & Values",
        "expert": "sadhguru",
        "category": "personal_growth",
        "domain": "personal_growth",
        "description": "Explore and clarify your identity and core values",
        "keywords": ["identity", "values", "purpose", "meaning", "who am i"],
        "questions": [
            "Who are you at your core?",
            "What are your non-negotiable values?",
            "What's your purpose?",
            "How do you want to be remembered?",
        ]
    },
    "P6": {
        "id": "P6",
        "title": "Major Life Decisions",
        "expert": "charlie_munger",
        "category": "personal_growth",
        "domain": "personal_growth",
        "description": "Make wise decisions using mental models",
        "keywords": ["decision", "choice", "framework", "thinking", "wisdom"],
        "questions": [
            "What decision are you facing?",
            "What mental models apply?",
            "What would inverting this show?",
            "What's the second-order consequence?",
        ]
    },

    # ──── 🎨 CREATIVITY ────
    "CR1": {
        "id": "CR1",
        "title": "Idea Generation",
        "expert": "steve_jobs",
        "category": "creativity",
        "domain": "creativity",
        "description": "Generate ideas at the intersection of disciplines",
        "keywords": ["idea", "creativity", "innovation", "inspiration", "flow"],
        "questions": [
            "What problem fascinates you?",
            "What unexpected connections do you see?",
            "What would you create if you weren't afraid?",
            "What simple solution is most elegant?",
        ]
    },
    "CR2": {
        "id": "CR2",
        "title": "Writing",
        "expert": "naval_ravikant",
        "category": "creativity",
        "domain": "creativity",
        "description": "Develop your writing voice and clarity",
        "keywords": ["writing", "communication", "clarity", "voice", "expression"],
        "questions": [
            "What do you want to communicate?",
            "Who's your reader?",
            "What's your unique voice?",
            "How can you be more concise?",
        ]
    },
    "CR3": {
        "id": "CR3",
        "title": "Personal Project Planning",
        "expert": "jeff_bezos",
        "category": "creativity",
        "domain": "creativity",
        "description": "Plan creative projects with working backwards",
        "keywords": ["project", "creative", "planning", "execution", "goal"],
        "questions": [
            "What do you want to create?",
            "Who will benefit?",
            "What's the minimum viable version?",
            "What's your timeline?",
        ]
    },

    # ──── 📚 MEMORIES ────
    "M1": {
        "id": "M1",
        "title": "Memory Capture",
        "expert": "apj_abdul_kalam",
        "category": "memories",
        "domain": "memories",
        "description": "Capture turning points and moments of grace",
        "keywords": ["memory", "moment", "turning point", "story", "significance"],
        "questions": [
            "What moment changed everything?",
            "What did you learn from it?",
            "Who was there?",
            "Why does it matter?",
        ]
    },
    "M2": {
        "id": "M2",
        "title": "Life Review",
        "expert": "sadhguru",
        "category": "memories",
        "domain": "memories",
        "description": "Review your life for patterns and consciousness",
        "keywords": ["life", "review", "pattern", "consciousness", "meaning"],
        "questions": [
            "What patterns emerge in your life?",
            "What brought you joy?",
            "What do you regret?",
            "How have you grown?",
        ]
    },
    "M3": {
        "id": "M3",
        "title": "People Notes",
        "expert": "devdutt_pattanaik",
        "category": "memories",
        "domain": "memories",
        "description": "Document relationships as stories",
        "keywords": ["people", "relationship", "story", "notes", "character"],
        "questions": [
            "Who has shaped you most?",
            "What's their story?",
            "How did they influence you?",
            "What do you want to remember?",
        ]
    },
}


def get_use_case(use_case_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific use case by ID."""
    return USE_CASES.get(use_case_id)


def get_use_cases_by_category(category: str) -> Dict[str, Dict[str, Any]]:
    """Get all use cases in a category."""
    return {
        uc_id: uc for uc_id, uc in USE_CASES.items()
        if uc.get("category") == category
    }


def get_use_cases_by_domain(domain: str) -> Dict[str, Dict[str, Any]]:
    """Get all use cases in a domain."""
    return {
        uc_id: uc for uc_id, uc in USE_CASES.items()
        if uc.get("domain") == domain
    }


def get_use_case_keywords() -> Dict[str, List[str]]:
    """Get mapping of all keywords to use case IDs for matching."""
    keyword_map = {}
    for uc_id, uc in USE_CASES.items():
        for keyword in uc.get("keywords", []):
            if keyword not in keyword_map:
                keyword_map[keyword] = []
            keyword_map[keyword].append(uc_id)
    return keyword_map


def find_use_cases_by_keywords(keywords: List[str]) -> List[str]:
    """Find use case IDs matching given keywords."""
    keyword_map = get_use_case_keywords()
    matching_uc_ids = set()

    for keyword in keywords:
        keyword_lower = keyword.lower()
        for kw, uc_ids in keyword_map.items():
            if keyword_lower in kw.lower() or kw.lower() in keyword_lower:
                matching_uc_ids.update(uc_ids)

    return sorted(list(matching_uc_ids))
