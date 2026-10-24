
import json
import os
import re
from pathlib import Path

import requests

NETBOX_URL = os.environ["NETBOX_URL"].rstrip("/")
NETBOX_TOKEN = os.environ["NETBOX_TOKEN"]

PROJECT_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_DIR / "configs"
OUTPUT_DIR = CONFIG_DIR / "devices"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

session = requests.Session()
session.headers.update({
    "Authorization": f"Token {NETBOX_TOKEN}",
    "Accept": "application/json",
})


def get_all(endpoint):
    url = f"{NETBOX_URL}/api/{endpoint}/"
    results = []

    while url:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        page = response.json()
        results.extend(page["results"])
        url = page["next"]

    return results


def safe_name(name):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", name)


def fetch_configs():
    devices = get_all("dcim/devices")
    contexts = get_all("extras/config-contexts")

    inventory = []

    for device in devices:
        inventory.append({
            "id": device["id"],
            "name": device["name"],
            "device_type": device["device_type"]["display"],
            "site": device["site"]["name"] if device["site"] else None,
        })

    inventory_path = CONFIG_DIR / "inventory.json"
    inventory_path.write_text(
        json.dumps(inventory, indent=2),
        encoding="utf-8",
    )

    saved = 0

    for context in contexts:
        data = context.get("data") or {}
        cli_config = data.get("cli_config")

        if not isinstance(cli_config, str) or not cli_config.strip():
            continue

        filename = safe_name(context["name"]) + ".cfg"
        path = OUTPUT_DIR / filename
        path.write_text(cli_config.rstrip() + "\n", encoding="utf-8")

        print(f"Saved configuration: {path.relative_to(PROJECT_DIR)}")
        saved += 1

    print(f"Retrieved {len(devices)} devices.")
    print(f"Saved {saved} configuration context(s).")
    print(f"Inventory: {inventory_path.relative_to(PROJECT_DIR)}")


if __name__ == "__main__":
    fetch_configs()
