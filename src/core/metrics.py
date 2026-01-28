from prometheus_client import Counter, Histogram


WORKER_ATTEMPTS_TOTAL = Counter(
    "worker_attempts_total",
    "Number of worker execution attempts",
    ["workflow_id"],
)

WORKER_SUCCESS_TOTAL = Counter(
    "worker_success_total",
    "Number of successful worker executions",
    ["workflow_id"],
)

WORKER_FAILURE_TOTAL = Counter(
    "worker_failure_total",
    "Number of failed worker executions",
    ["workflow_id"],
)

WORKER_DLQ_TOTAL = Counter(
    "worker_dlq_total",
    "Number of executions routed to DLQ",
    ["workflow_id"],
)

WORKER_DURATION_SECONDS = Histogram(
    "worker_action_duration_seconds",
    "Execution duration per action",
    ["workflow_id"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10),
)


def _label(workflow_id) -> dict:
    return {"workflow_id": str(workflow_id)}


def record_attempt(workflow_id) -> None:
    WORKER_ATTEMPTS_TOTAL.labels(**_label(workflow_id)).inc()


def record_success(workflow_id) -> None:
    WORKER_SUCCESS_TOTAL.labels(**_label(workflow_id)).inc()


def record_failure(workflow_id) -> None:
    WORKER_FAILURE_TOTAL.labels(**_label(workflow_id)).inc()


def record_dlq(workflow_id) -> None:
    WORKER_DLQ_TOTAL.labels(**_label(workflow_id)).inc()


def record_duration(workflow_id, duration_seconds: float) -> None:
    WORKER_DURATION_SECONDS.labels(**_label(workflow_id)).observe(duration_seconds)
