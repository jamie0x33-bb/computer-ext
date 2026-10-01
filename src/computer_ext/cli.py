from __future__ import annotations

import argparse
import json
import sys

from . import __version__, connectors, env
from .search import Search
from .browser import render_page


def _search(args) -> int:
    s = Search(cache=not args.no_cache)
    results = s.query(args.query, max_results=args.max)
    if args.json:
        print(json.dumps([r.__dict__ for r in results], indent=2))
    else:
        for r in results:
            print(f"{r.rank:>2}. {r.title}")
            print(f"    {r.url}")
            if r.snippet:
                print(f"    {r.snippet[:120]}")
            print()
    return 0


def _render(args) -> int:
    page = render_page(args.url, timeout=args.timeout)
    if args.screenshot:
        if not page.rendered:
            print("playwright not available — cannot screenshot", file=sys.stderr)
            return 1
        print(f"screenshot saved (playwright rendered {page.url})")
    else:
        print(page.text[:2000] if not args.full else page.text)
    return 0


def _connectors(args) -> int:
    if args.describe:
        print(json.dumps(connectors.describe(args.describe), indent=2))
        return 0
    items = connectors.connected() if args.connected else connectors.list_connectors()
    if args.json:
        print(json.dumps(items, indent=2))
    else:
        for c in items:
            print(f"{c.get('status','?'):<13} {c.get('source_id',''):<26} {len(c.get('tools', []))} tools")
    return 0


def _env(args) -> int:
    rep = env.sandbox_report()
    if args.json:
        print(json.dumps(rep, indent=2))
    else:
        print("\n".join(env.summarize(rep)))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="cext", description="Perplexity Computer extensions")
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("search", help="web search")
    s.add_argument("query")
    s.add_argument("--max", type=int, default=10)
    s.add_argument("--no-cache", action="store_true")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=_search)

    r = sub.add_parser("render", help="render a page")
    r.add_argument("url")
    r.add_argument("--screenshot", metavar="FILE")
    r.add_argument("--timeout", type=int, default=30)
    r.add_argument("--full", action="store_true")
    r.set_defaults(func=_render)

    c = sub.add_parser("connectors", help="list/describe connectors")
    c.add_argument("--connected", action="store_true")
    c.add_argument("--describe", metavar="SOURCE_ID")
    c.add_argument("--json", action="store_true")
    c.set_defaults(func=_connectors)

    e = sub.add_parser("env", help="sandbox environment report")
    e.add_argument("--json", action="store_true")
    e.set_defaults(func=_env)

    args = p.parse_args(argv)
    try:
        return args.func(args)
    except connectors.ConnectorError as exc:
        print(f"connector error {exc.status}: {exc.body[:300]}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
