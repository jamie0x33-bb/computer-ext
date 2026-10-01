"""Page rendering with Playwright fallback to urllib."""

from __future__ import annotations

import urllib.request
from dataclasses import dataclass


@dataclass
class Page:
    url: str
    title: str
    text: str
    html: str
    status: int
    rendered: bool


def _render_playwright(url: str, timeout: int) -> Page:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        resp = page.goto(url, timeout=timeout * 1000, wait_until="networkidle")
        result = Page(
            url=page.url,
            title=page.title(),
            text=page.inner_text("body"),
            html=page.content(),
            status=resp.status if resp else 0,
            rendered=True,
        )
        browser.close()
    return result


def _render_urllib(url: str, timeout: int) -> Page:
    req = urllib.request.Request(url, headers={"User-Agent": "computer-ext/0.2.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    import re
    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1).strip() if title_match else ""
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return Page(url=url, title=title, text=text, html=html, status=200, rendered=False)


def render_page(url: str, timeout: int = 30, prefer_playwright: bool = True) -> Page:
    if prefer_playwright:
        try:
            return _render_playwright(url, timeout)
        except ImportError:
            pass
        except Exception:
            pass
    return _render_urllib(url, timeout)
