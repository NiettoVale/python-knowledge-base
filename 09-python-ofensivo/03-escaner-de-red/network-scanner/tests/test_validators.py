"""Tests de network_scanner.utils.validators."""

import pytest

from network_scanner.utils.validators import (
    detect_target_type,
    is_valid_ip,
    is_valid_ip_range,
    is_valid_subnet,
    validate_target,
)


class TestIsValidIp:
    @pytest.mark.parametrize(
        "ip",
        [
            "192.168.0.1",
            "0.0.0.0",
            "255.255.255.255",
            "::1",  # IPv6 tambien es una IP valida
        ],
    )
    def test_valid_ips(self, ip: str) -> None:
        assert is_valid_ip(ip) is True

    @pytest.mark.parametrize(
        "ip",
        [
            "999.999.999.999",
            "192.168.0",
            "no-es-una-ip",
            "",
        ],
    )
    def test_invalid_ips(self, ip: str) -> None:
        assert is_valid_ip(ip) is False


class TestIsValidIpRange:
    @pytest.mark.parametrize(
        "ip_range",
        [
            "192.168.0.1-100",
            "10.0.0.1-2",
            "10.0.0.1-255",
        ],
    )
    def test_valid_ranges(self, ip_range: str) -> None:
        assert is_valid_ip_range(ip_range) is True

    def test_invalid_base_ip(self) -> None:
        assert is_valid_ip_range("999.168.0.1-100") is False

    def test_start_greater_than_end(self) -> None:
        assert is_valid_ip_range("192.168.0.100-50") is False

    def test_start_equal_to_end(self) -> None:
        # La validacion exige start < end (rango de al menos 2 hosts).
        assert is_valid_ip_range("192.168.0.50-50") is False

    def test_end_host_out_of_bounds(self) -> None:
        assert is_valid_ip_range("192.168.0.1-300") is False

    def test_end_host_not_a_number(self) -> None:
        assert is_valid_ip_range("192.168.0.1-abc") is False

    def test_missing_dash(self) -> None:
        assert is_valid_ip_range("192.168.0.1") is False

    def test_too_many_dashes(self) -> None:
        assert is_valid_ip_range("192.168.0.1-50-60") is False


class TestIsValidSubnet:
    @pytest.mark.parametrize(
        "subnet",
        [
            "192.168.0.0/24",
            "10.0.0.0/8",
            "192.168.0.5/32",
        ],
    )
    def test_valid_subnets(self, subnet: str) -> None:
        assert is_valid_subnet(subnet) is True

    @pytest.mark.parametrize(
        "subnet",
        [
            "192.168.0.0/33",  # prefijo fuera de rango para IPv4
            "no-es-una-subred",
            "192.168.0.0/24/24",
        ],
    )
    def test_invalid_subnets(self, subnet: str) -> None:
        assert is_valid_subnet(subnet) is False


class TestDetectTargetType:
    def test_detects_subnet(self) -> None:
        assert detect_target_type("192.168.0.0/24") == "subnet"

    def test_detects_range(self) -> None:
        assert detect_target_type("192.168.0.1-100") == "range"

    def test_detects_ip(self) -> None:
        assert detect_target_type("192.168.0.1") == "ip"


class TestValidateTarget:
    def test_valid_ip(self) -> None:
        assert validate_target("192.168.0.1") == (True, "ip")

    def test_valid_range(self) -> None:
        assert validate_target("192.168.0.1-100") == (True, "range")

    def test_valid_subnet(self) -> None:
        assert validate_target("192.168.0.0/24") == (True, "subnet")

    def test_invalid_ip(self) -> None:
        assert validate_target("999.999.999.999") == (False, "ip")

    def test_invalid_range(self) -> None:
        assert validate_target("192.168.0.100-50") == (False, "range")

    def test_invalid_subnet(self) -> None:
        assert validate_target("10.0.0.0/99") == (False, "subnet")
