from computer_ext.browser import Page


def test_page_fields():
    p = Page(url="https://example.com", title="Test", text="hello", html="<p>hello</p>", status=200, rendered=False)
    assert p.url == "https://example.com"
    assert p.rendered is False
