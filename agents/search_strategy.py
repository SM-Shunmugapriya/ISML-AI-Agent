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
        "pdf"
    ]
}}

The search_tools values MUST contain only:
"web", "youtube", or "pdf".
"""

    try:
        response = ask_llm(prompt, provider="gemini")

        search_queries = response.get(
            "search_queries",
            []
        )

        search_tools = response.get(
            "search_tools",
            []
        )

        # Allow only supported search tools
        valid_tools = {
            "web",
            "youtube",
            "pdf"
        }

        search_tools = [
            tool
            for tool in search_tools
            if tool in valid_tools
        ]

        # Fallback to web search
        # if the LLM returns no valid tools.
        if not search_tools:
            search_tools = ["web"]

        result = {
            **state,
            "search_queries": search_queries,
            "search_tools": search_tools,
        }

        log_info(
            f"Search strategy completed | "
            f"queries_count={len(search_queries)} | "
            f"selected_tools={search_tools}"
        )

        return result

    except Exception as e:
        log_error(
            f"Search strategy generation failed | error={e}"
        )
        raise