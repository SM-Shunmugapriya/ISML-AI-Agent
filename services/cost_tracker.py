from dataclasses import dataclass, field
from typing import Dict


@dataclass
class CostRecord:
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cost: float


@dataclass
class WorkflowCost:
    run_id: str
    records: list[CostRecord] = field(default_factory=list)

    @property
    def total_cost(self) -> float:
        return round(
            sum(record.cost for record in self.records),
            8,
        )


class CostTracker:
    """
    Tracks estimated LLM cost for each workflow run.
    """

    # Approximate cost per 1M tokens.
    # These values can be updated when provider pricing changes.
    PRICING: Dict[str, Dict[str, Dict[str, float]]] = {
        "gemini": {
            "gemini-3.6-flash": {
                "input": 0.10,
                "output": 0.40,
            }
        },
        "deepseek": {
            "deepseek-chat": {
                "input": 0.27,
                "output": 1.10,
            }
        },
    }

    def __init__(self, default_budget: float = 0.05) -> None:
        self.runs: Dict[str, WorkflowCost] = {}
        self.default_budget = default_budget

    def start_run(self, run_id: str) -> WorkflowCost:
        workflow = WorkflowCost(run_id=run_id)
        self.runs[run_id] = workflow
        return workflow

    def track(
        self,
        run_id: str,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> CostRecord:
        if run_id not in self.runs:
            self.start_run(run_id)

        pricing = self.PRICING.get(provider, {}).get(model)

        if pricing is None:
            raise ValueError(
                f"No pricing configured for {provider}/{model}"
            )

        input_cost = (
            input_tokens / 1_000_000
        ) * pricing["input"]

        output_cost = (
            output_tokens / 1_000_000
        ) * pricing["output"]

        total_cost = input_cost + output_cost

        record = CostRecord(
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=round(total_cost, 8),
        )

        self.runs[run_id].records.append(record)

        return record

    def record(
        self,
        workflow_run_id: str,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> CostRecord:
        return self.track(
            run_id=workflow_run_id,
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

    def get_run_cost(self, run_id: str) -> float:
        workflow = self.runs.get(run_id)

        if workflow is None:
            return 0.0

        return workflow.total_cost

    def get_summary(self, run_id: str) -> dict:
        workflow = self.runs.get(run_id)

        if workflow is None:
            return {
                "run_id": run_id,
                "total_cost": 0.0,
                "calls": 0,
            }

        return {
            "run_id": run_id,
            "total_cost": workflow.total_cost,
            "calls": len(workflow.records),
        }

    def is_within_budget(
        self,
        run_id: str,
        budget: float | None = None,
    ) -> bool:
        limit = (
            self.default_budget
            if budget is None
            else budget
        )

        return self.get_run_cost(run_id) <= limit


cost_tracker = CostTracker()