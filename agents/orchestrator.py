"""
Modules 1, 5, 6, 8 — Chat Assistant, Multi-Source Research,
Structured Output, Sequential Chain.
"""
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from config import get_llm
from tools.web_search_tool import web_search
from tools.wikipedia_tool import wikipedia_lookup
from tools.python_analysis_tool import compare_metrics
from rag.retriever import search_uploaded_documents
from agents.schemas import Report

def _to_langchain_messages(messages: list[dict]) -> list:
    lc_messages = []
    for m in messages:
        role = m.get("role")
        content = m.get("content", "")
        if role == "user":
            lc_messages.append(HumanMessage(content=content))
        elif role == "assistant":
            lc_messages.append(AIMessage(content=content))
        elif role == "system":
            lc_messages.append(SystemMessage(content=content))
    return lc_messages

ALL_TOOLS = [web_search, wikipedia_lookup, search_uploaded_documents, compare_metrics]

CHAT_SYSTEM_PROMPT = """You are an enterprise research analyst assistant for a
business consulting firm. Use the available tools to ground your answers in real information.
Cite where information came from (web, Wikipedia, or uploaded document) in your answer.
Be concise and professional, like a consultant briefing a colleague."""

RESEARCH_SYSTEM_PROMPT = """You are a research analyst. Use the available tools to gather real,
up-to-date facts on the topic. Provide a comprehensive summary of all findings."""


def build_chat_agent():
    return create_agent(model=get_llm(), tools=ALL_TOOLS, system_prompt=CHAT_SYSTEM_PROMPT)


def _extract_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "".join(parts) if parts else str(content)
    return str(content)


def chat(user_input: str, chat_history: list[dict] | None = None) -> str:
    """
    Module 1 — conversational entry point, tools called as needed.
    """
    agent = build_chat_agent()
    messages = _to_langchain_messages(chat_history or []) + [HumanMessage(content=user_input)]
    result = agent.invoke({"messages": messages})
    return _extract_text(result["messages"][-1].content)


def generate_report(topic: str, use_documents: bool = True) -> Report:
    """
    Modules 6 + 8 — Sequential Chain:
    Step 1: Research Agent gathers facts via tools.
    Step 2: Structured Output model extracts findings into Report Pydantic model using json_mode.
    """
    # Step 1: Gather facts using research tools
    tools = ALL_TOOLS if use_documents else [web_search, wikipedia_lookup, compare_metrics]
    research_agent = create_agent(
        model=get_llm(temperature=0.2),
        tools=tools,
        system_prompt=RESEARCH_SYSTEM_PROMPT,
    )
    
    instruction = f"Gather comprehensive facts, metrics, and details for a report on: {topic}"
    research_result = research_agent.invoke({"messages": [HumanMessage(content=instruction)]})
    research_notes = _extract_text(research_result["messages"][-1].content)

    # Step 2: Format research notes into Report schema via JSON Mode
    structured_llm = get_llm(temperature=0.1).with_structured_output(Report, method="json_mode")
    
    # Prompt MUST explicitly include the word "JSON" for Groq API validation
    prompt = f"""Convert the following research notes on "{topic}" into a structured report.
Respond in valid JSON format according to the schema:

{research_notes}
"""
    report = structured_llm.invoke(prompt)
    return report