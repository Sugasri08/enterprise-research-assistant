"""
Configuration module for LLM selection, embeddings, environment variables, and directory paths.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Force load variables from .env
load_dotenv(override=True)

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Directory Paths
SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")
DATA_DIR = os.path.join(BASE_DIR, "data")
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")

# Ensure required storage directories exist
os.makedirs(SESSIONS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)

# API Keys
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings


def get_embeddings():
    """Returns an open-source sentence-transformers embedding model for ChromaDB vector store."""
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def get_llm(temperature: float = 0.7) -> ChatGroq:
    """Returns ChatGroq model instance targeting llama-3.1-8b-instant."""
    if not GROQ_API_KEY or not GROQ_API_KEY.startswith("gsk_"):
        raise ValueError("GROQ_API_KEY is missing or invalid in your .env file.")

    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=temperature,
        max_retries=5,
        groq_api_key=GROQ_API_KEY,
    )