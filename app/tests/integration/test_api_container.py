import os

import pytest
import requests


RUN_INTEGRATION = os.getenv("RUN_INTEGRATION_TESTS", "false").lower() == "true"
BASE_URL = os.getenv("INTEGRATION_BASE_URL", "http://localhost:8000")

pytestmark = pytest.mark.skipif(not RUN_INTEGRATION, reason="Set RUN_INTEGRATION_TESTS=true to run")


def test_healthcheck_in_container():
    response = requests.get(f"{BASE_URL}/health", timeout=10)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
