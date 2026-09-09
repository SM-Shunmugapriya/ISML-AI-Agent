from typing import TypedDict, List, Dict, Any


class AgentState(TypedDict, total=False):
    # User input
    user_query: str
    domain: str
    course: str
    topic: str
    level: str

    # Topic understanding
    subtopics: List[str]
    learning_intent: str

    # Search strategy
    search_queries: List[str]
    search_tools: List[str]
    search_results: List[Dict[str, Any]]

    # Resource processing
    resources: List[Dict[str, Any]]
    metadata: List[Dict[str, Any]]
    validated_resources: List[Dict[str, Any]]
    unique_resources: List[Dict[str, Any]]

    # Evaluation and ranking
    evaluated_resources: List[Dict[str, Any]]
    ranked_resources: List[Dict[str, Any]]
    categorized_resources: List[Dict[str, Any]]

    # Final processing
    learning_sequence: List[Dict[str, Any]]
    persisted_resources: List[Dict[str, Any]]
    embeddings: List[List[float]]

    # Final answer
    final_answer: str
    validated_output: Dict[str, Any]