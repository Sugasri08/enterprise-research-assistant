# Enterprise Research Assistant

An AI-powered research analyst for consultants: chat-driven research across
the web, Wikipedia, and uploaded client documents, producing structured,
downloadable reports. Built entirely on a **free-tier stack** — no paid
API keys or hosting required to run this as an MVP.

## Stack (all free)

| Piece | Tool |
|---|---|
| LLM | Google Gemini 2.5 Flash (Google AI Studio free tier) |
| Agent framework | LangChain `create_agent()` |
| Web search | DuckDuckGo (no key) |
| Background knowledge | Wikipedia (no key) |
| Vector store (RAG) | ChromaDB, local |
| Memory | Streamlit session state (short-term) + local JSON (persistent/long-term) |
| UI | Streamlit |
| Hosting (optional) | Streamlit Community Cloud |

## Setup

1. Get a free Gemini API key: https://aistudio.google.com/app/apikey (no credit card).
2. `pip install -r requirements.txt`
3. `cp .env.example .env` and paste your key into `GOOGLE_API_KEY`.
4. `streamlit run app.py`

## Module map

| Module (from project brief) | Where it lives |
|---|---|
| 1. AI Chat Assistant | `agents/orchestrator.py::chat`, `app.py` Chat tab |
| 2. Internet Research | `tools/web_search_tool.py` |
| 3. Wikipedia Research | `tools/wikipedia_tool.py` |
| 4. Document Research (RAG) | `rag/ingest.py`, `rag/retriever.py` |
| 5. Multi-Source Research | agent tool selection in `orchestrator.py` |
| 6. Structured Output | `agents/schemas.py` (`Report` Pydantic model) |
| 7. Parallel Agent | `agents/chains.py::parallel_research` |
| 8. Sequential Chain | `agents/orchestrator.py::generate_report` |
| 9. Memory | `memory/short_term.py`, `memory/persistent_store.py` |
| 10. Python Tool | `tools/python_analysis_tool.py` |
| 11. Gmail Integration | not yet implemented — see below |
| 12. Google Drive (optional) | not yet implemented |

## Not yet built (next steps)

- **Gmail integration**: send the generated report to `manager@company.com`.
  Use the Gmail API free tier; OAuth credentials go in `.env`.
- **Google Drive integration** (optional per the brief).
- Swap the free DuckDuckGo tool for Tavily if you want higher-quality
  search results — just set `TAVILY_API_KEY` in `.env`.

## Known free-tier limits

- Gemini free tier: ~1,500 requests/day — plenty for development and demos.
- DuckDuckGo search has no official rate limit but can throttle under heavy
  automated use; keep request volume reasonable during testing.
