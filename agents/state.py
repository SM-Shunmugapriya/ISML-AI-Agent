
from typing import TypedDict, List, Dict, Any


class AgentState(TypedDict, total=False):
    user_query: str

    topic: str
    subtopics: List[str]
    learning_intent: str

    search_queries: List[str]
    search_results: List[Dict[str, Any]]

    resources: List[Dict[str, Any]]
    metadata: List[Dict[str, Any]]
    validated_resources: List[Dict[str, Any]]
    unique_resources: List[Dict[str, Any]]

    evaluated_resources: List[Dict[str, Any]]
    ranked_resources: List[Dict[str, Any]]
    categorized_resources: List[Dict[str, Any]]

    learning_sequence: List[Dict[str, Any]]
    persisted_resources: List[Dict[str, Any]]
    embeddings: List[List[float]]

    final_answer: str