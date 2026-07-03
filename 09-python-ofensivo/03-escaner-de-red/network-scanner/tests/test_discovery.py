"""Tests de network_scanner.core.discovery.

Los tests que ejercitan `host_discovery`/`ping_sweep` mockean
`subprocess.run` (y en algunos casos `host_discovery`) para no depender
de la red real ni de la disponibilidad del binario `ping` del sistema.
"""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from network_scanner.core.discovery import (
    _print_summary,
    host_discovery,
    ping_sweep,
    unpack_ip_range,
    unpack_ip_subnet,
)


class TestHostDiscovery:
    @patch("network_scanner.core.discovery.subprocess.run")
    def test_returns_true_when_host_responds(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=0)

        assert host_discovery("192.168.0.1") is True

    @patch("network_scanner.core.discovery.subprocess.run")
    def test_returns_false_when_host_does_not_respond(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=1)

        assert host_discovery("192.168.0.1") is False

    @patch("network_scanner.core.discovery.subprocess.run")
    def test_returns_false_on_timeout(self, mock_run: MagicMock) -> None:
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="ping", timeout=1)

        assert host_discovery("192.168.0.1") is False

    @patch("network_scanner.core.discovery.subprocess.run")
    def test_calls_ping_with_expected_args(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=0)

        host_discovery("10.0.0.5")

        args, kwargs = mock_run.call_args
        assert args[0] == ["ping", "-c", "1", "10.0.0.5"]
        assert kwargs["timeout"] == 1


class TestPingSweep:
    @patch("network_scanner.core.discovery.host_discovery")
    def test_returns_only_active_hosts_sorted(self, mock_host_discovery: MagicMock) -> None:
        active = {"192.168.0.1", "192.168.0.10", "192.168.0.2"}
        mock_host_discovery.side_effect = lambda target: target in active

        targets = ["192.168.0.10", "192.168.0.1", "192.168.0.2", "192.168.0.3"]
        result = ping_sweep(targets)

        # Ordenado numericamente (no alfabeticamente): .1, .2, .10
        assert result == ["192.168.0.1", "192.168.0.2", "192.168.0.10"]

    @patch("network_scanner.core.discovery.host_discovery", return_value=False)
    def test_returns_empty_list_when_no_host_is_active(self, _mock_host_discovery: MagicMock) -> None:
        result = ping_sweep(["192.168.0.1", "192.168.0.2"])

        assert result == []

    def test_returns_empty_list_for_empty_targets(self) -> None:
        assert ping_sweep([]) == []

    @patch("network_scanner.core.discovery.host_discovery")
    def test_prints_active_host_to_console(
        self, mock_host_discovery: MagicMock, capsys: pytest.CaptureFixture[str]
    ) -> None:
        mock_host_discovery.side_effect = lambda target: target == "192.168.0.1"

        ping_sweep(["192.168.0.1"])

        out = capsys.readouterr().out
        assert "192.168.0.1" in out


class TestPrintSummary:
    def test_prints_no_hosts_message_when_empty(self, capsys: pytest.CaptureFixture[str]) -> None:
        _print_summary([], total_scanned=10)

        out = capsys.readouterr().out
        assert "No se encontraron hosts activos" in out

    def test_prints_table_with_active_hosts(self, capsys: pytest.CaptureFixture[str]) -> None:
        _print_summary(["192.168.0.1", "192.168.0.2"], total_scanned=5)

        out = capsys.readouterr().out
        assert "192.168.0.1" in out
        assert "192.168.0.2" in out
        assert "2/5" in out


class TestUnpackIpRange:
    def test_expands_simple_range(self) -> None:
        assert unpack_ip_range("192.168.0.1-5") == [
            "192.168.0.1",
            "192.168.0.2",
            "192.168.0.3",
            "192.168.0.4",
            "192.168.0.5",
        ]

    def test_expands_range_with_different_base(self) -> None:
        assert unpack_ip_range("10.0.0.10-12") == [
            "10.0.0.10",
            "10.0.0.11",
            "10.0.0.12",
        ]

    def test_single_host_range(self) -> None:
        # start == end no pasaria la validacion, pero unpack no valida por
        # su cuenta: solo expande el rango que recibe.
        assert unpack_ip_range("192.168.0.5-5") == ["192.168.0.5"]


class TestUnpackIpSubnet:
    def test_excludes_network_and_broadcast_addresses(self) -> None:
        # /30 tiene 4 direcciones: .0 (red), .1 y .2 (host), .3 (broadcast)
        assert unpack_ip_subnet("192.168.0.0/30") == ["192.168.0.1", "192.168.0.2"]

    def test_slash_24_returns_254_hosts(self) -> None:
        targets = unpack_ip_subnet("10.0.0.0/24")

        assert len(targets) == 254
        assert targets[0] == "10.0.0.1"
        assert targets[-1] == "10.0.0.254"
