"""
Use Case Catalog System

Provides access to 40+ guided conversation use cases across 7 categories.
Implements semantic matching to surface top-10 most relevant use cases.
"""

from .catalog import UseCaseCatalog, UseCase
from .matcher import UseCaseMatcher, MatchResult

__all__ = [
    "UseCaseCatalog",
    "UseCase",
    "UseCaseMatcher",
    "MatchResult",
]
