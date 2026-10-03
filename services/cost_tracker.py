from dataclasses import dataclass, field
from typing import Dict


# Approximate cost per 1M tokens.
# Keep these configurable so pricing can be updated without
# changing the tracking logic.
MODEL_PRICING = {
    "gemini-3.6-flash": {
        "input_per_1m": 0.0,
        "output_per_1m": 0.0,
    },
    "deepseek-chat": {
        "input_per_1m": 0.28,
        "output_per_1m": 0.42,
    },
}


@dataclass
class CostRecord:
    workflow_run_id: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cost: float


@dataclass
class CostTracker:
    records: list[CostRecord] = field(default_factory=list)

    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        pricing = MODEL_PRICING.get(model)

        if pricing is None:
            return 0.0

        input_cost = (
            input_tokens / 1_000_000
        ) * pricing["input_per_1m"]

        output_cost = (
            output_tokens / 1_000_000
        ) * pricing["output_per_1m"]

        return round(input_cost + output_cost, 8)

    def record(
        self,
        workflow_run_id: str,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> CostRecord:
        cost = self.calculate_cost(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

        record = CostRecord(
            workflow_run_id=workflow_run_id,
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
        )

        self.records.append(record)

        return record

    def get_run_cost(self, workflow_run_id: str) -> float:
        return round(
            sum(
                record.cost
                for record in self.records
                if record.workflow_run_id == workflow_run_id
            ),
            8,
        )

    def get_total_cost(self) -> float:
        return round(
            sum(record.cost for record in self.records),
            8,
        )

    def get_run_summary(self, workflow_run_id: str) -> Dict:
        records = [
            record
            for record in self.records
            if record.workflow_run_id == workflow_run_id
        ]

        return {
            "workflow_run_id": workflow_run_id,
            "total_cost": round(
                sum(record.cost for record in records),
                8,
            ),
            "llm_calls": len(records),
            "total_input_tokens": sum(
                record.input_tokens for record in records
            ),
            "total_output_tokens": sum(
                record.output_tokens for record in records
            ),
        }


cost_tracker = CostTracker()