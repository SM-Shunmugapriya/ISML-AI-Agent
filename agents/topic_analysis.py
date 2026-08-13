from services.llm_service import ask_llm
from agents.state import AgentState


def analyze_topic(state: AgentState) -> AgentState:
    user_query = state["user_query"]

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

    response = ask_llm(prompt, provider="gemini")

    return {
        **state,
        "topic": response.get("topic", ""),
        "subtopics": response.get("subtopics", []),
        "learning_intent": response.get("learning_intent", "")
    }