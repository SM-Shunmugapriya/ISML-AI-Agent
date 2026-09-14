from agents.workflow import app


def test_end_to_end_workflow():
    initial_state = {
        "user_query": "Learn Python programming basics",
    }

    result = app.invoke(initial_state)

    assert result["topic"]
    assert "validated_output" in result

    output = result["validated_output"]

    assert "topic" in output
    assert "recommendedResources" in output
    assert "learningSequence" in output

    assert isinstance(output["recommendedResources"], list)
    assert isinstance(output["learningSequence"], list)

    assert "persisted_resources" in result
    assert "embeddings" in result
