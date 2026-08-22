from typing import List, Dict, Any

from agents.state import AgentState
from services.logger import log_info, log_error


def categorize_resources(state: AgentState) -> AgentState:
    resources = state.get("ranked_resources", [])

    log_info(
        f"Resource categorization started | resources_count={len(resources)}"
    )

    categorized_resources: List[Dict[str, Any]] = []

    try:
        for resource in resources:
            title = resource.get("resource", {}).get("title", "").lower()
            content = resource.get("resource", {}).get("content", "").lower()

            text = f"{title} {content}"

            if any(
                keyword in text
                for keyword in ["machine learning", "ml", "supervised", "unsupervised"]
            ):
                category = "Machine Learning"

            elif any(
                keyword in text
                for keyword in ["artificial intelligence", " ai ", "intelligent agent"]
            ):
                category = "Artificial Intelligence"

            elif any(
                keyword in text
                for keyword in ["python", "programming", "code", "software"]
            ):
                category = "Programming"

            elif any(
                keyword in text
                for keyword in ["data science", "dataset", "data analysis"]
            ):
                category = "Data Science"

            else:
                category = "General"

            categorized_resources.append({
                **resource,
                "category": category,
            })

        log_info(
            f"Resource categorization completed | categorized_count={len(categorized_resources)}"
        )

        return {
            **state,
            "categorized_resources": categorized_resources,
        }

    except Exception as e:
        log_error(
            f"Resource categorization failed | error={e}"
        )
        raise