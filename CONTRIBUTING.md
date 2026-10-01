# Contributing

## Setup

```bash
git clone https://github.com/jamie0x33-bb/computer-ext.git
cd computer-ext
pip install -e ".[dev]"
pytest
```

## Bug reports

If the bug is environment-specific (connector calls failing, missing env vars,
proxy rejections), attach a preflight report. We cannot reproduce another
workspace's wiring without one.

## Code style

- No comments that restate the code.
- Functions that touch credentials must never print or log them.
  Reduce secrets to a fingerprint (SHA-256 prefix). There is a test for this.
- `urllib` only — no `requests` dependency.
