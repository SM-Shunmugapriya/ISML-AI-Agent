from langgraph.graph import StateGraph, START, END

from agents.state import AgentState
from agents.topic_analysis import analyze_topic
from agents.search_strategy import generate_search_strategy
from agents.resource_discovery import discover_resources
from agents.metadata_extraction import extract_resource_metadata
from agents.validation import validate_resources
from agents.deduplication import deduplicate_resources_node
from agents.evaluation import evaluate_resources
from agents.ranking import rank_resources
from agents.categorization import categorize_resources
from agents.learning_sequence import create_learning_sequence
from agents.database_persistence import persist_resources
from agents.embedding import generate_resource_embeddings
from agents.output_validation import validate_final_output

from services.retrieval_strategy import retrieve_existing_knowledge
from services.logger import log_info, log_error


log_info("Initializing ISML AI Agent workflow")


def observe_node(node_name, node_function):
    def wrapped_node(state, config=None):
        observability = None

        if config:
            observability = (
                config.get("configurable", {})
                .get("observability")
            )

        if observability is None:
            return node_function(state)

        observability.start_stage(node_name)

        try:
            result = node_function(state)

            observability.end_stage(
                node_name,
                status="success"
            )

            return result

        except Exception as e:
            observability.end_stage(
                node_name,
                status="failed",
                error=e
            )
            raise

    return wrapped_node


def route_after_retrieval(state: AgentState) -> str:
    """
    Route to ranking when existing knowledge is sufficient.
    Otherwise continue with the normal discovery pipeline.
    """

    if state.get("retrieval_hit", False):
        log_info(
            "Retrieval routing decision | "
            "existing_knowledge_sufficient=True | "
            "next=ranking"
        )
        return "ranking"

    log_info(
        "Retrieval routing decision | "
        "existing_knowledge_sufficient=False | "
        "next=topic_analysis"
    )
    return "topic_analysis"


try:
    graph = StateGraph(AgentState)

    # Add workflow nodes with observability
    graph.add_node(
        "topic_analysis",
        observe_node("topic_analysis", analyze_topic)
    )

    graph.add_node(
        "search_strategy",
        observe_node("search_strategy", generate_search_strategy)
    )

    graph.add_node(
        "retrieval_strategy",
        observe_node(
            "retrieval_strategy",
            retrieve_existing_knowledge
        )
    )

    graph.add_node(
        "resource_discovery",
        observe_node("resource_discovery", discover_resources)
    )

    graph.add_node(
        "metadata_extraction",
        observe_node("metadata_extraction", extract_resource_metadata)
    )

    graph.add_node(
        "validation",
        observe_node("validation", validate_resources)
    )

    graph.add_node(
        "deduplication",
        observe_node("deduplication", deduplicate_resources_node)
    )

    graph.add_node(
        "evaluation",
        observe_node("evaluation", evaluate_resources)
    )

    graph.add_node(
        "ranking",
        observe_node("ranking", rank_resources)
    )

    graph.add_node(
        "categorization",
        observe_node("categorization", categorize_resources)
    )

    graph.add_node(
        "learning_sequence",
        observe_node("learning_sequence", create_learning_sequence)
    )

    graph.add_node(
        "database_persistence",
        observe_node("database_persistence", persist_resources)
    )

    graph.add_node(
        "embedding",
        observe_node("embedding", generate_resource_embeddings)
    )

    graph.add_node(
        "output_validation",
        observe_node("output_validation", validate_final_output)
    )

    # ENH-006: Check existing knowledge before any discovery/LLM analysis
    graph.add_edge(START, "retrieval_strategy")

    graph.add_conditional_edges(
        "retrieval_strategy",
        route_after_retrieval,
        {
            "ranking": "ranking",
            "topic_analysis": "topic_analysis",
        },
    )

    # Normal discovery path
    graph.add_edge("topic_analysis", "search_strategy")
    graph.add_edge("search_strategy", "resource_discovery")

    graph.add_edge("resource_discovery", "metadata_extraction")
    graph.add_edge("metadata_extraction", "validation")
    graph.add_edge("validation", "deduplication")
    graph.add_edge("deduplication", "evaluation")
    graph.add_edge("evaluation", "ranking")

    # ENH-006: Reuse existing knowledge without re-categorizing,
    # persisting, or re-embedding resources.
    def route_after_ranking(state: AgentState) -> str:
        if state.get("retrieval_hit", False):
            log_info(
                "Retrieval downstream routing | "
                "existing_knowledge=True | next=learning_sequence"
            )
            return "learning_sequence"

        return "categorization"

    def route_after_learning_sequence(state: AgentState) -> str:
        if state.get("retrieval_hit", False):
            log_info(
                "Retrieval completion routing | "
                "existing_knowledge=True | next=output_validation"
            )
            return "output_validation"

        return "database_persistence"

    graph.add_conditional_edges(
        "ranking",
        route_after_ranking,
        {
            "learning_sequence": "learning_sequence",
            "categorization": "categorization",
        },
    )

    graph.add_edge("categorization", "learning_sequence")

    graph.add_conditional_edges(
        "learning_sequence",
        route_after_learning_sequence,
        {
            "output_validation": "output_validation",
            "database_persistence": "database_persistence",
        },
    )

    graph.add_edge("database_persistence", "embedding")
    graph.add_edge("embedding", "output_validation")
    graph.add_edge("output_validation", END)

    app = graph.compile()

    log_info(
        "ISML AI Agent workflow compiled successfully"
    )

except Exception as e:
    log_error(
        f"Workflow initialization failed | error={e}"
    )
    raise

agent_workflow = app
