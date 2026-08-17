from services.llm_service import ask_llm
from services.logger import log_info, log_error
from agents.state import AgentState


def analyze_topic(state: AgentState) -> AgentState:
    user_query = state["user_query"]

    log_info(f"Topic analysis started | query={user_query}")

    prompt = f"""
Analyze the following learning request.

User request:
{user_query}

Return ONLY valid JSON in this exact structure:

{{
    "topic": "main topic",
    "subtopics": ["subtopic 1", "subtopic 2"],
    "learning_intent": "what the user wants to learn"
}}
"""

    try:
        response = ask_llm(prompt, provider="gemini")

        log_info("Gemini topic analysis completed successfully")

        result = {
            **state,
            "topic": response.get("topic", ""),
            "subtopics": response.get("subtopics", []),
            "learning_intent": response.get("learning_intent", "")
        }

        log_info(
            f"Topic analysis result | topic={result['topic']}"
        )

        return result

    except Exception as e:
        log_error(f"Topic analysis failed | error={e}")
        raise
