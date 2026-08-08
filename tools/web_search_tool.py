"""
Module 2 — Internet Research.
Web search tool. Prefers Tavily (free tier, built for LLM agents and far
more reliable) if TAVILY_API_KEY is set in .env. Falls back to DuckDuckGo
scraping via the `ddgs` package if no Tavily key is set — note DuckDuckGo/
Bing scraping is rate-limited unpredictably and can fail under normal use,
so Tavily's free tier (https://tavily.com, no cost for moderate usage) is
the recommended default; DuckDuckGo is a zero-signup fallback only.
"""
from langchain_core.tools import tool
from config import TAVILY_API_KEY


@tool
def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the live web for current information — news, stock prices,
    recent events, or anything that requires up-to-date data.
    Use this for queries like 'latest NVIDIA news' or 'current Google stock'.
    """
    if TAVILY_API_KEY:
        try:
            return _tavily_search(query, max_results)
        except Exception as e:
            # fall through to DuckDuckGo rather than failing the whole query
            fallback_note = f"(Tavily search failed: {e}; falling back to DuckDuckGo)\n\n"
            try:
                return fallback_note + _duckduckgo_search(query, max_results)
            except Exception as e2:
                return f"Web search unavailable right now (Tavily error: {e}; DuckDuckGo error: {e2})."

    try:
        return _duckduckgo_search(query, max_results)
    except Exception as e:
        return (
            f"Web search failed: {e}. DuckDuckGo's free search is rate-limited and can "
            "fail intermittently — for reliable results, get a free Tavily API key at "
            "https://tavily.com and set TAVILY_API_KEY in your .env file."
        )


def _tavily_search(query: str, max_results: int) -> str:
    from langchain_community.tools.tavily_search import TavilySearchResults
    results = TavilySearchResults(max_results=max_results, api_key=TAVILY_API_KEY).invoke(query)
    return _format_results(results, key_map={"snippet": "content", "url": "url", "title": "title"})


def _duckduckgo_search(query: str, max_results: int) -> str:
    from ddgs import DDGS
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))
    if not results:
        return f"No web results found for '{query}'."
    return _format_results(results, key_map={"snippet": "body", "url": "href", "title": "title"})


def _format_results(results, key_map: dict) -> str:
    lines = []
    for i, r in enumerate(results, 1):
        title = r.get(key_map["title"], "Untitled")
        snippet = r.get(key_map["snippet"], "")
        url = r.get(key_map["url"], "")
        lines.append(f"{i}. {title}\n   {snippet}\n   Source: {url}")
    return "\n\n".join(lines)