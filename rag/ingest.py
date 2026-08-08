"""
Module 4 — Document Research (RAG), ingestion side.
Chunks uploaded PDFs/TXT files and stores embeddings in a local
ChromaDB instance. Fully free: Chroma runs in-process, embeddings use
the free Gemini quota (separate from the Groq chat model).
"""
import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from config import get_embeddings, CHROMA_DIR


def get_vectorstore() -> Chroma:
    return Chroma(
        collection_name="client_documents",
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_DIR,
    )


def ingest_file(file_path: str, client_name: str = "default") -> int:
    """
    Loads a PDF or TXT file, splits it into chunks, and adds it to the
    knowledge base tagged with a client_name so documents can later be
    filtered per client. Returns the number of chunks stored.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".txt":
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file type: {ext}. Use PDF or TXT.")

    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(docs)

    for c in chunks:
        c.metadata["client"] = client_name
        c.metadata["source_file"] = os.path.basename(file_path)

    vectorstore = get_vectorstore()
    vectorstore.add_documents(chunks)
    return len(chunks)