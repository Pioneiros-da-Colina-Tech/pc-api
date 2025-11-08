from datetime import UTC, datetime
from typing import final
from uuid import uuid4

from locust import HttpUser, task


@final
class HttpClient(HttpUser):
    @task
    def create_batch(self):
        create_batch_payload = {
            "external_id": str(uuid4()),
            "assignment_date": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S"),
        }
        _ = self.client.post("/batches", json=create_batch_payload)

    @task
    def test_health(self):
        _ = self.client.get("/health")
