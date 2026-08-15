from typing import Dict, Any, List

from services.resource_evaluator import ResourceEvaluator


class ResourceRanker:
    """
    Rank and recommend educational resources
    based on their evaluation scores.
    """

    def __init__(self):
        self.evaluator = ResourceEvaluator()

    def rank_resources(
        self,
        resources: List[Dict[str, Any]],
        topic: str
    ) -> List[Dict[str, Any]]:
        """
        Evaluate and rank resources from highest to lowest score.
        """

        evaluated_resources = []

        for resource in resources:
            evaluation = self.evaluator.evaluate(
                resource,
                topic
            )

            evaluated_resources.append(evaluation)

        evaluated_resources.sort(
            key=lambda x: x["overall_score"],
            reverse=True
        )

        return evaluated_resources

    def get_recommendations(
        self,
        resources: List[Dict[str, Any]],
        topic: str,
        top_n: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Return the top N recommended resources.
        """

        ranked_resources = self.rank_resources(
            resources,
            topic
        )

        return ranked_resources[:top_n]