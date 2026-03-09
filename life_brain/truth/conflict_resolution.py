"""
Conflict resolution UX and protocol.

Displays conflicting information and provides resolution options
for documents with contradictory fields.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ResolutionOption(Enum):
    """Resolution options for conflicts."""
    KEEP_EXISTING = "keep_existing"  # Keep original value
    USE_NEW = "use_new"  # Use new value
    MERGE = "merge"  # Combine both values
    MANUAL = "manual"  # User provides custom value
    SKIP = "skip"  # Skip this field


@dataclass
class Conflict:
    """A conflicting field in a document."""

    field_name: str
    existing_value: Any
    new_value: Any
    confidence_existing: float = 0.9  # 0-1 confidence in existing
    confidence_new: float = 0.7  # 0-1 confidence in new
    conflict_type: str = "content_mismatch"  # Type of conflict
    severity: str = "medium"  # low, medium, high, critical
    source_new: str = "user_input"  # Where new value comes from
    timestamp_existing: str = field(default_factory=lambda: datetime.now().isoformat())
    timestamp_new: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "field_name": self.field_name,
            "existing_value": self.existing_value,
            "new_value": self.new_value,
            "confidence_existing": self.confidence_existing,
            "confidence_new": self.confidence_new,
            "conflict_type": self.conflict_type,
            "severity": self.severity,
            "source_new": self.source_new,
            "timestamp_existing": self.timestamp_existing,
            "timestamp_new": self.timestamp_new,
        }

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate conflict."""
        errors = []

        if not self.field_name or not self.field_name.strip():
            errors.append("field_name is required")

        if not (0 <= self.confidence_existing <= 1):
            errors.append("confidence_existing must be 0-1")

        if not (0 <= self.confidence_new <= 1):
            errors.append("confidence_new must be 0-1")

        valid_severities = ["low", "medium", "high", "critical"]
        if self.severity not in valid_severities:
            errors.append(f"severity must be one of: {valid_severities}")

        return len(errors) == 0, errors


@dataclass
class ConflictPrompt:
    """A conflict prompt to be shown for resolution."""

    prompt_id: str
    document_id: str
    conflict: Conflict
    recommended_resolution: ResolutionOption = ResolutionOption.USE_NEW
    available_options: List[ResolutionOption] = field(
        default_factory=lambda: [
            ResolutionOption.KEEP_EXISTING,
            ResolutionOption.USE_NEW,
            ResolutionOption.MERGE,
            ResolutionOption.SKIP,
        ]
    )
    context: str = ""  # Additional context for user
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_display_dict(self) -> Dict[str, Any]:
        """Convert to user-display format."""
        return {
            "prompt_id": self.prompt_id,
            "field": self.conflict.field_name,
            "existing": {
                "value": self.conflict.existing_value,
                "confidence": f"{self.conflict.confidence_existing:.0%}",
                "timestamp": self.conflict.timestamp_existing,
            },
            "new": {
                "value": self.conflict.new_value,
                "confidence": f"{self.conflict.confidence_new:.0%}",
                "source": self.conflict.source_new,
                "timestamp": self.conflict.timestamp_new,
            },
            "severity": self.conflict.severity,
            "recommended": self.recommended_resolution.value,
            "options": [opt.value for opt in self.available_options],
            "context": self.context,
        }


