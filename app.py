"""
Enterprise Research Assistant — Streamlit entrypoint.
Wires together chat (Module 1), RAG upload (Module 4), structured
reports (Module 6), parallel research (Module 7), and memory (Module 9).
"""
import os
import tempfile
import streamlit as st

from memory.short_term import init_short_term_memory, add_message, get_history, clear_history
from memory.persistent_store import save_session, load_client_profile, list_clients
from rag.ingest import ingest_file
from agents.orchestrator import chat, generate_report
from agents.chains import parallel_research
from reports.exporter import to_txt_bytes, to_pdf_bytes

st.set_page_config(page_title="Enterprise Research Assistant", layout="wide")
init_short_term_memory()

# ---------------------------------------------------------------- Sidebar
with st.sidebar:
    st.header("Client & knowledge base")

    client_name = st.text_input("Client name", value=st.session_state.get("client_name", "default"))
    st.session_state.client_name = client_name

    st.subheader("Upload documents")
    uploaded_files = st.file_uploader(
        "PDF or TXT (annual reports, research, policies)",
        type=["pdf", "txt"],
        accept_multiple_files=True,
    )
    if uploaded_files and st.button("Create / update knowledge base"):
        with st.spinner("Ingesting documents..."):
            total_chunks = 0
            for f in uploaded_files:
                suffix = os.path.splitext(f.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(f.read())
                    tmp_path = tmp.name
                total_chunks += ingest_file(tmp_path, client_name=client_name)
                os.unlink(tmp_path)
        st.success(f"Indexed {total_chunks} chunks from {len(uploaded_files)} file(s).")

    st.divider()
    if st.button("Clear conversation"):
        clear_history()
        st.rerun()

    st.subheader("Previous clients")
    known_clients = list_clients()
    if known_clients:
        st.write(", ".join(known_clients))
    else:
        st.caption("No saved sessions yet.")

# ---------------------------------------------------------------- Main tabs
tab_chat, tab_report, tab_parallel = st.tabs(["Chat", "Generate report", "Compare companies"])

with tab_chat:
    _, col_mid, _ = st.columns([1, 4, 1])
    with col_mid:
        history = get_history()
        if not history:
            st.markdown("""
                <div style="text-align: center; margin-top: 2rem; margin-bottom: 2rem;">
                    <h2 style="font-weight: 700; font-size: 2.2rem; background: linear-gradient(90deg, #2563eb, #7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">
                        Research Assistant
                    </h2>
                    <p style="color: #64748b; font-size: 1.05rem;">Ask questions, draft comprehensive reports, or compare companies side-by-side.</p>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.info("💡 **Web Search**\n\n'Research NVIDIA's latest Blackwell chip release and GPU demand trends.'")
            with col2:
                st.info("📊 **Metrics Comparison**\n\n'Compare gross margins and revenue growth for Apple and Microsoft.'")
        else:
            st.markdown("<h3 style='margin-bottom: 1.5rem;'>Research Chat</h3>", unsafe_allow_html=True)

        # Render message history
        for msg in history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_input = st.chat_input("Ask a research question...")
        if user_input:
            add_message("user", user_input)
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                with st.status("Gathering intelligence and running tools...", expanded=True) as status:
                    try:
                        prior_turns = get_history()[:-1]  # Exclude current user message
                        reply = chat(user_input, chat_history=prior_turns)
                        status.update(label="Research completed", state="complete", expanded=False)
                    except Exception as e:
                        status.update(label="Failed to complete research", state="error", expanded=True)
                        reply = f"Something went wrong: {e}"
                
                st.markdown(reply)

            add_message("assistant", reply)
            save_session(client_name, get_history())
            st.rerun()

with tab_report:
    _, col_mid, _ = st.columns([1, 4, 1])
    with col_mid:
        st.subheader("Generate a structured report")
        topic = st.text_input("Research topic", placeholder="e.g. Tesla's AI strategy")
        use_docs = st.checkbox("Include uploaded documents", value=True)

        if st.button("Generate report", type="primary") and topic:
            with st.spinner("Researching, summarizing, and drafting the report..."):
                try:
                    report = generate_report(topic, use_documents=use_docs)
                    st.session_state.last_report = report
                except Exception as e:
                    st.error(f"Report generation failed: {e}")
                    report = None

        report = st.session_state.get("last_report")
        if report:
            st.markdown(report.to_markdown())
            col1, col2 = st.columns(2)
            with col1:
                st.download_button("Download as TXT", to_txt_bytes(report), file_name=f"{report.title}.txt")
            with col2:
                st.download_button("Download as PDF", to_pdf_bytes(report), file_name=f"{report.title}.pdf")

with tab_parallel:
    _, col_mid, _ = st.columns([1, 4, 1])
    with col_mid:
        st.subheader("Research multiple companies in parallel")
        raw_topics = st.text_input("Comma-separated topics", placeholder="Google, Microsoft, Amazon, OpenAI")
        if st.button("Run parallel research") and raw_topics:
            topics = [t.strip() for t in raw_topics.split(",") if t.strip()]
            with st.spinner(f"Researching {len(topics)} topics in parallel..."):
                results = parallel_research(topics)
            for topic_item, rep in results.items():
                with st.expander(topic_item, expanded=False):
                    st.markdown(rep.to_markdown())