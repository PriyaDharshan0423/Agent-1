"""Streamlit e-commerce support assistant powered by LangChain."""

from __future__ import annotations

import os
from typing import Any

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

load_dotenv()

st.set_page_config(
    page_title="Shopwise Support",
    page_icon="🛍️",
    layout="centered",
    initial_sidebar_state="expanded",
)

SYSTEM_PROMPT = """You are Shopwise, a helpful and professional e-commerce customer support assistant.

Guidelines:
- Be empathetic, concise, and practical. Ask one focused follow-up question when needed.
- Help with delayed orders, damaged or missing products, returns, and refunds.
- Never claim to have accessed an order, account, shipment, or refund system. Do not invent policies, dates, order statuses, or actions.
- If details are missing, explain what information the customer should check or provide to the store's human support team. Do not request full payment card numbers, passwords, or other sensitive credentials.
- Explain that eligibility and timing depend on the store's actual policy when no policy details are supplied.
- For urgent safety concerns involving a product, advise the customer to stop using it and contact the retailer promptly.
- Use the conversation history to understand follow-up questions; do not repeat the whole prior answer unnecessarily."""

PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)


def create_model(provider: str, model_name: str) -> Any:
    """Build the configured LangChain chat model or raise an actionable error."""
    if provider == "OpenRouter":
        api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY is missing. Add it to your .env file, then restart the app."
            )
        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            default_headers={
                "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "http://localhost:8501"),
                "X-Title": os.getenv("OPENROUTER_APP_NAME", "Shopwise Support"),
            },
            temperature=0.3,
            timeout=60,
            max_retries=2,
        )

    return ChatOllama(
        model=model_name,
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0.3,
    )


def friendly_error(error: Exception, provider: str) -> str:
    """Return useful setup guidance without revealing environment values."""
    message = str(error).lower()
    if isinstance(error, ValueError):
        return str(error)
    if any(term in message for term in ("401", "unauthorized", "invalid api key", "authentication")):
        return "The provider rejected its credentials. Check your API key in .env and try again."
    if any(term in message for term in ("404", "model_not_found", "model not found")):
        return f"The model was not found. Check the {provider} model name and confirm it is available."
    if any(term in message for term in ("connection", "connect", "refused", "timeout", "network")):
        if provider == "Ollama":
            return "Could not connect to Ollama. Start Ollama and confirm the model is downloaded."
        return "Could not connect to OpenRouter. Check your internet connection and provider status."
    return f"The request failed ({type(error).__name__}). Check the provider settings and try again."


if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("🛍️ Shopwise")
    st.caption("AI-powered customer support")
    provider = st.radio("LLM provider", ["Ollama", "OpenRouter"], horizontal=True)

    default_model = (
        os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
        if provider == "OpenRouter"
        else os.getenv("OLLAMA_MODEL", "llama3.2")
    )
    model_name = st.text_input("Model", value=default_model, help="Use a model available from the selected provider.")

    if provider == "OpenRouter":
        if os.getenv("OPENROUTER_API_KEY", "").strip():
            st.success("OpenRouter API key loaded from .env")
        else:
            st.warning("Add OPENROUTER_API_KEY to .env before sending a message.")
    else:
        st.caption("Ollama must be running locally with the selected model available.")

    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.title("How can we help?")
st.write("Ask about a delayed order, a damaged item, a return, or a refund.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Type your question…")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Preparing a response…"):
            try:
                model = create_model(provider, model_name.strip())
                chain = PROMPT | model
                history = [
                    HumanMessage(content=item["content"])
                    if item["role"] == "user"
                    else AIMessage(content=item["content"])
                    for item in st.session_state.messages[:-1]
                ]
                result = chain.invoke({"history": history, "question": question})
                answer = result.content
                if isinstance(answer, list):
                    answer = "\n".join(
                        str(part.get("text", "")) if isinstance(part, dict) else str(part)
                        for part in answer
                    )
                answer = str(answer).strip() or "I couldn't generate a response. Please try again."
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as error:  # Provider and transport exceptions vary by integration.
                message = friendly_error(error, provider)
                st.error(message)
                st.session_state.messages.append({"role": "assistant", "content": message})
