import time
import uuid
from datetime import datetime, timezone

from services.logger import log_info, log_error


class ObservabilityService:
    """
    Tracks structured metrics for a single workflow execution.
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.run_id = str(uuid.uuid4())
        self.start_time = None
        self.end_time = None

        self.input_data = None
        self.provider = None
        self.model = None
        self.prompt_version = None

        self.search_count = 0
        self.discovered_count = 0
        self.valid_count = 0
        self.evaluated_count = 0
        self.ranked_count = 0
        self.stored_count = 0

        self.errors = []
        self.stage_metrics = {}

        self.final_status = "started"

    def start_run(
        self,
        input_data=None,
        provider=None,
        model=None,
        prompt_version=None,
    ):
        self.reset()

        self.start_time = time.perf_counter()
        self.input_data = input_data
        self.provider = provider
        self.model = model
        self.prompt_version = prompt_version

        log_info(
            f"OBSERVABILITY | run_id={self.run_id} | "
            f"status=started | input={input_data}"
        )

        return self.run_id

    def start_stage(self, stage_name):
        self.stage_metrics[stage_name] = {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "start_time": time.perf_counter(),
            "status": "started",
        }

    def end_stage(self, stage_name, status="success", error=None):
        stage = self.stage_metrics.get(stage_name)

        if not stage:
            return

        duration = time.perf_counter() - stage["start_time"]

        stage["duration_seconds"] = round(duration, 4)
        stage["ended_at"] = datetime.now(timezone.utc).isoformat()
        stage["status"] = status

        if error:
            stage["error"] = str(error)
            self.errors.append(
                {
                    "stage": stage_name,
                    "error": str(error),
                }
            )

        log_info(
            f"OBSERVABILITY | run_id={self.run_id} | "
            f"stage={stage_name} | "
            f"status={status} | "
            f"duration={round(duration, 4)}s"
        )

    def record_counts(
        self,
        search_count=None,
        discovered_count=None,
        valid_count=None,
        evaluated_count=None,
        ranked_count=None,
        stored_count=None,
    ):
        if search_count is not None:
            self.search_count = search_count

        if discovered_count is not None:
            self.discovered_count = discovered_count

        if valid_count is not None:
            self.valid_count = valid_count

        if evaluated_count is not None:
            self.evaluated_count = evaluated_count

        if ranked_count is not None:
            self.ranked_count = ranked_count

        if stored_count is not None:
            self.stored_count = stored_count

    def record_error(self, stage, error):
        error_data = {
            "stage": stage,
            "error": str(error),
        }

        self.errors.append(error_data)

        log_error(
            f"OBSERVABILITY | run_id={self.run_id} | "
            f"stage={stage} | error={error}"
        )

    def finish_run(self, status="success"):
        self.end_time = time.perf_counter()
        self.final_status = status

        duration = 0

        if self.start_time is not None:
            duration = self.end_time - self.start_time

        summary = {
            "run_id": self.run_id,
            "input": self.input_data,
            "provider": self.provider,
            "model": self.model,
            "prompt_version": self.prompt_version,
            "duration_seconds": round(duration, 4),
            "search_count": self.search_count,
            "discovered_count": self.discovered_count,
            "valid_count": self.valid_count,
            "evaluated_count": self.evaluated_count,
            "ranked_count": self.ranked_count,
            "stored_count": self.stored_count,
            "errors": self.errors,
            "stages": self.stage_metrics,
            "final_status": self.final_status,
        }

        log_info(
            f"OBSERVABILITY | run_id={self.run_id} | "
            f"status={status} | "
            f"duration={round(duration, 4)}s | "
            f"discovered={self.discovered_count} | "
            f"valid={self.valid_count} | "
            f"evaluated={self.evaluated_count} | "
            f"ranked={self.ranked_count} | "
            f"stored={self.stored_count} | "
            f"errors={len(self.errors)}"
        )

        return summary