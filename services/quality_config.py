"""
Configurable quality governance thresholds.
"""

QUALITY_THRESHOLDS = {
    "excellent": 90,
    "high_quality": 80,
    "acceptable": 70,
    "review": 0,
}


def get_quality_level(score: float) -> str:
    """Return the governance level for a quality score."""
    if score >= QUALITY_THRESHOLDS["excellent"]:
        return "Excellent"
    if score >= QUALITY_THRESHOLDS["high_quality"]:
        return "High Quality"
    if score >= QUALITY_THRESHOLDS["acceptable"]:
        return "Acceptable"
    return "Review/Reject"


def is_auto_approved(score: float) -> bool:
    """Return True when the score meets the acceptable threshold."""
    return score >= QUALITY_THRESHOLDS["acceptable"]
