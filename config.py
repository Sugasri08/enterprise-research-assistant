"""
Central configuration for the Enterprise Research Assistant.
Loads environment variables and exposes shared model instances.

Chat/agent model: Groq (llama-3.3-70b-versatile) — very high free-tier
throughput, good tool-calling support.
Embeddings: Google Gemini — Groq has no embeddings API, and Gemini's
free embedding quota is separate from (and much higher than) its chat
quota, so this stays zero-cost.
"""
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv(override=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "data", "chroma_db")
SESSIONS_DIR = os.path.join(os.path.dirname(__file__), "data", "sessions")


def get_llm(temperature: float = 0.3) -> ChatGroq:
    """
    Returns the shared chat/agent LLM. Uses Groq's free tier
    (no credit card required, high requests-per-day limit).
    """
    if not GROQ_API_KEY:
        raise EnvironmentError(
            "GROQ_API_KEY is not set. Copy .env.example to .env and add your "
            "free key from https://console.groq.com/keys"
        )
    return ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=GROQ_API_KEY,
        temperature=temperature,
        model_kwargs={"parallel_tool_calls": False},
    )


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """
    Returns the shared embeddings model for RAG (Module 4).
    Uses Gemini since Groq doesn't offer an embeddings endpoint.
    """
    if not GOOGLE_API_KEY:
        raise EnvironmentError(
            "GOOGLE_API_KEY is not set. RAG/document search needs a free Gemini "
            "key (separate from Groq) for embeddings — get one at "
            "https://aistudio.google.com/app/apikey and add it to .env"
        )
    return GoogleGenerativeAIEmbeddings(model="gemini-embedding-001", google_api_key=GOOGLE_API_KEY)