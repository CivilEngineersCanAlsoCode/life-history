"""
Life Brain configuration — constants, thresholds, enums.
"""

from enum import Enum
from typing import Dict, List

# ──── CHROMADB ────
CHROMA_PATH = "./life_brain_db"
COLLECTION_NAME = "life_brain"
EMBEDDING_MODEL = "text-embedding-3-small"  # OpenAI
HNSW_SPACE = "cosine"

# ──── TRUTH ENGINE ────
CONFLICT_THRESHOLDS = {
    "semantic_similarity_threshold": 0.75,  # "about the same thing"
    "hard_conflict": 0.6,                   # block user, ask to resolve
    "soft_conflict": 0.3,                   # warn user
    "enrichment": 0.1,                      # auto-update existing (new adds detail)
}

GROUNDEDNESS_THRESHOLDS = {
    "high_confidence": 0.85,      # cite source
    "medium_confidence": 0.70,    # caveat: "confirm karo"
    "low_confidence": 0.50,       # flag uncertainty
}

ENTITY_ALIASES = {
    # Companies
    "amex": "american express",
    "american express": "american express",
    "sprinklr": "sprinklr",
    "apple": "apple",
    "google": "google",
    # Roles
    "pm": "product manager",
    "product manager": "product manager",
    "swe": "software engineer",
    "engineer": "software engineer",
}

# ──── METADATA SCHEMA ────

class Domain(str, Enum):
    """20 life domains"""
    CAREER = "career"
    RELATIONSHIPS = "relationships"
    HEALTH = "health"
    FINANCE = "finance"
    EDUCATION = "education"
    PERSONAL_GROWTH = "personal_growth"
    DECISIONS = "decisions"
    DAILY_LIFE = "daily_life"
    GOALS = "goals"
    BELIEFS = "beliefs"
    MEMORIES = "memories"
    CREATIVITY = "creativity"
    COMMUNICATION = "communication"
    LEGAL = "legal"
    FAMILY = "family"
    TRAVEL = "travel"
    ENTERTAINMENT = "entertainment"
    EMERGENCY = "emergency"
    SOCIAL_DIGITAL = "social_digital"
    AI_META = "ai_meta"

class AtomType(str, Enum):
    """5 types of knowledge atoms"""
    FACT = "fact"
    STORY = "star_story"
    METRIC = "metric"
    DECISION = "decision"
    LESSON = "lesson"
    QA_PAIR = "qa_pair"
    EVENT = "event"
    REFLECTION = "reflection"
    PREFERENCE = "preference"
    GOAL = "goal"
    BELIEF = "belief"
    DIARY_ENTRY = "diary_entry"
    DREAM = "dream"
    REGRET = "regret"
    REVIEW = "review"
    RELATIONSHIP_NOTE = "relationship_note"
    HABIT = "habit"
    DOCUMENT_RECORD = "document_record"

class Privacy(str, Enum):
    """Privacy tiers"""
    PUBLIC = "public"
    PRIVATE = "private"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"

class Confidence(str, Enum):
    """Data confidence levels"""
    VERIFIED = "verified"
    APPROXIMATE = "approximate"
    UNCERTAIN = "uncertain"
    SUBJECTIVE = "subjective"

class Source(str, Enum):
    """Where information came from"""
    INTERVIEW = "interview"
    DIARY = "diary"
    MEMORY = "memory"
    DOCUMENT = "document"
    REFLECTION = "reflection"
    CONVERSATION = "conversation"
    MEDICAL_RECORD = "medical_record"
    FINANCIAL_RECORD = "financial_record"

class Status(str, Enum):
    """Status values for goals, projects, etc."""
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    DROPPED = "dropped"
    PENDING = "pending"
    RESOLVED = "resolved"

# ──── REQUIRED METADATA FIELDS ────
REQUIRED_METADATA_FIELDS = [
    "domain",
    "subdomain",
    "type",
    "importance",
    "privacy",
    "source",
    "schema_version",
]

# ──---- TIER 1: Core Fields (24) ────
TIER_1_FIELDS = {
    # WHAT (Content Classification)
    "domain": str,
    "subdomain": str,
    "type": str,
    "tags": str,
    # WHEN (Temporal)
    "date": str,
    "date_start": str,
    "date_end": str,
    "life_phase": str,
    # WHO (People & Organizations)
    "people": str,
    "relationships": str,
    "organization": str,
    "role": str,
    # WHERE (Location & Context)
    "location": str,
    "country": str,
    "context": str,
    # CAREER-SPECIFIC
    "company": str,
    "project": str,
    "category": str,
    # META (About the entry)
    "importance": int,
    "emotion": str,
    "sentiment": str,
    "privacy": str,
    "confidence": str,
    "source": str,
    "schema_version": int,
}

# ──---- TIER 2: Extended Fields (23) ────
TIER_2_FIELDS = {
    # STATUS & OUTCOME
    "status": str,
    "outcome": str,
    "resolution_status": str,
    "follow_up_status": str,
    # QUANTITATIVE
    "monetary_value": float,
    "currency": str,
    "rating": int,
    "energy_level": int,
    "severity": int,
    # CONTENT REFERENCE
    "title": str,
    "author_creator": str,
    "medium": str,
    "platform": str,
    # TRIGGERS & PATTERNS
    "trigger": str,
    "pattern_id": str,
    "related_id": str,
    # TEMPORAL EXTRAS
    "duration": str,
    "frequency": str,
    "expiry_date": str,
    "time_of_day": str,
    # ITEMS & EVENTS
    "item": str,
    "event_name": str,
    "environment": str,
}

# ──── LANGUAGE TRANSLATION ────
PRESERVED_TERMS = [
    # Technical acronyms
    "CRR", "AML", "OKR", "API", "HNSW", "LLM",
    "SQL", "NoSQL", "REST", "JSON", "CSV", "ML", "AI",
    # Companies & proper nouns
    "Sprinklr", "American Express", "AmEx", "Google", "Apple",
    "LinkedIn", "Twitter", "YouTube", "Netflix", "Udemy",
    # Product names
    "ChromaDB", "Cadence", "CGB", "Walmart Spark",
    # People names
    "Satvik", "Satya", "Warren", "Elon", "Steve", "Richard",
]

# ──---- CONFLICT DETECTION ────
ATOM_TYPE_CONTRADICTIONS = {
    "metric": "numeric_difference",      # |new - old| / max
    "fact": "binary_llm_check",          # 0.0 or 1.0
    "date": "normalized_days_diff",      # days / 365
    "story": "semantic_divergence",      # LLM 0-1
}

# ──── EXTRACTION ────
MAX_VECTORS_PER_SYNTHESIS = 3
NUGGET_MIN_CONFIDENCE = 0.6
QA_PAIR_MIN_CONFIDENCE = 0.9

# ──---- CONVERSATIONAL ────
SMALL_TALK_CONFIDENCE = 0.6
GUIDED_CONFIDENCE_THRESHOLD = 0.7
INTENT_SUGGESTION_ONCE = True
WEEKLY_REVIEW_INTERVAL_DAYS = 7

# ──---- SESSION STATE ────
SESSION_TIMEOUT_HOURS = 24
MAX_QUESTIONS_PER_SESSION = 15
