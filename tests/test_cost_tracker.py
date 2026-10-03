from services.cost_tracker import CostTracker


def test_calculate_cost():
    tracker = CostTracker()

    cost = tracker.calculate_cost(
        model="deepseek-chat",
        input_tokens=1_000_000,
        output_tokens=1_000_000,
    )

    assert cost == 0.70


def test_record_cost():
    tracker = CostTracker()

    record = tracker.record(
        workflow_run_id="run-001",
        provider="deepseek",
        model="deepseek-chat",
        input_tokens=1000,
        output_tokens=2000,
    )

    assert record.workflow_run_id == "run-001"
    assert record.provider == "deepseek"
    assert record.model == "deepseek-chat"
    assert record.input_tokens == 1000
    assert record.output_tokens == 2000
    assert record.cost > 0


def test_get_run_cost():
    tracker = CostTracker()

    tracker.record(
        workflow_run_id="run-001",
        provider="deepseek",
        model="deepseek-chat",
        input_tokens=1000,
        output_tokens=1000,
    )

    tracker.record(
        workflow_run_id="run-001",
        provider="deepseek",
        model="deepseek-chat",
        input_tokens=2000,
        output_tokens=2000,
    )

    assert tracker.get_run_cost("run-001") > 0


def test_get_run_summary():
    tracker = CostTracker()

    tracker.record(
        workflow_run_id="run-001",
        provider="deepseek",
        model="deepseek-chat",
        input_tokens=1000,
        output_tokens=2000,
    )

    summary = tracker.get_run_summary("run-001")

    assert summary["workflow_run_id"] == "run-001"
    assert summary["llm_calls"] == 1
    assert summary["total_input_tokens"] == 1000
    assert summary["total_output_tokens"] == 2000
    assert summary["total_cost"] > 0


def test_unknown_model_has_zero_cost():
    tracker = CostTracker()

    cost = tracker.calculate_cost(
        model="unknown-model",
        input_tokens=1000,
        output_tokens=1000,
    )

    assert cost == 0.0