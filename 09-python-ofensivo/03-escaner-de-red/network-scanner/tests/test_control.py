"""Tests de network_scanner.utils.control.

`def_handler` llama a `os._exit(1)`, que mata el proceso actual sin
excepciones que pytest pueda capturar. Por eso se mockea siempre
`os._exit` antes de invocar el handler.
"""

from unittest.mock import MagicMock, patch

import pytest


class TestDefHandler:
    @patch("network_scanner.utils.control.os._exit")
    def test_calls_os_exit_with_code_1(self, mock_exit: MagicMock) -> None:
        from network_scanner.utils.control import def_handler

        def_handler(2, None)

        mock_exit.assert_called_once_with(1)

    @patch("network_scanner.utils.control.os._exit")
    def test_prints_exit_message(
        self, _mock_exit: MagicMock, capsys: pytest.CaptureFixture[str]
    ) -> None:
        from network_scanner.utils.control import def_handler

        def_handler(2, None)

        out = capsys.readouterr().out
        assert "Saliendo del programa" in out
