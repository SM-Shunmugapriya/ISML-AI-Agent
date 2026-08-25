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

Identify the user's learning request and return ONLY valid JSON.

The JSON MUST contain all of the following fields:

{{
    "domain": "main domain",
    "course": "course or subject",
    "topic": "main topic",
    "level": "beginner/intermediate/advanced",
    "subtopics": [
        "subtopic 1",
        "subtopic 2"
    ],
    "learning_intent": "what the user wants to learn"
}}

Rules:

1. Always return the "domain" field.
2. Always return the "course" field.
3. Always return the "topic" field.
4. Always return the "level" field.
5. Always return the "subtopics" field as a list.
6. Always return the "learning_intent" field as a string.
7. Do not omit any field.
8. If a value cannot be identified, return "Not specified".
9. Do not return any explanation outside the JSON.
"""

    try:
        response = ask_llm(prompt, provider="gemini")

        log_info("Gemini topic analysis completed successfully")

        result = {
            **state,

            # Required input understanding fields
            "domain": response.get(
                "domain",
                state.get("domain", "Not specified")
            ),

            "course": response.get(
                "course",
                state.get("course", "Not specified")
            ),

            "topic": response.get(
                "topic",
                state.get("topic", "")
            ),

            "level": response.get(
                "level",
                state.get("level", "Not specified")
            ),

            # Existing topic analysis fields
            "subtopics": response.get(
                "subtopics",
                []
            ),

            "learning_intent": response.get(
                "learning_intent",
                ""
            )
        }

        log_info(
            f"Topic analysis result | "
            f"domain={result['domain']} | "
            f"course={result['course']} | "
            f"topic={result['topic']} | "
            f"level={result['level']}"
        )

        return result

    except Exception as e:
        log_error(f"Topic analysis failed | error={e}")
        raise