from computer_ext.search import Search, SearchResult


def test_search_result_fields():
    r = SearchResult(title="Test", url="https://example.com", snippet="A test", rank=1)
    assert r.title == "Test"
    assert r.rank == 1


def test_search_no_config(monkeypatch):
    monkeypatch.delenv("PPLX_CONNECTOR_BASE_URL", raising=False)
    monkeypatch.delenv("PPLX_AGENT_PROXY_TOKEN", raising=False)
    s = Search(cache=False)
    assert s.query("test") == []
