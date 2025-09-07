# RUB
- Each lab is a Notebood
- activate .venv from agents folder
- Run cells top to bottom, choose the venv kernel

# 2. OpenAI Agents SDK

This directory explores the **OpenAI Agents SDK**, a lightweight framework for building agentic applications. It covers the progression from basic agents to complex, multi-agent workflows with tools, handoffs, and guardrails.

## Labs

### [Lab 1: Introduction to Agents SDK](1_lab1.ipynb)
**Goal:** Get started with the `agents` library.
- Basic Agent creation (`Agent` class).
- Running agents with `Runner`.
- **Key Concept:** **Tracing**. Viewing execution traces in the OpenAI dashboard.

### [Lab 2: Sales Outreach System (Parallelism & Handoffs)](2_lab2.ipynb)
**Goal:** Build a multi-agent system for cold emailing.
- **Pattern:** **Parallel Execution**. Running multiple agents (Professional, Engaging, Busy) simultaneously using `asyncio.gather`.
- **Pattern:** **Agent-as-a-Tool**. Converting agents into callable tools.
- **Pattern:** **Handoffs**. Transferring control from a "Sales Manager" to an "Email Manager".
- Integration with **SendGrid** for sending real emails.

### [Lab 3: Multi-Model & Guardrails](3_lab3.ipynb)
**Goal:** Advanced configuration and safety.
- **Multi-Model Support:** Using models from other providers (DeepSeek, Google Gemini, Groq/Llama) within the OpenAI Agents SDK structure.
- **Pattern:** **Guardrails**. Implementing input guardrails (`@input_guardrail`) to validate or block user inputs before they reach the agent (e.g., PII protection).

### [Lab 4: Deep Research Agent](4_lab4.ipynb)
**Goal:** Build a complex "Deep Research" workflow.
- **Pattern:** **Planning & Execution**. A `PlannerAgent` breaks down a query into search terms, and a `SearchAgent` executes them.
- **Feature:** **Structured Outputs**. Using Pydantic models to force agents to return strict JSON schemas (e.g., `WebSearchPlan`).
- **Feature:** **Hosted Tools**. Using the built-in `WebSearchTool`.
- **Workflow:** Plan -> Search (Parallel) -> Report (Writer Agent) -> Email.
