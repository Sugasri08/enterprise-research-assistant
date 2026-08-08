"""
Module 7 — Parallel Agent.
Researches multiple topics/companies independently, then combines
the results. Uses a thread pool rather than LangChain's async runnables
for simplicity, since Streamlit's execution model is synchronous.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from agents.orchestrator import generate_report
from agents.schemas import Report


def parallel_research(topics: list[str], use_documents: bool = True, max_workers: int = 4) -> dict[str, Report]:
    """
    Runs generate_report() for each topic concurrently.
    e.g. parallel_research(["Google", "Microsoft", "Amazon", "OpenAI"])
    Returns {topic: Report}. Failed topics are omitted with a warning printed.
    """
    results: dict[str, Report] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        future_to_topic = {
            pool.submit(generate_report, topic, use_documents): topic
            for topic in topics
        }
        for future in as_completed(future_to_topic):
            topic = future_to_topic[future]
            try:
                results[topic] = future.result()
            except Exception as e:
                print(f"[parallel_research] failed for '{topic}': {e}")
    return results
