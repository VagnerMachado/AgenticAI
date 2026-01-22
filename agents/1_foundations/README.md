# RUN:
From agents folder:
- .\.venv\Scripts\activate
- uv sync
- python .\app.py
- Gradio app run on http://127.0.0.1:7860

# 1. Foundations of Agentic AI

This directory contains the foundational labs for building AI Agents. It progresses from basic API calls to multi-model evaluation, self-correction, and finally tool use and deployment.

## Labs

### [Lab 1: The Adventure Begins](1_lab1.ipynb)
**Goal:** Introduction to the OpenAI API and basic chaining.
- Setting up the environment and API keys.
- Basic Chat Completion API usage.
- **Pattern:** Chaining prompts. Generating a business idea, identifying a pain point, and proposing a solution using sequential LLM calls.

### [Lab 2: Multi-Model Evaluation](2_lab2.ipynb)
**Goal:** Compare different LLMs and introduce the "Judge" pattern.
- Querying multiple models: OpenAI (GPT-4o), Anthropic (Claude), Google (Gemini), Groq (Llama), and local models via Ollama.
- **Pattern:** **Evaluator/Judge**. Using an LLM to evaluate and rank the quality of responses from other LLMs.

### [Lab 3: The "Professionally You" Agent (Self-Correction)](3_lab3.ipynb)
**Goal:** Build a persona-based chatbot with a feedback loop.
- Uses `pypdf` to ingest a LinkedIn profile and `gradio` for the UI.
- **Pattern:** **Evaluator/Self-Correction**. An LLM checks the agent's response against specific criteria (e.g., "is it professional?"). If rejected, the agent retries with feedback.

### [Lab 4: Adding Tools & Deployment](4_lab4.ipynb)
**Goal:** Give the agent the ability to interact with the world.
- Adds **Function Calling (Tools)** to the chatbot from Lab 3.
- Tools implemented:
    - `record_user_details`: Saves user contact info.
    - `record_unknown_question`: Logs questions the agent couldn't answer.
- Integrates **Pushover** for real-time notifications.
- Deployment to **Hugging Face Spaces**.
