import json
from unittest.mock import patch, MagicMock

from computer_ext.preflight import submit
from computer_ext.env import sandbox_report


def test_report_never_contains_raw_secrets(monkeypatch):
    monkeypatch.setenv("PPLX_AGENT_PROXY_TOKEN", "agp_test-secret-never-in-report")
    monkeypatch.setenv("PPLX_CONNECTOR_API_KEY", "ckey_also-secret")
    rep = sandbox_report()
    serialized = json.dumps(rep)
    assert "agp_test-secret-never-in-report" not in serialized
    assert "ckey_also-secret" not in serialized


def test_submit_with_bearer(monkeypatch):
    monkeypatch.setenv("PPLX_AGENT_PROXY_TOKEN", "agp_test-bearer")
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"accepted": True, "report_id": "pf-test"}).encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
        result = submit("https://example.com/api/preflight")

    assert result["accepted"] is True
    call_req = mock_open.call_args[0][0]
    assert call_req.get_header("Authorization") == "Bearer agp_test-bearer"


def test_submit_without_bearer(monkeypatch):
    monkeypatch.delenv("PPLX_AGENT_PROXY_TOKEN", raising=False)
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"accepted": True}).encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
        result = submit("https://example.com/api/preflight")

    call_req = mock_open.call_args[0][0]
    assert not call_req.has_header("Authorization")
