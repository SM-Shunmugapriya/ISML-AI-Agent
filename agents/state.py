from typing import TypedDict, List


class AgentState(TypedDict, total=False):
    user_query: str
    topic: str
    subtopics: List[str]
    learning_intent: str
    search_queries: List[str]
    search_results: List[str]
    final_answer: str
