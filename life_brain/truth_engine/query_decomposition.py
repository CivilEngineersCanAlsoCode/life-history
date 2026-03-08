"""
Query Decomposition — Break complex queries into retrievable subqueries.

Implements:
- Query complexity detection
- Decomposition into atomic queries
- Query rewriting for better retrieval
- Metadata-aware routing
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import re

logger = logging.getLogger(__name__)


class QueryComplexity(str, Enum):
    """Complexity level of a query."""
    SIMPLE = "simple"  # Single clause, easily retrievable
    MODERATE = "moderate"  # 2-3 related concepts
    COMPLEX = "complex"  # 4+ concepts or multiple domains


@dataclass
class AtomicQuery:
    """A single, retrievable query."""

    query_text: str
    keywords: List[str]
    domain: Optional[str] = None  # e.g., "career", "relationships"
    entity_type: Optional[str] = None  # e.g., "project", "person", "skill"
    temporal_constraint: Optional[str] = None  # e.g., "2022", "recent", "Q1"
    priority: int = 1  # 1 = highest priority


@dataclass
class DecomposedQuery:
    """Result of query decomposition."""

    original_query: str
    complexity: QueryComplexity
    atomic_queries: List[AtomicQuery]
    is_multi_domain: bool  # Crosses multiple domains?
    requires_synthesis: bool  # Need to combine results?
    alternative_phrasings: List[str]  # Variations for better matching


class QueryAnalyzer:
    """Analyze query complexity and structure."""

    # Complexity indicators
    CONJUNCTION_KEYWORDS = ["and", "also", "additionally", "plus", "moreover"]
    DISJUNCTION_KEYWORDS = ["or", "either", "alternatively"]
    COMPARISON_KEYWORDS = ["vs", "versus", "compare", "difference", "similar"]
    CAUSATION_KEYWORDS = ["because", "caused", "resulted", "led to", "why"]
    QUESTION_KEYWORDS = ["how", "why", "what", "where", "when", "which", "who"]

    def __init__(self):
        """Initialize query analyzer."""
        pass

    def detect_complexity(self, query: str) -> QueryComplexity:
        """
        Detect query complexity level.

        Args:
            query: User query

        Returns:
            QueryComplexity level
        """
        query_lower = query.lower()

        # Count clause indicators
        clause_count = 0
        clause_count += len([k for k in self.CONJUNCTION_KEYWORDS if f" {k} " in f" {query_lower} "])
        clause_count += len([k for k in self.DISJUNCTION_KEYWORDS if f" {k} " in f" {query_lower} "])

        # Count distinct concepts (rough estimate by commas and sentences)
        concept_count = query.count(",") + query.count(";")

        # Check for multiple question types
        question_count = query.count("?")

        total_complexity_signals = clause_count + concept_count + question_count

        if total_complexity_signals >= 3:
            return QueryComplexity.COMPLEX
        elif total_complexity_signals >= 1:
            return QueryComplexity.MODERATE
        else:
            return QueryComplexity.SIMPLE

    def extract_keywords(self, query: str) -> List[str]:
        """
        Extract key search terms from query.

        Args:
            query: User query

        Returns:
            List of keyword strings
        """
        # Remove question marks and split
        query_clean = query.replace("?", "").replace(".", "")
        words = query_clean.lower().split()

        # Filter out stop words
        stop_words = {
            "a", "an", "the", "is", "are", "was", "were", "be", "been",
            "have", "has", "do", "does", "did", "will", "would", "could",
            "should", "can", "and", "or", "but", "if", "for", "to", "of",
            "in", "on", "at", "by", "from", "with", "as", "what", "why",
            "how", "where", "when", "which", "who", "whom", "whose",
        }

        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        return list(dict.fromkeys(keywords))  # Remove duplicates, preserve order

    def detect_domains(self, query: str) -> List[str]:
        """
        Detect which domains a query addresses.

        Args:
            query: User query

        Returns:
            List of domain names
        """
        query_lower = query.lower()

        domain_keywords = {
            "career": ["job", "interview", "project", "work", "role", "position", "company", "promotion", "salary", "skill"],
            "relationships": ["friend", "girlfriend", "partner", "family", "conflict", "breakup", "communication"],
            "health": ["health", "fitness", "sleep", "diet", "exercise", "wellness", "mental", "stress"],
            "finance": ["money", "investment", "budget", "loan", "savings", "financial", "expense"],
            "personal_growth": ["learn", "grow", "improve", "habit", "goal", "strength", "weakness"],
        }

        detected_domains = []
        for domain, keywords in domain_keywords.items():
            if any(kw in query_lower for kw in keywords):
                detected_domains.append(domain)

        return detected_domains

    def detect_entities(self, query: str) -> Dict[str, List[str]]:
        """
        Detect named entities and entity types.

        Args:
            query: User query

        Returns:
            Dict of entity_type → list of entities
        """
        entities = {
            "company": [],
            "person": [],
            "project": [],
            "skill": [],
            "location": [],
        }

        # Simple pattern matching
        # Company names (capitalized, often with typical suffixes)
        company_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Inc|Corp|LLC|Ltd|Co))?\b)'
        companies = re.findall(company_pattern, query)
        entities["company"].extend(companies)

        # People names (preceded by "with", "from", "met", etc)
        person_pattern = r'(?:with|from|met|saw|talked to|worked with|under)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
        people = re.findall(person_pattern, query)
        entities["person"].extend(people)

        # Keywords for projects, skills
        if "project" in query.lower():
            # Extract preceding nouns
            project_words = re.findall(r'(\w+)\s+project', query.lower())
            entities["project"].extend(project_words)

        return entities


class QueryDecomposer:
    """Decompose complex queries into atomic, retrievable queries."""

    def __init__(self, analyzer: Optional[QueryAnalyzer] = None):
        """
        Initialize decomposer.

        Args:
            analyzer: Optional QueryAnalyzer (creates if not provided)
        """
        self.analyzer = analyzer or QueryAnalyzer()

    def decompose(self, query: str) -> DecomposedQuery:
        """
        Decompose a complex query into atomic queries.

        Args:
            query: User query

        Returns:
            DecomposedQuery with atomic queries and metadata
        """
        # Step 1: Analyze complexity
        complexity = self.analyzer.detect_complexity(query)

        # Step 2: Extract information
        keywords = self.analyzer.extract_keywords(query)
        domains = self.analyzer.detect_domains(query)
        entities = self.analyzer.detect_entities(query)

        is_multi_domain = len(domains) > 1

        # Step 3: Generate atomic queries
        atomic_queries = self._generate_atomic_queries(
            query=query,
            complexity=complexity,
            keywords=keywords,
            domains=domains,
            entities=entities,
        )

        # Step 4: Determine if synthesis needed
        requires_synthesis = len(atomic_queries) > 1 or is_multi_domain

        # Step 5: Generate alternative phrasings
        alternative_phrasings = self._generate_alternatives(query, keywords)

        logger.info(
            f"Decomposed query: complexity={complexity.value}, "
            f"atomic_queries={len(atomic_queries)}, domains={domains}"
        )

        return DecomposedQuery(
            original_query=query,
            complexity=complexity,
            atomic_queries=atomic_queries,
            is_multi_domain=is_multi_domain,
            requires_synthesis=requires_synthesis,
            alternative_phrasings=alternative_phrasings,
        )

    def _generate_atomic_queries(
        self,
        query: str,
        complexity: QueryComplexity,
        keywords: List[str],
        domains: List[str],
        entities: Dict[str, List[str]],
    ) -> List[AtomicQuery]:
        """
        Generate atomic queries from decomposition data.

        Args:
            query: Original query
            complexity: Query complexity
            keywords: Extracted keywords
            domains: Detected domains
            entities: Detected entities

        Returns:
            List of AtomicQuery objects
        """
        atomic_queries = []

        if complexity == QueryComplexity.SIMPLE:
            # Single atomic query
            atomic_queries.append(
                AtomicQuery(
                    query_text=query,
                    keywords=keywords,
                    domain=domains[0] if domains else None,
                    priority=1,
                )
            )

        elif complexity == QueryComplexity.MODERATE:
            # Split by conjunctions
            parts = self._split_by_conjunctions(query)
            for i, part in enumerate(parts):
                atomic_queries.append(
                    AtomicQuery(
                        query_text=part.strip(),
                        keywords=self.analyzer.extract_keywords(part),
                        domain=domains[i] if i < len(domains) else domains[0] if domains else None,
                        priority=1 + i,
                    )
                )

        else:  # COMPLEX
            # Split by multiple strategies
            # First: by major conjunctions
            parts = self._split_by_conjunctions(query)

            # Then: by entities if present
            for i, part in enumerate(parts):
                if any(entities.values()):
                    # Generate queries for each entity
                    for entity_type, entity_list in entities.items():
                        if entity_list:
                            entity_query = f"{part} {entity_list[0]}"
                            atomic_queries.append(
                                AtomicQuery(
                                    query_text=entity_query,
                                    keywords=self.analyzer.extract_keywords(entity_query),
                                    entity_type=entity_type,
                                    domain=domains[i % len(domains)] if domains else None,
                                    priority=2 + i,
                                )
                            )
                            break
                else:
                    atomic_queries.append(
                        AtomicQuery(
                            query_text=part.strip(),
                            keywords=self.analyzer.extract_keywords(part),
                            domain=domains[i % len(domains)] if domains else None,
                            priority=2 + i,
                        )
                    )

        # Deduplicate by query text
        seen = set()
        unique_queries = []
        for aq in atomic_queries:
            if aq.query_text.lower() not in seen:
                seen.add(aq.query_text.lower())
                unique_queries.append(aq)

        return unique_queries

    def _split_by_conjunctions(self, query: str) -> List[str]:
        """
        Split query by conjunction keywords.

        Args:
            query: Query to split

        Returns:
            List of query parts
        """
        # Split by "and", "or"
        pattern = r'\s+(?:and|or|also)\s+'
        parts = re.split(pattern, query, flags=re.IGNORECASE)
        return parts if len(parts) > 1 else [query]

    def _generate_alternatives(self, query: str, keywords: List[str]) -> List[str]:
        """
        Generate alternative phrasings for better retrieval.

        Args:
            query: Original query
            keywords: Extracted keywords

        Returns:
            List of alternative phrasings
        """
        alternatives = []

        # Alternative 1: Keyword-only version
        if keywords:
            alternatives.append(" ".join(keywords))

        # Alternative 2: Remove question mark and qualifiers
        simplified = query.replace("?", "").replace("could", "").replace("would", "").strip()
        if simplified != query:
            alternatives.append(simplified)

        # Alternative 3: Expand contractions
        expanded = query.replace("'s", " is").replace("'t", " not")
        if expanded != query:
            alternatives.append(expanded)

        return alternatives

    def format_decomposition_report(self, decomposed: DecomposedQuery) -> str:
        """
        Format decomposition as readable report.

        Args:
            decomposed: DecomposedQuery result

        Returns:
            Formatted report
        """
        report = f"""
╔═══════════════════════════════════════════════════════════════════╗
║                QUERY DECOMPOSITION REPORT                         ║
╚═══════════════════════════════════════════════════════════════════╝

Original Query: {decomposed.original_query}

📊 Complexity: {decomposed.complexity.value.upper()}
🔀 Multi-domain: {decomposed.is_multi_domain}
🔗 Requires synthesis: {decomposed.requires_synthesis}

🎯 Atomic Queries ({len(decomposed.atomic_queries)} total):
"""
        for i, aq in enumerate(decomposed.atomic_queries, 1):
            report += f"  {i}. [{aq.priority}] {aq.query_text}\n"
            if aq.domain:
                report += f"     Domain: {aq.domain}\n"
            if aq.keywords:
                report += f"     Keywords: {', '.join(aq.keywords[:3])}\n"

        if decomposed.alternative_phrasings:
            report += f"""
🔍 Alternative Phrasings:
"""
            for alt in decomposed.alternative_phrasings[:3]:
                report += f"  • {alt}\n"

        return report.strip()
