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
Create an intelligent web search strategy for this learning topic.

Main topic:
{topic}

Subtopics:
{subtopics}

Generate 5 useful search queries that will help a learner
find accurate and relevant information.

Return ONLY valid JSON in this exact structure:

{{
    "search_queries": [
        "search query 1",
        "search query 2",
        "search query 3",
        "search query 4",
        "search query 5"
    ]
}}
"""

    try:
        response = ask_llm(prompt, provider="gemini")

        log_info(
            "Gemini search strategy generation completed successfully"
        )

        result = {
            **state,
            "search_queries": response.get("search_queries", [])
        }

        log_info(
            f"Search strategy result | queries_count={len(result['search_queries'])}"
        )

        return result

    except Exception as e:
        log_error(
            f"Search strategy generation failed | error={e}"
        )
        raise
