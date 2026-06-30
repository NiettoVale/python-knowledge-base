#!/usr/bin/env python3

from unittest.mock import patch, call

from mac_changer.core import change_mac_address


VALID_INTERFACE = "eth0"
VALID_MAC = "aa:bb:cc:dd:ee:ff"


class TestChangeMacAddress:
    def test_aborts_when_not_root(self, capsys):
        with patch("mac_changer.core.mac_changer.is_root", return_value=False):
            change_mac_address(VALID_INTERFACE, VALID_MAC)

        captured = capsys.readouterr()
        assert "root" in captured.out.lower()

    def test_error_on_invalid_interface(self, capsys):
        with patch("mac_changer.core.mac_changer.is_root", return_value=True):
            change_mac_address("wifi0", VALID_MAC)

        captured = capsys.readouterr()
        assert "interfaz" in captured.out.lower()

    def test_error_on_invalid_mac(self, capsys):
        with patch("mac_changer.core.mac_changer.is_root", return_value=True):
            change_mac_address(VALID_INTERFACE, "zz:zz:zz:zz:zz:zz")

        captured = capsys.readouterr()
        assert "mac" in captured.out.lower()

    def test_error_on_both_invalid(self, capsys):
        with patch("mac_changer.core.mac_changer.is_root", return_value=True):
            change_mac_address("wifi0", "zz:zz:zz:zz:zz:zz")

        captured = capsys.readouterr()
        assert "interfaz" in captured.out.lower()
        assert "mac" in captured.out.lower()

    def test_runs_ifconfig_commands_when_valid(self):
        with (
            patch("mac_changer.core.mac_changer.is_root", return_value=True),
            patch("mac_changer.core.mac_changer.subprocess.run") as mock_run,
        ):
            change_mac_address(VALID_INTERFACE, VALID_MAC)

        assert mock_run.call_count == 3
        mock_run.assert_has_calls([
            call(["ifconfig", VALID_INTERFACE, "down"]),
            call(["ifconfig", VALID_INTERFACE, "hw", "ether", VALID_MAC]),
            call(["ifconfig", VALID_INTERFACE, "up"]),
        ])

    def test_does_not_run_ifconfig_when_not_root(self):
        with (
            patch("mac_changer.core.mac_changer.is_root", return_value=False),
            patch("mac_changer.core.mac_changer.subprocess.run") as mock_run,
        ):
            change_mac_address(VALID_INTERFACE, VALID_MAC)

        mock_run.assert_not_called()

    def test_does_not_run_ifconfig_on_invalid_args(self):
        with (
            patch("mac_changer.core.mac_changer.is_root", return_value=True),
            patch("mac_changer.core.mac_changer.subprocess.run") as mock_run,
        ):
            change_mac_address("wifi0", "bad-mac")

        mock_run.assert_not_called()
