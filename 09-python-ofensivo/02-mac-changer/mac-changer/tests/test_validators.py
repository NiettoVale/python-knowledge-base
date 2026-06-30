#!/usr/bin/env python3

import pytest

from mac_changer.utils import is_valid_mac, is_valid_interface


class TestIsValidMac:
    def test_valid_lowercase(self):
        assert is_valid_mac("aa:bb:cc:dd:ee:ff") is True

    def test_valid_uppercase(self):
        assert is_valid_mac("AA:BB:CC:DD:EE:FF") is True

    def test_valid_mixed_case(self):
        assert is_valid_mac("aA:Bb:1C:d2:E3:f4") is True

    def test_invalid_missing_octet(self):
        assert is_valid_mac("aa:bb:cc:dd:ee") is False

    def test_invalid_separator(self):
        assert is_valid_mac("aa-bb-cc-dd-ee-ff") is False

    def test_invalid_short_octet(self):
        assert is_valid_mac("aa:bb:cc:dd:ee:f") is False

    def test_invalid_non_hex(self):
        assert is_valid_mac("zz:bb:cc:dd:ee:ff") is False

    def test_invalid_empty(self):
        assert is_valid_mac("") is False


class TestIsValidInterface:
    @pytest.mark.parametrize("iface", [
        "eth0", "eth1",
        "ens3", "ens33",
        "eno1", "eno2",
        "enp2s0", "enp3s0f0",
        "wlan0", "wlan1",
        "wlp2s0", "wlp3s0f0",
        "lo",
    ])
    def test_valid_interfaces(self, iface):
        assert is_valid_interface(iface) is True

    @pytest.mark.parametrize("iface", [
        "eth",
        "wlan",
        "wifi0",
        "en0",
        "docker0",
        "br-abc123",
        "",
        "ETH0",
    ])
    def test_invalid_interfaces(self, iface):
        assert is_valid_interface(iface) is False
