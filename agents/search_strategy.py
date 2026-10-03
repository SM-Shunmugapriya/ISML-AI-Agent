from services.llm_service import ask_llm
from services.logger import log_info, log_error
from agents.state import AgentState


def generate_search_strategy(state: AgentState) -> AgentState:
    topic = state.get("topic", "")
    subtopics = state.get("subtopics", [])

    log_info(
        f"Search strategy generation started | topic={topic}"
    )

    prompt = f"""
Create an intelligent search strategy for this learning topic.

Main topic:
{topic}

Subtopics:
{subtopics}

Generate 5 useful search queries.

Also select the appropriate search tools for the learning topic.

Available search tools:

- web: General web resources, documentation, articles, and tutorials
- youtube: Video tutorials, lectures, and demonstrations
- pdf: Academic papers, lecture notes, textbooks, and study materials
- audio: Audio lectures, podcasts, spoken tutorials, and educational recordings

Select one or more appropriate tools.

Return ONLY valid JSON in this exact structure:

{{
    "search_queries": [
        "search query 1",
        "search query 2",
        "search query 3",
        "search query 4",
        "search query 5"
    ],
    "search_tools": [
        "web",
        "youtube",
        "pdf",
        "audio"
    ]
}}

The search_tools values MUST contain only:
"web", "youtube", "pdf", or "audio".
"""

    try:
        # ENH-007: Pass workflow run ID when available
        # for cost tracking while keeping compatibility
        # with existing test mocks.
        workflow_run_id = state.get("workflow_run_id")

        if workflow_run_id:
            response = ask_llm(
                prompt,
                workflow_run_id=workflow_run_id
            )
        else:
            response = ask_llm(prompt)

        log_info("Search strategy generation completed successfully")

        result = {
            **state,
            "search_queries": response.get(
                "search_queries",
                []
            ),
            "search_tools": response.get(
                "search_tools",
                ["web"]
            )
        }

        log_info(
            f"Search strategy result | "
            f"queries={len(result['search_queries'])} | "
            f"tools={result['search_tools']}"
        )

        return result

    except Exception as e:
        log_error(
            f"Search strategy generation failed | error={e}"
        )
        raise
