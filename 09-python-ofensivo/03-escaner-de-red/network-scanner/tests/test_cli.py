"""Tests end-to-end del comando CLI usando el runner de Typer.

Se mockean `ping_sweep`, `unpack_ip_range` y `unpack_ip_subnet` tal como
quedaron importados dentro de `network_scanner.interface.cli`, para
verificar que el CLI arma y despacha el escaneo correctamente sin hacer
pings reales.
"""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from network_scanner.interface.cli import app

runner = CliRunner()


class TestCliMain:
    @patch("network_scanner.interface.cli.ping_sweep")
    def test_single_ip_target(self, mock_ping_sweep: MagicMock) -> None:
        result = runner.invoke(app, ["--target", "192.168.0.1"])

        assert result.exit_code == 0
        mock_ping_sweep.assert_called_once_with(["192.168.0.1"])

    @patch("network_scanner.interface.cli.unpack_ip_range", return_value=["192.168.0.1", "192.168.0.2"])
    @patch("network_scanner.interface.cli.ping_sweep")
    def test_range_target_is_unpacked_before_sweeping(
        self, mock_ping_sweep: MagicMock, mock_unpack_range: MagicMock
    ) -> None:
        result = runner.invoke(app, ["--target", "192.168.0.1-2"])

        assert result.exit_code == 0
        mock_unpack_range.assert_called_once_with("192.168.0.1-2")
        mock_ping_sweep.assert_called_once_with(["192.168.0.1", "192.168.0.2"])

    @patch("network_scanner.interface.cli.unpack_ip_subnet", return_value=["192.168.0.1", "192.168.0.2"])
    @patch("network_scanner.interface.cli.ping_sweep")
    def test_subnet_target_is_unpacked_before_sweeping(
        self, mock_ping_sweep: MagicMock, mock_unpack_subnet: MagicMock
    ) -> None:
        result = runner.invoke(app, ["--target", "192.168.0.0/30"])

        assert result.exit_code == 0
        mock_unpack_subnet.assert_called_once_with("192.168.0.0/30")
        mock_ping_sweep.assert_called_once_with(["192.168.0.1", "192.168.0.2"])

    @patch("network_scanner.interface.cli.ping_sweep")
    def test_invalid_target_does_not_trigger_sweep(self, mock_ping_sweep: MagicMock) -> None:
        result = runner.invoke(app, ["--target", "999.999.999.999"])

        assert result.exit_code == 0
        mock_ping_sweep.assert_not_called()
        assert "No se pudo determinar" in result.stdout

    def test_missing_target_option_fails(self) -> None:
        result = runner.invoke(app, [])

        assert result.exit_code != 0

    @patch("network_scanner.interface.cli.ping_sweep")
    def test_help_shows_usage(self, _mock_ping_sweep: MagicMock) -> None:
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "--target" in result.stdout
