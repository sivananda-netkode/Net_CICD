
import os

import pytest
import requests


def test_batfish_api_is_reachable():
    batfish_url = os.getenv("BATFISH_URL")

    if not batfish_url:
        pytest.skip(
            "Batfish connectivity test runs only when "
            "BATFISH_URL is configured."
        )

    response = requests.get(
        f"{batfish_url.rstrip('/')}/v2/version",
        timeout=10,
    )

    response.raise_for_status()
    assert "Batfish" in response.json()

