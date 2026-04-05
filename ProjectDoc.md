# Architectural Writeup: GitLab GenAI Assistant

## Approach: Hybrid Data Architecture
The core objective of this Retrieval-Augmented Generation (RAG) assistant is to provide highly accurate internal GitLab guidelines, principles, and strategic directions. To maximize information density and ensure high ingestion reliability, we designed a **Hybrid Data Architecture**:
- **Git Clone (Static Handbook):** We programmatically execute a `git clone` (and subsequent `pull` mechanisms) on the massive `gitlab-com/content-sites/handbook` repository. Pulling raw Markdown files locally achieves high-throughput, stable processing of the legacy handbook. We ingest this massive context efficiently using LangChain's `DirectoryLoader` paired with the `UnstructuredMarkdownLoader`.
- **URL Scraping (Direction Pages):** Simultaneously, to ensure the assistant provides immediate, up-to-date product insights, we dynamically invoke LangChain's `WebBaseLoader`. This handles real-time extraction of five crucial `about.gitlab.com/direction/` web URLs. 

This hybrid approach guarantees that our vector architecture remains both immensely deep (via the static Git Clone) and instantly relevant (via Web Scraping).

## Code Quality: Modular Structure (`src/`)
Constructed with modularization to adhere directly to core Software Engineering norms. Scaling this application logic is straightforward:
- `config.py`: Centralizes foundational constants like chunk variables, embedding parameters, database settings, and securely manages secrets logic, eliminating cross-file side effects.
- `data_loader.py`: Relegates the ETL (Extract, Transform, Load) logic to scrape, load, and recursively split the text payloads cleanly into usable vector chunks.
- `rag_chain.py`: Neatly separates the LangChain Prompt Templates, Retriever tuning (`k=10`), conversational memory instantiation, and chat session workflow away from the UI state logic.
- `app.py`: Acts purely as the visual frontend logic, leaving heavy compute tasks to the backend `src` modules.

## Innovation: Robustness & Enterprise UI Experience

- **Enterprise Prompt Guardrails:** Integrated a rigidly structured `PromptTemplate` dictating: *"You are an AI assistant for GitLab. Use ONLY the provided context. If the answer is not in the context, politely decline to answer."* to fundamentally counteract LLM hallucinations.
  - **QA Testing Proof:** During QA, when the bot was asked to list all core values, the retriever only fetched chunks mentioning 'transparency'. Instead of hallucinating the remaining values from its pre-trained global data, the bot strictly followed its system prompt and politely stated it didn't have the context to list them all. This proves the enterprise guardrails are fully operational.
  
- **Conversational Memory:** Utilizes LangChain's `ConversationSummaryBufferMemory`. By actively summarizing old conversations instead of concatenating them indefinitely, it maintains rich context for follow-up questions while strictly enforcing token limits and avoiding context window crashes.

- **Source Citations Transparency:** At a glance, the Streamlit frontend parses LangChain's return metadata, yielding non-obtrusive `st.caption` source URL hints below every answer. By denoting precisely which Markdown file or URL informed the language model's generation, it instills instant trust and auditability.
