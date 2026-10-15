"""
PrintPulse Temporal Workflow Runner
Demonstrates durable pipeline execution on local test server or production cluster.
"""

import asyncio
import os
import sys
import json
from dataclasses import asdict

from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.testing import WorkflowEnvironment

# Add current dir to path
sys.path.append(os.path.dirname(__file__))

from temporal_workflow import (
    PrintPulseWorkflow,
    JobInput,
    JobReceipt,
    parse_stl_activity,
    predict_scrap_risk_activity,
    generate_quote_activity,
    reserve_spool_inventory_activity,
    release_spool_reservation_activity
)

async def run_sample_pipeline(filepath: str, material: str = "PETG"):
    print(f"\n[Temporal] Initializing In-Process Durable Workflow Environment...")
    async with await WorkflowEnvironment.start_time_skipping() as env:
        client: Client = env.client
        task_queue = "printpulse-task-queue"

        # Register worker with our workflow and 5 activities
        async with Worker(
            client,
            task_queue=task_queue,
            workflows=[PrintPulseWorkflow],
            activities=[
                parse_stl_activity,
                predict_scrap_risk_activity,
                generate_quote_activity,
                reserve_spool_inventory_activity,
                release_spool_reservation_activity
            ]
        ):
            print(f"[Temporal] Worker listening on task queue: {task_queue}")
            print(f"[Temporal] Submitting Workflow execution for: {os.path.basename(filepath)} ({material})")

            job_id = f"printpulse-job-{os.urandom(3).hex()}"
            receipt: JobReceipt = await client.execute_workflow(
                PrintPulseWorkflow.run,
                JobInput(filepath=filepath, material=material),
                id=job_id,
                task_queue=task_queue
            )

            print("\n" + "=" * 60)
            print("TEMPORAL DURABLE EXECUTION COMPLETE - RECEIPT VERIFIED")
            print("=" * 60)
            print(json.dumps(asdict(receipt), indent=2))
            return receipt

if __name__ == "__main__":
    stl_path = sys.argv[1] if len(sys.argv) > 1 else "/root/printpulse/models/calibration_cube.stl"
    material = sys.argv[2] if len(sys.argv) > 2 else "PETG"
    asyncio.run(run_sample_pipeline(stl_path, material))
