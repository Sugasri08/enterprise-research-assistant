"""
Module 9 — Memory (short-term).
Wraps Streamlit's session_state so the ongoing conversation persists
across reruns within a session, but resets when the user clears it
or the session ends. Zero infrastructure cost.
"""
import streamlit as st


def init_short_term_memory():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []  # list[{"role": "user"|"assistant", "content": str}]


def add_message(role: str, content: str):
    st.session_state.chat_history.append({"role": role, "content": content})


def get_history() -> list[dict]:
    return st.session_state.get("chat_history", [])


def clear_history():
    st.session_state.chat_history = []


def history_as_text(max_turns: int = 10) -> str:
    """Render the last N turns as plain text, for inclusion in prompts."""
    turns = get_history()[-max_turns:]
    return "\n".join(f"{t['role'].upper()}: {t['content']}" for t in turns)
