"""
Module 3 — Wikipedia Research.
Retrieves background/encyclopedic knowledge. Free, no API key.
"""
import wikipedia
from langchain_core.tools import tool


@tool
def wikipedia_lookup(topic: str) -> str:
    """
    Look up background/encyclopedic knowledge on a topic, e.g.
    'Explain Artificial General Intelligence' or 'History of Microsoft'.
    Best for stable, foundational facts rather than breaking news.
    """
    try:
        summary = wikipedia.summary(topic, sentences=8, auto_suggest=True)
        page = wikipedia.page(topic, auto_suggest=True)
        return f"{summary}\n\nSource: {page.url}"
    except wikipedia.exceptions.DisambiguationError as e:
        options = ", ".join(e.options[:5])
        return f"'{topic}' is ambiguous on Wikipedia. Did you mean: {options}?"
    except wikipedia.exceptions.PageError:
        return f"No Wikipedia page found for '{topic}'."
    except Exception as e:
        return f"Wikipedia lookup failed: {e}"
