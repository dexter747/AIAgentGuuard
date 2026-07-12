"""
Corrective Intelligence Engine

Enhanced corrective engine that integrates with the database for
persistent pattern learning and ML-powered suggestion generation.

This builds on corrective_traces.py to provide:
1. Database persistence for suggestions and patterns
2. ML-powered similarity matching
3. Confidence scoring based on historical approvals
4. Automatic pattern learning from user feedback
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import uuid
import logging
from collections import Counter

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_

from app.models.coordination import (
    CorrectiveSuggestion,
    LearnedPattern,
    CoordinationIssue as CoordinationIssueDB,
    FeedbackStatus,
)
from .corrective_traces import (
    CorrectiveTraceGenerator,
    TraceCorrection,
    CorrectionStrategy,
)
from .coordination_analysis import (
    CoordinationAnalyzer,
    CoordinationIssue,
    CoordinationIssueType,
)

logger = logging.getLogger(__name__)


class SuggestionConfidence(str, Enum):
    """Confidence levels for suggestions."""
    HIGH = "high"  # > 0.8 confidence
    MEDIUM = "medium"  # 0.5 - 0.8 confidence
    LOW = "low"  # < 0.5 confidence


@dataclass
class EnhancedSuggestion:
    """Enhanced suggestion with ML-powered confidence."""
    suggestion: TraceCorrection
    confidence_score: float
    confidence_level: SuggestionConfidence
    similar_patterns: List[Dict[str, Any]]
    historical_success_rate: float
    suggested_priority: str
    auto_applicable: bool  # Can be auto-applied without human review


class CorrectiveEngine:
    """
    Enhanced corrective engine with database integration and pattern learning.

    Features:
    - Persistent storage of suggestions and patterns
    - ML-powered confidence scoring based on historical data
    - Automatic pattern learning from feedback
    - Priority ranking based on impact and confidence

    Usage:
        engine = CorrectiveEngine(db_session)

        # Generate suggestions for an issue
        suggestions = engine.generate_suggestions(org_id, trace_id, traces)

        # Process feedback
        engine.process_feedback(suggestion_id, approved=True, feedback_notes="Works well")
    """

    def __init__(self, db: Session):
        """Initialize corrective engine with database session."""
        self.db = db
        self.trace_generator = CorrectiveTraceGenerator()
        self.analyzer = CoordinationAnalyzer()

        # Confidence thresholds
        self.high_confidence_threshold = 0.8
        self.auto_apply_threshold = 0.95
        self.min_pattern_matches = 3  # Minimum similar patterns for high confidence

    def generate_suggestions(
        self,
        org_id: str,
        trace_id: Optional[str],
        traces: List[Dict[str, Any]],
        issue_id: Optional[str] = None,
    ) -> List[EnhancedSuggestion]:
        """
        Generate enhanced suggestions for coordination issues.

        Args:
            org_id: Organization ID
            trace_id: Optional trace ID that triggered the analysis
            traces: List of trace data to analyze
            issue_id: Optional existing issue ID to generate suggestions for

        Returns:
            List of enhanced suggestions with confidence scores
        """
        enhanced_suggestions = []

        # Get base corrections from trace generator
        corrections = self.trace_generator.generate_corrections(traces)

        # Enhance each correction with ML-powered confidence
        for correction in corrections:
            enhanced = self._enhance_suggestion(org_id, correction)

            # Persist suggestion to database
            db_suggestion = self._persist_suggestion(
                org_id=org_id,
                trace_id=trace_id,
                issue_id=issue_id,
                suggestion=enhanced,
            )

            enhanced.suggestion.original_trace_id = str(db_suggestion.id)
            enhanced_suggestions.append(enhanced)

        # Sort by confidence and priority
        enhanced_suggestions.sort(
            key=lambda s: (s.confidence_score, s.suggested_priority == "critical"),
            reverse=True
        )

        return enhanced_suggestions

    def _enhance_suggestion(
        self,
        org_id: str,
        correction: TraceCorrection
    ) -> EnhancedSuggestion:
        """Enhance a suggestion with ML-powered confidence scoring."""

        # Find similar learned patterns
        similar_patterns = self._find_similar_patterns(
            org_id=org_id,
            issue_type=correction.issue.issue_type.value,
            strategy=correction.correction_strategy.value,
        )

        # Calculate confidence based on historical data
        confidence_score = self._calculate_confidence(
            base_confidence=correction.confidence,
            similar_patterns=similar_patterns,
        )

        # Determine confidence level
        if confidence_score >= self.high_confidence_threshold:
            confidence_level = SuggestionConfidence.HIGH
        elif confidence_score >= 0.5:
            confidence_level = SuggestionConfidence.MEDIUM
        else:
            confidence_level = SuggestionConfidence.LOW

        # Calculate historical success rate
        success_rate = self._calculate_success_rate(similar_patterns)

        # Determine priority based on issue severity
        priority = self._determine_priority(correction.issue, confidence_score)

        # Determine if auto-applicable
        auto_applicable = (
            confidence_score >= self.auto_apply_threshold and
            success_rate >= 0.9 and
            len(similar_patterns) >= self.min_pattern_matches
        )

        return EnhancedSuggestion(
            suggestion=correction,
            confidence_score=confidence_score,
            confidence_level=confidence_level,
            similar_patterns=[
                {
                    "pattern_id": str(p.id),
                    "strategy": p.strategy,
                    "success_count": p.success_count,
                    "total_applications": p.total_applications,
                }
                for p in similar_patterns[:5]  # Top 5 similar patterns
            ],
            historical_success_rate=success_rate,
            suggested_priority=priority,
            auto_applicable=auto_applicable,
        )

    def _find_similar_patterns(
        self,
        org_id: str,
        issue_type: str,
        strategy: str,
    ) -> List[LearnedPattern]:
        """Find similar learned patterns from the database."""

        # Query for matching patterns
        patterns = self.db.query(LearnedPattern).filter(
            and_(
                LearnedPattern.org_id == uuid.UUID(org_id),
                LearnedPattern.issue_type == issue_type,
                LearnedPattern.strategy == strategy,
                LearnedPattern.is_active == True,
            )
        ).order_by(
            desc(LearnedPattern.success_rate),
            desc(LearnedPattern.total_applications),
        ).limit(10).all()

        return patterns

    def _calculate_confidence(
        self,
        base_confidence: float,
        similar_patterns: List[LearnedPattern],
    ) -> float:
        """Calculate confidence score based on base confidence and historical patterns."""

        if not similar_patterns:
            # No historical data, use base confidence with slight reduction
            return base_confidence * 0.8

        # Calculate weighted average success rate
        total_applications = sum(p.total_applications for p in similar_patterns)
        if total_applications == 0:
            return base_confidence

        weighted_success_rate = sum(
            p.success_rate * p.total_applications
            for p in similar_patterns
        ) / total_applications

        # Combine base confidence with historical success rate
        # More weight to historical data as we have more samples
        sample_weight = min(total_applications / 20, 0.7)  # Max 70% weight to history
        base_weight = 1 - sample_weight

        confidence = (base_confidence * base_weight) + (weighted_success_rate * sample_weight)

        # Boost confidence if we have many successful matches
        if len(similar_patterns) >= self.min_pattern_matches and weighted_success_rate > 0.8:
            confidence = min(confidence * 1.1, 0.99)

        return round(confidence, 3)

    def _calculate_success_rate(self, patterns: List[LearnedPattern]) -> float:
        """Calculate historical success rate from similar patterns."""
        if not patterns:
            return 0.0

        total_success = sum(p.success_count for p in patterns)
        total_applications = sum(p.total_applications for p in patterns)

        if total_applications == 0:
            return 0.0

        return round(total_success / total_applications, 3)

    def _determine_priority(
        self,
        issue: CoordinationIssue,
        confidence: float,
    ) -> str:
        """Determine suggestion priority based on issue severity and confidence."""

        # High severity issues with high confidence are critical
        if issue.severity == "critical":
            if confidence >= 0.7:
                return "critical"
            return "high"

        if issue.severity == "high":
            if confidence >= 0.8:
                return "high"
            return "medium"

        if issue.severity == "medium":
            if confidence >= 0.8:
                return "medium"
            return "low"

        return "low"

    def _persist_suggestion(
        self,
        org_id: str,
        trace_id: Optional[str],
        issue_id: Optional[str],
        suggestion: EnhancedSuggestion,
    ) -> CorrectiveSuggestion:
        """Persist suggestion to database."""

        db_suggestion = CorrectiveSuggestion(
            id=uuid.uuid4(),
            org_id=uuid.UUID(org_id),
            issue_id=uuid.UUID(issue_id) if issue_id else None,
            trace_id=uuid.UUID(trace_id) if trace_id else None,
            suggestion_type=suggestion.suggestion.correction_strategy.value,
            title=suggestion.suggestion.description,
            description=f"Suggested fix: {suggestion.suggestion.description}",
            suggested_fix=json.dumps(suggestion.suggestion.corrected_trace),
            confidence_score=suggestion.confidence_score,
            priority=suggestion.suggested_priority,
            status=FeedbackStatus.PENDING,
            evidence={
                "changes": suggestion.suggestion.changes,
                "similar_patterns": suggestion.similar_patterns,
                "historical_success_rate": suggestion.historical_success_rate,
                "auto_applicable": suggestion.auto_applicable,
            },
        )

        self.db.add(db_suggestion)
        self.db.commit()
        self.db.refresh(db_suggestion)

        return db_suggestion

    def process_feedback(
        self,
        suggestion_id: str,
        approved: bool,
        feedback_notes: Optional[str] = None,
        applied_changes: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process user feedback for a suggestion.

        Args:
            suggestion_id: ID of the suggestion
            approved: Whether the suggestion was approved
            feedback_notes: Optional notes from the user
            applied_changes: Optional details of how the fix was applied

        Returns:
            Result of feedback processing including pattern learning status
        """
        # Get suggestion from database
        suggestion = self.db.query(CorrectiveSuggestion).filter(
            CorrectiveSuggestion.id == uuid.UUID(suggestion_id)
        ).first()

        if not suggestion:
            raise ValueError(f"Suggestion {suggestion_id} not found")

        # Update suggestion status
        suggestion.status = FeedbackStatus.APPROVED if approved else FeedbackStatus.REJECTED
        suggestion.feedback_notes = feedback_notes
        suggestion.feedback_at = datetime.utcnow()

        result = {
            "suggestion_id": suggestion_id,
            "status": suggestion.status.value,
            "pattern_learned": False,
        }

        if approved:
            # Learn from approved suggestion
            pattern = self._learn_pattern(suggestion, applied_changes)
            result["pattern_learned"] = True
            result["pattern_id"] = str(pattern.id)
        else:
            # Update existing patterns if this was a failure
            self._record_pattern_failure(suggestion)

        self.db.commit()

        return result

    def _learn_pattern(
        self,
        suggestion: CorrectiveSuggestion,
        applied_changes: Optional[Dict[str, Any]],
    ) -> LearnedPattern:
        """Learn a new pattern from an approved suggestion."""

        # Check if pattern already exists
        existing_pattern = self.db.query(LearnedPattern).filter(
            and_(
                LearnedPattern.org_id == suggestion.org_id,
                LearnedPattern.issue_type == suggestion.suggestion_type,
                LearnedPattern.strategy == suggestion.suggestion_type,
            )
        ).first()

        if existing_pattern:
            # Update existing pattern
            existing_pattern.success_count += 1
            existing_pattern.total_applications += 1
            existing_pattern.success_rate = (
                existing_pattern.success_count / existing_pattern.total_applications
            )
            existing_pattern.updated_at = datetime.utcnow()

            # Merge pattern data
            if applied_changes:
                current_data = existing_pattern.pattern_data or {}
                current_data["recent_applications"] = current_data.get("recent_applications", [])
                current_data["recent_applications"].append({
                    "suggestion_id": str(suggestion.id),
                    "applied_at": datetime.utcnow().isoformat(),
                    "changes": applied_changes,
                })
                # Keep only last 10 applications
                current_data["recent_applications"] = current_data["recent_applications"][-10:]
                existing_pattern.pattern_data = current_data

            return existing_pattern

        # Create new pattern
        pattern = LearnedPattern(
            id=uuid.uuid4(),
            org_id=suggestion.org_id,
            source_suggestion_id=suggestion.id,
            issue_type=suggestion.suggestion_type,
            strategy=suggestion.suggestion_type,
            pattern_data={
                "fix_template": json.loads(suggestion.suggested_fix) if suggestion.suggested_fix else {},
                "source_suggestion_id": str(suggestion.id),
                "first_applied": datetime.utcnow().isoformat(),
            },
            success_count=1,
            total_applications=1,
            success_rate=1.0,
            is_active=True,
        )

        self.db.add(pattern)
        return pattern

    def _record_pattern_failure(self, suggestion: CorrectiveSuggestion):
        """Record a pattern failure when suggestion is rejected."""

        # Find matching pattern
        pattern = self.db.query(LearnedPattern).filter(
            and_(
                LearnedPattern.org_id == suggestion.org_id,
                LearnedPattern.issue_type == suggestion.suggestion_type,
                LearnedPattern.strategy == suggestion.suggestion_type,
            )
        ).first()

        if pattern:
            # Update failure count
            pattern.total_applications += 1
            pattern.success_rate = pattern.success_count / pattern.total_applications
            pattern.updated_at = datetime.utcnow()

            # Deactivate pattern if success rate drops too low
            if pattern.success_rate < 0.3 and pattern.total_applications >= 5:
                pattern.is_active = False
                logger.info(
                    f"Deactivated pattern {pattern.id} due to low success rate: "
                    f"{pattern.success_rate}"
                )

    def get_organization_patterns(
        self,
        org_id: str,
        include_inactive: bool = False,
    ) -> List[Dict[str, Any]]:
        """Get all learned patterns for an organization."""

        query = self.db.query(LearnedPattern).filter(
            LearnedPattern.org_id == uuid.UUID(org_id)
        )

        if not include_inactive:
            query = query.filter(LearnedPattern.is_active == True)

        patterns = query.order_by(
            desc(LearnedPattern.success_rate),
            desc(LearnedPattern.total_applications),
        ).all()

        return [
            {
                "id": str(p.id),
                "issue_type": p.issue_type,
                "strategy": p.strategy,
                "success_count": p.success_count,
                "total_applications": p.total_applications,
                "success_rate": p.success_rate,
                "is_active": p.is_active,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            }
            for p in patterns
        ]

    def get_suggestion_stats(self, org_id: str) -> Dict[str, Any]:
        """Get statistics about suggestions for an organization."""

        # Count suggestions by status
        status_counts = self.db.query(
            CorrectiveSuggestion.status,
            func.count(CorrectiveSuggestion.id)
        ).filter(
            CorrectiveSuggestion.org_id == uuid.UUID(org_id)
        ).group_by(
            CorrectiveSuggestion.status
        ).all()

        status_dict = {status.value: count for status, count in status_counts}

        # Count suggestions by type
        type_counts = self.db.query(
            CorrectiveSuggestion.suggestion_type,
            func.count(CorrectiveSuggestion.id)
        ).filter(
            CorrectiveSuggestion.org_id == uuid.UUID(org_id)
        ).group_by(
            CorrectiveSuggestion.suggestion_type
        ).all()

        type_dict = {stype: count for stype, count in type_counts}

        # Calculate approval rate
        total = sum(status_dict.values())
        approved = status_dict.get("approved", 0)
        approval_rate = approved / total if total > 0 else 0

        return {
            "total_suggestions": total,
            "by_status": status_dict,
            "by_type": type_dict,
            "approval_rate": round(approval_rate, 3),
            "active_patterns": self.db.query(LearnedPattern).filter(
                and_(
                    LearnedPattern.org_id == uuid.UUID(org_id),
                    LearnedPattern.is_active == True,
                )
            ).count(),
        }

    def apply_auto_corrections(
        self,
        org_id: str,
        traces: List[Dict[str, Any]],
        dry_run: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Apply auto-corrections for high-confidence suggestions.

        Args:
            org_id: Organization ID
            traces: Traces to analyze and correct
            dry_run: If True, only return what would be corrected without applying

        Returns:
            List of corrections that were (or would be) applied
        """
        applied = []

        # Generate suggestions
        suggestions = self.generate_suggestions(org_id, None, traces)

        for enhanced in suggestions:
            if enhanced.auto_applicable:
                correction_info = {
                    "suggestion_id": enhanced.suggestion.original_trace_id,
                    "strategy": enhanced.suggestion.correction_strategy.value,
                    "description": enhanced.suggestion.description,
                    "confidence": enhanced.confidence_score,
                    "corrected_trace": enhanced.suggestion.corrected_trace,
                    "dry_run": dry_run,
                }

                if not dry_run:
                    # Mark as auto-applied
                    self.process_feedback(
                        suggestion_id=enhanced.suggestion.original_trace_id,
                        approved=True,
                        feedback_notes="Auto-applied due to high confidence",
                    )
                    correction_info["applied"] = True

                applied.append(correction_info)

        return applied


# Factory function for creating engine instances
def create_corrective_engine(db: Session) -> CorrectiveEngine:
    """Create a corrective engine instance."""
    return CorrectiveEngine(db)
