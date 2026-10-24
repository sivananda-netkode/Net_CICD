
import requests


def test_batfish_api_is_reachable():
    response = requests.get(
        "http://localhost:9996/v2/version",
        timeout=10,
    )

    assert response.status_code == 200
    assert "Batfish" in response.json()

