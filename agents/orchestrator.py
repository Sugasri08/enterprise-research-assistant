"""
Modules 1, 5, 6, 8 — Chat Assistant, Multi-Source Research,
Structured Output, Sequential Chain.
"""
import json
import re
from langgraph.prebuilt import create_react_agent
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

CHAT_SYSTEM_PROMPT = """You are an enterprise research analyst assistant for a business consulting firm. 
Use the available tools to ground your answers in real information.
Cite where information came from (web, Wikipedia, or uploaded document) in your answer.
Be concise and professional, like a consultant briefing a colleague.

CRITICAL INSTRUCTION: Never output raw XML, HTML, or text tags like <web_search>, <search_uploaded_documents>, or </function>. Call native tools silently."""

RESEARCH_SYSTEM_PROMPT = """You are a research analyst. Use the available tools to gather real, up-to-date facts on the topic. 
Provide a concise summary of all findings.

CRITICAL INSTRUCTION: Never output raw XML, HTML, or text tags like <web_search>, <search_uploaded_documents>, or </function>. Call native tools silently."""


def build_chat_agent():
    llm = get_llm()
    llm_with_tools = llm.bind_tools(ALL_TOOLS)
    return create_react_agent(
        model=llm_with_tools,
        tools=ALL_TOOLS,
        prompt=CHAT_SYSTEM_PROMPT,
    )


def _extract_text(content) -> str:
    """Extract clean string text and strip leftover tool XML tags."""
    text = ""
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        text = "".join(parts) if parts else str(content)
    else:
        text = str(content)

    # Strip hallucinated pseudo-XML tags
    clean_text = re.sub(
        r'<(web_search|search_uploaded_documents|wikipedia_lookup|compare_metrics)>.*?</\1>',
        '',
        text,
        flags=re.DOTALL
    )
    clean_text = re.sub(r'</?function>', '', clean_text)
    return clean_text.strip()


def chat(user_input: str, chat_history: list[dict] | None = None) -> str:
    """
    Module 1 — Conversational entry point; calls tools as needed.
    """
    agent = build_chat_agent()
    
    # Keep only the last 4 messages to avoid Groq 6,000 TPM rate limit
    recent_history = (chat_history or [])[-4:]
    
    messages = _to_langchain_messages(recent_history) + [HumanMessage(content=user_input)]
    result = agent.invoke({"messages": messages})
    return _extract_text(result["messages"][-1].content)


def generate_report(topic: str, use_documents: bool = True) -> Report:
    """
    Modules 6 + 8 — Sequential Chain:
    Step 1: Research Agent gathers facts via tools.
    Step 2: Structured Output model extracts findings into Report Pydantic model using json_mode.
    """
    tools = ALL_TOOLS if use_documents else [web_search, wikipedia_lookup, compare_metrics]
    llm = get_llm(temperature=0.2)
    llm_with_tools = llm.bind_tools(tools)
    
    research_agent = create_react_agent(
        model=llm_with_tools,
        tools=tools,
        prompt=RESEARCH_SYSTEM_PROMPT,
    )

    instruction = f"Gather essential facts, metrics, and details for a concise report on: {topic}"
    research_result = research_agent.invoke({"messages": [HumanMessage(content=instruction)]})
    research_notes = _extract_text(research_result["messages"][-1].content)

    # Safely truncate research output to fit comfortably within single-request token limits
    MAX_CHAR_LIMIT = 8000
    if len(research_notes) > MAX_CHAR_LIMIT:
        research_notes = research_notes[:MAX_CHAR_LIMIT] + "\n...[Notes truncated to avoid token limit threshold]"

    # Step 2: Format research notes into Report schema via JSON Mode
    structured_llm = get_llm(temperature=0.1).with_structured_output(Report, method="json_mode")
    json_schema = json.dumps(Report.model_json_schema(), indent=2)

    prompt = f"""You are a research analyst. Convert the research notes on "{topic}" into a structured JSON report.

You MUST match this exact JSON schema structure and key names:
{json_schema}

Required JSON Keys:
- "title": (string)
- "executive_summary": (string)
- "key_findings": (list of strings)
- "strengths": (list of strings)
- "weaknesses": (list of strings)
- "future_opportunities": (list of strings)
- "conclusion": (string)
- "references": (list of strings)

Research Notes:
{research_notes}
"""
    report = structured_llm.invoke(prompt)
    return report