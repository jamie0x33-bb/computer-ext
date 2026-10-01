"""Structured web search with caching and filtering."""

from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

from .config import load

CACHE_DIR = Path(os.environ.get("CEXT_CACHE", "/tmp/.cext_cache"))
CACHE_TTL = 3600


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    rank: int


@dataclass
class SearchResponse:
    query: str
    results: list[SearchResult] = field(default_factory=list)
    cached: bool = False


class Search:
    def __init__(self, cache: bool = True):
        self._cache = cache

    def query(self, q: str, max_results: int = 10) -> list[SearchResult]:
        if self._cache:
            cached = self._cache_get(q)
            if cached is not None:
                return cached

        cfg = load()
        if not cfg.usable:
            return []

        url = f"{cfg.base_url.rstrip('/')}/rest/connector-service/connectors/web_search/tools/search/execute"
        payload = json.dumps({
            "parameters": {"query": q, "max_results": max_results}
        }).encode()

        req = urllib.request.Request(url, data=payload, headers=cfg.headers())
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
        except Exception:
            return []

        results = []
        for i, item in enumerate(data.get("content", {}).get("results", [])):
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("snippet", ""),
                rank=i + 1,
            ))

        if self._cache:
            self._cache_put(q, results)
        return results

    def _cache_key(self, q: str) -> Path:
        import hashlib
        h = hashlib.sha256(q.encode()).hexdigest()[:16]
        return CACHE_DIR / f"{h}.json"

    def _cache_get(self, q: str) -> list[SearchResult] | None:
        path = self._cache_key(q)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text())
            if time.time() - data["ts"] > CACHE_TTL:
                path.unlink(missing_ok=True)
                return None
            return [SearchResult(**r) for r in data["results"]]
        except Exception:
            return None

    def _cache_put(self, q: str, results: list[SearchResult]):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        data = {"ts": time.time(), "results": [r.__dict__ for r in results]}
        self._cache_key(q).write_text(json.dumps(data))
