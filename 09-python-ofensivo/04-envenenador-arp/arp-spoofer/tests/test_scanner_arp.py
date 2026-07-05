from unittest.mock import MagicMock, patch

from scapy.layers.l2 import ARP

from arp_spoofer.core.scanner_arp import scan


def _fake_answered(pairs: list[tuple[str, str]]) -> list[tuple[MagicMock, MagicMock]]:
    answered = []
    for ip, mac in pairs:
        sent = MagicMock()
        received = MagicMock(psrc=ip, hwsrc=mac)
        answered.append((sent, received))
    return answered


@patch("arp_spoofer.core.scanner_arp.srp")
def test_scan_returns_devices_from_answered_packets(mock_srp: MagicMock) -> None:
    mock_srp.return_value = (
        _fake_answered([("192.168.1.1", "aa:bb:cc:dd:ee:ff")]),
        [],
    )

    devices = scan("192.168.1.0/24")

    assert devices == [{"ip": "192.168.1.1", "mac": "aa:bb:cc:dd:ee:ff"}]


@patch("arp_spoofer.core.scanner_arp.srp")
def test_scan_returns_multiple_devices(mock_srp: MagicMock) -> None:
    mock_srp.return_value = (
        _fake_answered(
            [
                ("192.168.1.1", "aa:bb:cc:dd:ee:ff"),
                ("192.168.1.2", "11:22:33:44:55:66"),
            ]
        ),
        [],
    )

    devices = scan("192.168.1.0/24")

    assert devices == [
        {"ip": "192.168.1.1", "mac": "aa:bb:cc:dd:ee:ff"},
        {"ip": "192.168.1.2", "mac": "11:22:33:44:55:66"},
    ]


@patch("arp_spoofer.core.scanner_arp.srp")
def test_scan_returns_empty_list_when_no_devices_respond(
    mock_srp: MagicMock,
) -> None:
    mock_srp.return_value = ([], [])

    devices = scan("192.168.1.0/24")

    assert devices == []


@patch("arp_spoofer.core.scanner_arp.srp")
def test_scan_sends_arp_request_to_target_ip(mock_srp: MagicMock) -> None:
    mock_srp.return_value = ([], [])

    scan("192.168.1.5")

    assert mock_srp.call_count == 1
    sent_packet = mock_srp.call_args[0][0]
    assert sent_packet[ARP].pdst == "192.168.1.5"
