import pytest
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.testing import WorkflowEnvironment

from src.temporal_workflow import (
    PrintPulseWorkflow,
    JobInput,
    JobReceipt,
    parse_stl_activity,
    predict_scrap_risk_activity,
    generate_quote_activity,
    reserve_spool_inventory_activity,
    release_spool_reservation_activity
)

ALL_ACTIVITIES = [
    parse_stl_activity,
    predict_scrap_risk_activity,
    generate_quote_activity,
    reserve_spool_inventory_activity,
    release_spool_reservation_activity
]

@pytest.mark.asyncio
async def test_temporal_nominal_pipeline():
    async with await WorkflowEnvironment.start_time_skipping() as env:
        client: Client = env.client
        task_queue = "test-printpulse-nominal-queue"

        async with Worker(
            client,
            task_queue=task_queue,
            workflows=[PrintPulseWorkflow],
            activities=ALL_ACTIVITIES
        ):
            receipt: JobReceipt = await client.execute_workflow(
                PrintPulseWorkflow.run,
                JobInput(filepath="/root/printpulse/models/calibration_cube.stl", material="PLA"),
                id="test-job-cube-nominal",
                task_queue=task_queue
            )

            assert receipt.status == "READY_FOR_PRINT"
            assert receipt.risk_tier in ["LOW", "MODERATE"]
            assert receipt.final_quote_usd > 0.0
            assert receipt.durable_execution_verified is True
            assert receipt.saga_compensation_applied is False

@pytest.mark.asyncio
async def test_temporal_saga_compensation_on_critical_risk():
    async with await WorkflowEnvironment.start_time_skipping() as env:
        client: Client = env.client
        task_queue = "test-printpulse-saga-queue"

        async with Worker(
            client,
            task_queue=task_queue,
            workflows=[PrintPulseWorkflow],
            activities=ALL_ACTIVITIES
        ):
            # Tall tower in ABS triggers >90% scrap risk -> must execute Saga compensating activity
            receipt: JobReceipt = await client.execute_workflow(
                PrintPulseWorkflow.run,
                JobInput(filepath="/root/printpulse/models/tall_tower.stl", material="ABS"),
                id="test-job-tower-critical",
                task_queue=task_queue
            )

            assert receipt.status == "REVIEW_REQUIRED_HIGH_SCRAP"
            assert receipt.risk_tier == "CRITICAL"
            assert receipt.durable_execution_verified is True
            assert receipt.saga_compensation_applied is True
            assert receipt.spool_reservation_id.startswith("SPOOL-RES-")
