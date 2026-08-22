from langgraph.graph import StateGraph, START, END

from agents.state import AgentState
from agents.topic_analysis import analyze_topic
from agents.search_strategy import generate_search_strategy
from agents.resource_discovery import discover_resources
from agents.metadata_extraction import extract_resource_metadata
from agents.validation import validate_resources
from agents.deduplication import deduplicate_resources
from agents.evaluation import evaluate_resources
from agents.ranking import rank_resources
from agents.categorization import categorize_resources
from agents.learning_sequence import create_learning_sequence
from agents.database_persistence import persist_resources
from agents.embedding import generate_resource_embeddings

from services.logger import log_info, log_error


log_info("Initializing ISML AI Agent workflow")


try:
    graph = StateGraph(AgentState)

    # Add workflow nodes
    graph.add_node("topic_analysis", analyze_topic)
    graph.add_node("search_strategy", generate_search_strategy)
    graph.add_node("resource_discovery", discover_resources)
    graph.add_node("metadata_extraction", extract_resource_metadata)
    graph.add_node("validation", validate_resources)
    graph.add_node("deduplication", deduplicate_resources)
    graph.add_node("evaluation", evaluate_resources)
    graph.add_node("ranking", rank_resources)
    graph.add_node("categorization", categorize_resources)
    graph.add_node("learning_sequence", create_learning_sequence)
    graph.add_node("database_persistence", persist_resources)
    graph.add_node("embedding", generate_resource_embeddings)

    # Connect workflow nodes
    graph.add_edge(START, "topic_analysis")
    graph.add_edge("topic_analysis", "search_strategy")
    graph.add_edge("search_strategy", "resource_discovery")
    graph.add_edge("resource_discovery", "metadata_extraction")
    graph.add_edge("metadata_extraction", "validation")
    graph.add_edge("validation", "deduplication")
    graph.add_edge("deduplication", "evaluation")
    graph.add_edge("evaluation", "ranking")
    graph.add_edge("ranking", "categorization")
    graph.add_edge("categorization", "learning_sequence")
    graph.add_edge("learning_sequence", "database_persistence")
    graph.add_edge("database_persistence", "embedding")
    graph.add_edge("embedding", END)

    app = graph.compile()

    log_info(
        "ISML AI Agent workflow compiled successfully"
    )

except Exception as e:
    log_error(
        f"Workflow initialization failed | error={e}"
    )
    raise