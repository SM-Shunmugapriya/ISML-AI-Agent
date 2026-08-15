from typing import Dict, Any


class ResourceEvaluator:
    """
    Framework for evaluating the quality of educational resources.
    """

    def __init__(self):
        self.criteria = {
            "relevance": 0.30,
            "educational_quality": 0.25,
            "credibility": 0.20,
            "learning_effectiveness": 0.25,
        }

    def calculate_relevance(
        self, topic: str, resource: Dict[str, Any]
    ) -> float:
        """
        Calculate how relevant a resource is to the requested topic.
        Returns a score between 0.0 and 1.0.
        """

        topic_words = set(topic.lower().split())

        title = resource.get("title", "").lower()
        content = resource.get("content", "").lower()

        if not topic_words:
            return 0.0

        title_matches = sum(word in title for word in topic_words)
        content_matches = sum(word in content for word in topic_words)

        title_score = title_matches / len(topic_words)
        content_score = content_matches / len(topic_words)

        relevance_score = (title_score * 0.7) + (content_score * 0.3)

        return round(min(relevance_score, 1.0), 2)

    def calculate_educational_quality(
        self, resource: Dict[str, Any]
    ) -> float:
        """
        Calculate the educational quality of a resource.
        Returns a score between 0.0 and 1.0.
        """

        title = resource.get("title", "").lower()
        content = resource.get("content", "").lower()

        score = 0.0

        educational_keywords = [
            "tutorial",
            "course",
            "guide",
            "lesson",
            "learn",
            "learning",
            "example",
            "examples",
            "explained",
            "documentation",
        ]

        title_matches = sum(
            keyword in title for keyword in educational_keywords
        )

        if title_matches > 0:
            score += 0.5

        content_matches = sum(
            keyword in content for keyword in educational_keywords
        )

        if content_matches >= 3:
            score += 0.5
        elif content_matches >= 1:
            score += 0.3

        return round(min(score, 1.0), 2)

    def calculate_credibility(
        self, resource: Dict[str, Any]
    ) -> float:
        """
        Calculate the credibility of a resource based on its source.
        Returns a score between 0.0 and 1.0.
        """

        url = resource.get("url", "").lower()

        if ".edu" in url or ".gov" in url:
            return 1.0

        if "wikipedia.org" in url or "python.org" in url:
            return 0.95

        if "github.com" in url:
            return 0.85

        if "youtube.com" in url or "youtu.be" in url:
            return 0.80

        if url.startswith("https://"):
            return 0.70

        return 0.50

    def calculate_learning_effectiveness(
        self, resource: Dict[str, Any]
    ) -> float:
        """
        Calculate how effective a resource is for learning.
        Returns a score between 0.0 and 1.0.
        """

        title = resource.get("title", "").lower()
        content = resource.get("content", "").lower()

        text = f"{title} {content}"

        learning_keywords = [
            "example",
            "examples",
            "exercise",
            "exercises",
            "practice",
            "practical",
            "hands-on",
            "step-by-step",
            "project",
            "code",
        ]

        matches = sum(
            keyword in text for keyword in learning_keywords
        )

        if matches >= 5:
            score = 1.0
        elif matches >= 3:
            score = 0.8
        elif matches >= 1:
            score = 0.6
        else:
            score = 0.4

        return score

    def evaluate(
        self,
        resource: Dict[str, Any],
        topic: str = ""
    ) -> Dict[str, Any]:
        """
        Evaluate a resource using all quality criteria.
        """

        relevance = self.calculate_relevance(topic, resource)
        educational_quality = self.calculate_educational_quality(resource)
        credibility = self.calculate_credibility(resource)
        learning_effectiveness = self.calculate_learning_effectiveness(
            resource
        )

        overall_score = (
            relevance * self.criteria["relevance"]
            + educational_quality * self.criteria["educational_quality"]
            + credibility * self.criteria["credibility"]
            + learning_effectiveness
            * self.criteria["learning_effectiveness"]
        )

        return {
            "resource": resource,
            "scores": {
                "relevance": relevance,
                "educational_quality": educational_quality,
                "credibility": credibility,
                "learning_effectiveness": learning_effectiveness,
            },
            "overall_score": round(overall_score, 2),
        }