# computer-ext

Extensions for Perplexity Computer. Better search, page rendering, connector
debugging.

Computer exposes connectors and a web search surface but gives skill authors
almost nothing to debug with. This fills the gap: structured search with
filtering, Playwright rendering for JavaScript-heavy pages, and connector
diagnostics that tell you whether the environment is wired up before you
waste a turn on a call that was always going to fail.

## Install

```bash
pip install -e .
pip install -e ".[browser]"   # adds playwright page rendering
```

## Commands

```bash
cext search "site:github.com perplexity computer"   # structured search
cext render https://example.com --screenshot out.png # playwright render
cext connectors                                      # list connected services
cext connectors describe gcal                        # tool schemas
cext env                                             # sandbox environment summary
```

## Search

`cext search` wraps the connector search surface with structured output,
result-type filtering, and a local cache that avoids burning rate-limited
calls on repeated queries.

```python
from computer_ext.search import Search

s = Search()
results = s.query("perplexity computer playwright", max_results=5)
for r in results:
    print(f"{r.rank}. {r.title} — {r.url}")
```

## Page rendering

Uses Playwright when available. Falls back to raw urllib for pages that
do not require JavaScript.

```python
from computer_ext.browser import render_page

page = render_page("https://example.com")
print(page.title, len(page.text))
```

## Connector debugging

Same principle as `doctor` in skill-kit: report which environment pairs
are complete, never print credential values.

```python
from computer_ext.env import sandbox_report
print(sandbox_report())
```

## Docs

<https://computer-ext-site.vercel.app>

## Contributing

Environment-specific bugs need a preflight report attached. See
[CONTRIBUTING.md](CONTRIBUTING.md).
