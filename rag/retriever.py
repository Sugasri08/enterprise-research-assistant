"""
Module 4 — Document Research (RAG), retrieval side.
Exposes the uploaded-documents knowledge base as an agent tool.
"""
from langchain_core.tools import tool
from rag.ingest import get_vectorstore


@tool
def search_uploaded_documents(query: str, k: int = 4) -> str:
    """
    Search the client's uploaded PDF/TXT documents (annual reports,
    research papers, policy documents) for relevant passages.
    Use this whenever the user references 'the uploaded report',
    'the document', or asks something that requires the client's
    own files rather than the open web.
    """
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search(query, k=k)

    if not results:
        return "No relevant content found in the uploaded documents. Has a document been uploaded yet?"

    chunks = []
    for i, doc in enumerate(results, 1):
        source = doc.metadata.get("source_file", "unknown")
        page = doc.metadata.get("page")
        loc = f"{source}" + (f", page {page + 1}" if page is not None else "")
        chunks.append(f"[{i}] ({loc})\n{doc.page_content.strip()}")

    return "\n\n".join(chunks)