class ConflictResolver:
    """Resolve conflicts with user/system prompts."""

    # Severity levels
    SEVERITY_LEVELS = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4,
    }

    def __init__(self):
        """Initialize conflict resolver."""
        self.active_prompts: Dict[str, ConflictPrompt] = {}  # prompt_id -> ConflictPrompt
        self.resolutions: Dict[str, Dict[str, Any]] = {}  # prompt_id -> resolution
        self.conflict_history: List[Dict[str, Any]] = []

    def conflict_prompt(
        self,
        document_id: str,
        field_name: str,
        existing_value: Any,
        new_value: Any,
        confidence_existing: float = 0.9,
        confidence_new: float = 0.7,
        conflict_type: str = "content_mismatch",
        source_new: str = "user_input",
        context: str = "",
        available_options: Optional[List[ResolutionOption]] = None,
    ) -> ConflictPrompt:
        """
        Create a conflict resolution prompt.

        Args:
            document_id: Document with conflict
            field_name: Field with conflicting values
            existing_value: Current value
            new_value: Proposed/new value
            confidence_existing: Confidence in existing value (0-1)
            confidence_new: Confidence in new value (0-1)
            conflict_type: Type of conflict
            source_new: Source of new value
            context: Additional context for resolution
            available_options: Options available to user (default: all except MANUAL)

        Returns:
            ConflictPrompt object
        """
        # Determine severity
        difference = abs(confidence_new - confidence_existing)
        if difference < 0.1:
            severity = "medium"
        elif confidence_new > confidence_existing:
            severity = "high"
        else:
            severity = "low"

        # Create conflict
        conflict = Conflict(
            field_name=field_name,
            existing_value=existing_value,
            new_value=new_value,
            confidence_existing=confidence_existing,
            confidence_new=confidence_new,
            conflict_type=conflict_type,
            severity=severity,
            source_new=source_new,
        )

        # Validate
        is_valid, errors = conflict.validate()
        if not is_valid:
            raise ValueError(f"Invalid conflict: {errors}")

        # Determine recommended resolution
        recommended = (
            ResolutionOption.USE_NEW
            if confidence_new >= confidence_existing
            else ResolutionOption.KEEP_EXISTING
        )

        # Create prompt
        prompt_id = f"conflict_{document_id}_{field_name}_{hash(str(new_value)) % 10000:04d}"

        if available_options is None:
            available_options = [
                ResolutionOption.KEEP_EXISTING,
                ResolutionOption.USE_NEW,
                ResolutionOption.MERGE,
                ResolutionOption.SKIP,
            ]

        prompt = ConflictPrompt(
            prompt_id=prompt_id,
            document_id=document_id,
            conflict=conflict,
            recommended_resolution=recommended,
            available_options=available_options,
            context=context,
        )

        # Store active prompt
        self.active_prompts[prompt_id] = prompt

        return prompt

    def get_active_prompts(self) -> List[ConflictPrompt]:
        """Get all active conflict prompts."""
        return list(self.active_prompts.values())

    def get_prompts_for_document(self, document_id: str) -> List[ConflictPrompt]:
        """Get conflicts for a specific document."""
        return [
            p for p in self.active_prompts.values()
            if p.document_id == document_id
        ]

    def get_prompts_by_severity(
        self,
        severity: str,
    ) -> List[ConflictPrompt]:
        """Get prompts by severity level."""
        return [
            p for p in self.active_prompts.values()
            if p.conflict.severity == severity
        ]

    def resolve_conflict(
        self,
        prompt_id: str,
        chosen_option: ResolutionOption,
        custom_value: Optional[Any] = None,
        reasoning: str = "",
    ) -> Tuple[bool, Optional[str]]:
        """
        Record conflict resolution.

        Args:
            prompt_id: Prompt being resolved
            chosen_option: Resolution option chosen
            custom_value: If MANUAL option, the custom value
            reasoning: User/system reasoning for choice

        Returns:
            (success, error_message)
        """
        if prompt_id not in self.active_prompts:
            return False, f"Prompt {prompt_id} not found"

        prompt = self.active_prompts[prompt_id]

        # Determine resolved value
        resolved_value = None
        if chosen_option == ResolutionOption.KEEP_EXISTING:
            resolved_value = prompt.conflict.existing_value
        elif chosen_option == ResolutionOption.USE_NEW:
            resolved_value = prompt.conflict.new_value
        elif chosen_option == ResolutionOption.MERGE:
            # Merge both values (representation depends on data type)
            if isinstance(prompt.conflict.existing_value, list):
                resolved_value = list(
                    set(prompt.conflict.existing_value + prompt.conflict.new_value)
                )
            elif isinstance(prompt.conflict.existing_value, dict):
                resolved_value = {
                    **prompt.conflict.existing_value,
                    **prompt.conflict.new_value,
                }
            else:
                resolved_value = f"{prompt.conflict.existing_value} / {prompt.conflict.new_value}"
        elif chosen_option == ResolutionOption.MANUAL:
            resolved_value = custom_value
        elif chosen_option == ResolutionOption.SKIP:
            resolved_value = None
        else:
            return False, f"Unknown resolution option: {chosen_option}"

        # Record resolution
        resolution = {
            "prompt_id": prompt_id,
            "document_id": prompt.document_id,
            "field_name": prompt.conflict.field_name,
            "existing_value": prompt.conflict.existing_value,
            "new_value": prompt.conflict.new_value,
            "chosen_option": chosen_option.value,
            "resolved_value": resolved_value,
            "reasoning": reasoning,
            "resolved_at": datetime.now().isoformat(),
        }

        self.resolutions[prompt_id] = resolution
        self.conflict_history.append(resolution)

        # Remove from active
        del self.active_prompts[prompt_id]

        return True, None

    def get_resolution(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """Get resolution for a prompt."""
        return self.resolutions.get(prompt_id)

    def get_conflict_history(self) -> List[Dict[str, Any]]:
        """Get history of all resolved conflicts."""
        return self.conflict_history

    def get_document_conflicts(self, document_id: str) -> Dict[str, Any]:
        """Get all conflicts/resolutions for a document."""
        active = self.get_prompts_for_document(document_id)
        resolved = [
            r for r in self.conflict_history
            if r["document_id"] == document_id
        ]

        return {
            "document_id": document_id,
            "active_conflicts": len(active),
            "resolved_conflicts": len(resolved),
            "active": [p.to_display_dict() for p in active],
            "resolved": resolved,
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get conflict resolution statistics."""
        total_resolved = len(self.conflict_history)

        if total_resolved == 0:
            return {
                "active_prompts": len(self.active_prompts),
                "resolved_conflicts": 0,
                "by_resolution_option": {},
                "by_severity": {},
            }

        # Count by resolution option
        by_option = {}
        for entry in self.conflict_history:
            option = entry["chosen_option"]
            by_option[option] = by_option.get(option, 0) + 1

        # Count by severity
        by_severity = {}
        for prompt in self.active_prompts.values():
            severity = prompt.conflict.severity
            by_severity[severity] = by_severity.get(severity, 0) + 1

        for entry in self.conflict_history:
            # Get severity from original prompt (if still available)
            # For now, estimate from reasoning or other clues
            pass

        return {
            "active_prompts": len(self.active_prompts),
            "resolved_conflicts": total_resolved,
            "by_resolution_option": by_option,
            "by_severity": by_severity,
        }

    def export_active_conflicts(self) -> List[Dict[str, Any]]:
        """Export all active conflict prompts for display."""
        return [
            p.to_display_dict()
            for p in sorted(
                self.active_prompts.values(),
                key=lambda p: self.SEVERITY_LEVELS.get(p.conflict.severity, 0),
                reverse=True,
            )
        ]

    def export_resolution_history(self) -> List[Dict[str, Any]]:
        """Export complete resolution history."""
        return sorted(
            self.conflict_history,
            key=lambda x: x["resolved_at"],
            reverse=True,
        )
