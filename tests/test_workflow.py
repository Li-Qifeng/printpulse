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
    reserve_spool_inventory_activity
)

@pytest.mark.asyncio
async def test_temporal_pipeline_execution():
    async with await WorkflowEnvironment.start_time_skipping() as env:
        client: Client = env.client
        task_queue = "test-printpulse-queue"

        async with Worker(
            client,
            task_queue=task_queue,
            workflows=[PrintPulseWorkflow],
            activities=[
                parse_stl_activity,
                predict_scrap_risk_activity,
                generate_quote_activity,
                reserve_spool_inventory_activity
            ]
        ):
            receipt: JobReceipt = await client.execute_workflow(
                PrintPulseWorkflow.run,
                JobInput(filepath="/root/printpulse/models/calibration_cube.stl", material="PETG"),
                id="test-job-cube-01",
                task_queue=task_queue
            )

            assert receipt.status == "READY_FOR_PRINT"
            assert receipt.risk_tier == "LOW"
            assert receipt.final_quote_usd > 0.0
            assert receipt.durable_execution_verified is True
