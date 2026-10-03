from dataclasses import dataclass


@dataclass(frozen=True)
class ModelRoute:
    provider: str
    model: str
    reason: str


class ModelRouter:
    """
    Select the cheapest capable model based on task complexity.
    """

    SIMPLE_MODEL = ModelRoute(
        provider="gemini",
        model="gemini-3.6-flash",
        reason="Simple task uses fast and low-cost model",
    )

    COMPLEX_MODEL = ModelRoute(
        provider="deepseek",
        model="deepseek-chat",
        reason="Complex task uses more capable model",
    )

    def route(self, task: str) -> ModelRoute:
        task_lower = task.lower()

        complex_keywords = [
            "complex",
            "analyze",
            "analysis",
            "reason",
            "reasoning",
            "compare",
            "evaluate",
            "multi-step",
            "architecture",
            "debug",
        ]

        if any(
            keyword in task_lower
            for keyword in complex_keywords
        ):
            return self.COMPLEX_MODEL

        return self.SIMPLE_MODEL


model_router = ModelRouter()