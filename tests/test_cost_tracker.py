from services.cost_tracker import CostTracker


def test_budget_within_limit():
    tracker = CostTracker(default_budget=0.05)

    tracker.record(
        workflow_run_id="run-budget-001",
        provider="gemini",
        model="gemini-3.6-flash",
        input_tokens=1000,
        output_tokens=500,
    )

    assert tracker.is_within_budget("run-budget-001") is True


def test_budget_exceeded():
    tracker = CostTracker(default_budget=0.0001)

    tracker.record(
        workflow_run_id="run-budget-002",
        provider="gemini",
        model="gemini-3.6-flash",
        input_tokens=1000,
        output_tokens=500,
    )

    assert tracker.is_within_budget("run-budget-002") is False