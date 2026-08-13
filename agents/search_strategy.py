from services.llm_service import ask_llm
from agents.state import AgentState


def generate_search_strategy(state: AgentState) -> AgentState:
    topic = state.get("topic", "")
    subtopics = state.get("subtopics", [])

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

    response = ask_llm(prompt, provider="gemini")

    return {
        **state,
        "search_queries": response.get("search_queries", [])
    }