# Shopwise AI Customer Support

A small Streamlit chat application that answers e-commerce support questions using LangChain and either a local Ollama model or OpenRouter. Conversation history is retained for follow-up questions for the lifetime of the current browser session.

## Requirements

- Python 3.10 or newer
- For Ollama: Ollama installed and running, plus a downloaded chat model
- For OpenRouter: an account and an API key

## Setup on Windows PowerShell

From this project directory:

1. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal and activate again.

2. Install dependencies:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Configure a provider:

   - **Ollama:** Install Ollama, then download a model, for example `ollama pull llama3.2`. Start Ollama before launching the app. No API key is needed.
   - **OpenRouter:** Copy `.env.example` to `.env`, then set `OPENROUTER_API_KEY` and, if needed, `OPENROUTER_MODEL`. Keep `.env` private; it is ignored by Git.

   The provider can be selected in the app sidebar. You can also set the model defaults in `.env`.

4. Start the UI:

   ```powershell
   streamlit run app.py
   ```

   Streamlit prints the local URL (usually http://localhost:8501).

## Example questions to test

- “My order is three days late. What should I do?”
- “My mug arrived broken. Can I get a replacement or refund?”
- “How do I return shoes that do not fit?”
- “How long do refunds usually take after a return?”
- Follow up with “What information should I include?” to verify the assistant uses conversation context.

## Safety and limitations

The assistant is not connected to order, account, shipping, or payment systems. It cannot verify order status, initiate returns, or issue refunds, and it is instructed not to invent store policy. It will suggest practical next steps and ask the customer to contact the retailer where account-specific action is needed. Do not enter passwords, payment card numbers, or other sensitive credentials.

## Evaluation checklist

For each sample question, check that the response is relevant, empathetic, and concise; does not fabricate an order status or policy; asks for useful missing details when appropriate; and correctly uses context in follow-ups. Repeat questions to check that tone and safety guidance remain consistent. Results depend on the selected model and its availability.
