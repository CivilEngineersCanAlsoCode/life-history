"""
Expert Personas System

16 expert personas for guided conversations across life domains.
Each expert brings distinct perspective, speaking style, and domain expertise.
"""

from .roster import ExpertRoster, Expert
from .context_manager import ExpertContextManager

__all__ = [
    "ExpertRoster",
    "Expert",
    "ExpertContextManager",
]
