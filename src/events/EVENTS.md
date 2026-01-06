# Events Catalog

## workflow.triggered (v1)

Emitted when a workflow execution is triggered via API.

Source:
- api

Envelope:
- event_id: UUID
- event_type: workflow.triggered
- version: 1
- timestamp: UTC
- trace_id: request id

Payload:
- workflow_id: UUID
