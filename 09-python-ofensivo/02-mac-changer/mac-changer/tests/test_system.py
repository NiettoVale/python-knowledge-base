#!/usr/bin/env python3

from unittest.mock import patch

from mac_changer.utils import is_root


class TestIsRoot:
    def test_returns_true_when_root(self):
        with patch("os.geteuid", return_value=0):
            assert is_root() is True

    def test_returns_false_when_not_root(self):
        with patch("os.geteuid", return_value=1000):
            assert is_root() is False
