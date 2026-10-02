from typing import Dict, Any


class RankingExplainer:
    """
    Generates human-readable explanations for resource rankings.
    """

    FACTOR_LABELS = {
        "relevance": "Relevance",
        "educational_quality": "Educational Quality",
        "credibility": "Credibility",
        "learning_effectiveness": "Learning Effectiveness",
    }

    def build_factor_breakdown(
        self,
        scores: Dict[str, Any],
    ) -> Dict[str, float]:
        """
        Convert evaluation scores from 0.0-1.0 to 0-100 percentages.
        """

        return {
            key: round(float(scores.get(key, 0.0)) * 100, 2)
            for key in self.FACTOR_LABELS
        }

    def generate_explanation(
        self,
        resource: Dict[str, Any],
        rank: int,
    ) -> Dict[str, Any]:
        """
        Generate factor breakdown and natural-language ranking explanation.
        """

        scores = resource.get("scores", {})

        factors = self.build_factor_breakdown(scores)

        strongest_factor = max(
            factors,
            key=factors.get,
            default="relevance",
        )

        strongest_score = factors.get(
            strongest_factor,
            0.0,
        )

        strongest_label = self.FACTOR_LABELS.get(
            strongest_factor,
            strongest_factor,
        )

        explanation = (
            f"Ranked #{rank} with a quality score of "
            f"{resource.get('overall_score', 0.0)}. "
            f"The strongest factor is {strongest_label} "
            f"({strongest_score:.0f}/100), contributing to its "
            f"overall ranking."
        )

        return {
            "factor_breakdown": factors,
            "ranking_explanation": explanation,
        }