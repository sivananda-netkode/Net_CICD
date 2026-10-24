from pathlib import Path
import re

PROJECT_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_DIR / "configs" / "devices"


def read_config(filename):
    path = CONFIG_DIR / filename
    assert path.is_file(), f"Configuration file missing: {path}"
    return path.read_text(encoding="utf-8")


def test_r1_dhcp_configuration_exists():
    config = read_config("R1-DHCP-CLI.cfg")
    assert config.strip()


def test_r1_dhcp_pools_exist():
    config = read_config("R1-DHCP-CLI.cfg")

    for pool in ("VLAN10", "VLAN20", "VLAN30", "VLAN40"):
        assert re.search(
            rf"(?im)^\s*ip dhcp pool {pool}\s*$",
            config,
        ), f"Missing DHCP pool: {pool}"


def test_dhcp_pools_have_network_and_gateway():
    config = read_config("R1-DHCP-CLI.cfg")

    for vlan, subnet in (
        (10, "192.168.10.0"),
        (20, "192.168.20.0"),
        (30, "192.168.30.0"),
        (40, "192.168.40.0"),
    ):
        pattern = (
            rf"(?ims)^\s*ip dhcp pool VLAN{vlan}\s*$"
            rf"(.*?)(?=^\s*ip dhcp pool |\Z)"
        )
        match = re.search(pattern, config)
        assert match, f"Missing DHCP pool VLAN{vlan}"

        block = match.group(1)
        assert subnet in block, f"Wrong or missing subnet in VLAN{vlan}"
        assert f"192.168.{vlan}.1" in block, (
            f"Wrong or missing gateway in VLAN{vlan}"
        )


def test_switch_acl_configuration_exists():
    config = read_config("SWITCH1-ACL-CLI.cfg")
    assert config.strip()


def test_switch_acl_has_expected_rules():
    config = read_config("SWITCH1-ACL-CLI.cfg")

    assert "ip access-list extended VLAN10-ACL" in config
    assert (
        "deny ip 192.168.10.0 0.0.0.255 "
        "192.168.40.0 0.0.0.255"
    ) in config
    assert "permit ip any any" in config
