from computer_ext.env import sandbox_report, summarize
from computer_ext.config import fingerprint


def test_fingerprint_consistency():
    assert fingerprint("secret123") == fingerprint("secret123")


def test_fingerprint_none():
    assert fingerprint(None) is None
    assert fingerprint("") is None


def test_fingerprint_no_raw_value():
    fp = fingerprint("my-secret-token")
    assert "my-secret-token" not in fp
    assert len(fp) == 12


def test_report_structure():
    rep = sandbox_report()
    assert "version" in rep
    assert "connector" in rep
    assert "pairs" in rep
    assert "secret_fingerprints" in rep


def test_report_never_contains_raw_secrets(monkeypatch):
    monkeypatch.setenv("PPLX_AGENT_PROXY_TOKEN", "agp_super-secret-value")
    rep = sandbox_report()
    serialized = str(rep)
    assert "agp_super-secret-value" not in serialized


def test_summarize():
    rep = sandbox_report()
    lines = summarize(rep)
    assert any("computer-ext" in l for l in lines)
