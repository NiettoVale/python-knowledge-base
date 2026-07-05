from unittest.mock import patch

from typer.testing import CliRunner

from arp_spoofer.interface.cli import app

runner = CliRunner()


@patch("arp_spoofer.interface.cli.scan")
def test_main_prints_table_when_devices_found(mock_scan) -> None:
    mock_scan.return_value = [{"ip": "192.168.1.1", "mac": "aa:bb:cc:dd:ee:ff"}]

    result = runner.invoke(app, ["-t", "192.168.1.0/24"])

    assert result.exit_code == 0
    assert "192.168.1.1" in result.stdout
    assert "aa:bb:cc:dd:ee:ff" in result.stdout
    mock_scan.assert_called_once_with("192.168.1.0/24")


@patch("arp_spoofer.interface.cli.scan")
def test_main_prints_warning_when_no_devices_found(mock_scan) -> None:
    mock_scan.return_value = []

    result = runner.invoke(app, ["-t", "192.168.1.0/24"])

    assert result.exit_code == 0
    assert "No se encontraron dispositivos" in result.stdout


def test_main_requires_target_option() -> None:
    result = runner.invoke(app, [])

    assert result.exit_code != 0
