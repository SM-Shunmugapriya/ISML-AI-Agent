from agents.workflow import graph


def test_complete_workflow_structure():
    nodes = graph.nodes

    expected_nodes = [
        "topic_analysis",
        "search_strategy",
        "resource_discovery",
        "metadata_extraction",
        "validation",
        "deduplication",
        "evaluation",
        "ranking",
        "categorization",
        "learning_sequence",
        "database_persistence",
        "embedding",
    ]

    for node in expected_nodes:
        assert node in nodes


def test_workflow_has_all_required_nodes():
    assert len(graph.nodes) == 12