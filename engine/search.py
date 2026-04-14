import hashlib
import json
from pathlib import Path

from ddgs import DDGS

_CACHE_DIR = Path(__file__).parent.parent / "cache"


def search_web(query: str, max_results: int = 4) -> list[dict]:
    """Search DuckDuckGo, with a file-based cache keyed on the query string."""
    _CACHE_DIR.mkdir(exist_ok=True)
    cache_file = _CACHE_DIR / (hashlib.sha1(query.encode()).hexdigest() + ".json")

    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))

    with DDGS() as ddgs:
        raw = list(ddgs.text(query, max_results=max_results))
    results = [{"title": r["title"], "url": r["href"], "snippet": r["body"]} for r in raw]
    cache_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    return results
