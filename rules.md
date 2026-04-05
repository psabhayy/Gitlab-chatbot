Markdown
# MASTER PROJECT BLUEPRINT: GitLab GenAI Chatbot (Detailed Specification)

## 🎯 System Instructions for Copilot Agent
You are an Expert AI Python Engineer. You are building a production-grade Retrieval-Augmented Generation (RAG) chatbot for a beginner user. You MUST read and follow this document strictly.

**STRICT RULES FOR COPILOT:**
1. **Modern LangChain ONLY:** You must NEVER use deprecated imports. 
   - 🚫 FORBIDDEN: `langchain.document_loaders`, `langchain.embeddings`, `langchain.vectorstores`, `langchain.chat_models`
   - ✅ REQUIRED: `langchain_community.document_loaders`, `langchain_chroma`, `langchain_google_genai`, `langchain_community.embeddings`
2. **Step-by-Step Execution:** Execute exactly ONE phase at a time. Do not create files for Phase 2 until the user confirms Phase 1 is done. Ask for permission to proceed after every phase.
3. **Extreme Commenting:** The user is a beginner. Add inline comments explaining what almost every line of Python code does.
4. **Terminal Commands:** When a phase requires running a terminal command (like `pip install` or `python run...`), output the exact command for the user to copy-paste.

---

## 📂 Expected Folder Structure
```text
gitlab-rag-bot/
├── data/
│   └── handbook/          # Cloned GitLab Handbook repository
├── src/
│   ├── __init__.py        # Empty file to make src a package
│   ├── config.py          # Constants and environment variables
│   ├── data_loader.py     # Logic for reading Markdown and Web URLs
│   └── rag_chain.py       # LLM, Memory, and Chain orchestration
├── vector_db/             # Local Chroma database directory
├── app.py                 # Streamlit Frontend UI
├── build_vector_store.py  # Script to ingest data and build the DB
├── requirements.txt       # Python dependencies
├── .env                   # Secret API Keys (DO NOT COMMIT)
├── README.md              # Setup instructions
└── ProjectDoc.md          # Architectural write-up
🛠️ Execution Phases & Exact File Specifications
Phase 1: Environment & Foundations
Create requirements.txt with exactly these contents:

Plaintext
streamlit==1.42.0
langchain==0.3.20
langchain-community==0.3.19
langchain-google-genai==2.0.10
langchain-chroma==0.2.2
sentence-transformers==3.4.1
chromadb==0.6.3
python-dotenv==1.0.1
unstructured==0.16.20
beautifulsoup4
Tell the user to create a virtual environment, activate it, and run pip install -r requirements.txt.

Create .env.example with GEMINI_API_KEY=your_gemini_api_key_here. Tell the user to copy this to .env and add their real key.

Create .gitignore to ignore venv/, .env, __pycache__/, and vector_db/.

Phase 2: Configuration (src/config.py)
Create src/config.py with the following explicit logic:

Import os and load_dotenv from dotenv. Call load_dotenv().

Define CHUNK_SIZE = 800 and CHUNK_OVERLAP = 150.

Define EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2" and LLM_MODEL_NAME = "gemini-1.5-flash".

Retrieve GEMINI_API_KEY = os.getenv("GEMINI_API_KEY"). Add a check: if the key is missing, raise a ValueError.

Define DIRECTION_PAGE_URLS as a list containing exactly these 5 URLs: https://about.gitlab.com/direction/, https://about.gitlab.com/direction/ai-powered/, https://about.gitlab.com/direction/plan/, https://about.gitlab.com/direction/create/, https://about.gitlab.com/direction/secure/.

Phase 3: Data Ingestion (src/data_loader.py)
Create src/data_loader.py.

Imports: os, DirectoryLoader, UnstructuredMarkdownLoader, WebBaseLoader (from langchain_community.document_loaders), RecursiveCharacterTextSplitter (from langchain_text_splitters), and constants from src.config.

Function load_documents():

Initialize an empty documents = [] list.

Handbook Logic: Check if os.path.exists("data/handbook"). If true, print a status message, initialize DirectoryLoader targeting **/*.md, load the docs, and extend the documents list. If false, print a warning.

Direction URLs Logic: Loop over DIRECTION_PAGE_URLS. Wrap WebBaseLoader(url).load() in a try/except block to gracefully catch and print scraping errors. Extend the documents list.

Chunking Logic: Initialize RecursiveCharacterTextSplitter using CHUNK_SIZE and CHUNK_OVERLAP. Call split_documents(documents).

Return the chunks. Include print statements showing how many total chunks were created.

Phase 4: Database Builder (build_vector_store.py)
Create build_vector_store.py at the root folder.

Imports: os, shutil, subprocess, Chroma (from langchain_chroma), HuggingFaceEmbeddings (from langchain_community.embeddings), and load_documents.

Function update_data_sources():

Use os.makedirs("data", exist_ok=True).

If data/handbook exists, use subprocess.run to execute git -C data/handbook pull.

If it does NOT exist, execute git clone https://gitlab.com/gitlab-com/content-sites/handbook.git data/handbook.

Function main():

Call update_data_sources().

Call chunks = load_documents(). If chunks is empty, exit gracefully.

If os.path.exists("vector_db"), use shutil.rmtree("vector_db") to delete the old database to prevent duplicates.

Initialize HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME).

Call Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory="vector_db").

Print a success message. Instruct the user to run this script.

Phase 5: The RAG Engine (src/rag_chain.py)
Create src/rag_chain.py.

Imports: os, Chroma, HuggingFaceEmbeddings, ChatGoogleGenerativeAI (from langchain_google_genai), ConversationSummaryBufferMemory, ConversationalRetrievalChain, PromptTemplate.

Function get_rag_chain():

Check if not os.path.exists("vector_db"). Return None if true.

Initialize embeddings. Initialize vector_store = Chroma(persist_directory="vector_db", embedding_function=embeddings).

Initialize retriever = vector_store.as_retriever(search_kwargs={"k": 5}).

Initialize llm = ChatGoogleGenerativeAI(model=LLM_MODEL_NAME, google_api_key=GEMINI_API_KEY, temperature=0.2).

Initialize memory = ConversationSummaryBufferMemory(llm=llm, memory_key="chat_history", return_messages=True, output_key="answer").

System Prompt: Create a PromptTemplate with input_variables=["context", "chat_history", "question"]. The prompt MUST enforce guardrails: "You are an AI assistant for GitLab. Use ONLY the provided context. If the answer is not in the context, politely decline to answer. Cite your sources naturally."

Build the chain: ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever, memory=memory, combine_docs_chain_kwargs={"prompt": prompt}, return_source_documents=True).

Return the chain.

Phase 6: The Frontend (app.py)
Create app.py at the root.

Imports: streamlit as st, get_rag_chain from src.rag_chain.

Page Config: st.set_page_config(page_title="GitLab Assistant", page_icon="🦊"). Display a title and description.

Initialization: Check if "messages" not in st.session_state. If not, set to empty list. Initialize st.session_state.qa_chain = get_rag_chain(). If it returns None, show st.error telling the user to run build_vector_store.py and call st.stop().

Sidebar: Add a "Clear Chat" button that resets st.session_state.messages and re-initializes the qa_chain (to clear memory).

Chat Rendering: Loop through st.session_state.messages and use st.chat_message to render past conversation.

Input Handling: if prompt := st.chat_input("Ask a question..."):

Render user message. Append to session state.

Render assistant message. Use with st.spinner("Searching GitLab Knowledge Base...").

Call response = st.session_state.qa_chain.invoke({"question": prompt}).

Render response["answer"].

Citations: Extract source_documents from the response. Create a set() of unique doc.metadata.get("source") strings. Loop through the set and display them using st.caption() below the answer.

Append assistant answer to session state.

Phase 7: Documentation (README.md & ProjectDoc.md)
README.md: Must contain: Project description, Tech Stack list, and numbered steps for Local Setup (git clone, venv, pip install, .env setup, python build_vector_store.py, streamlit run app.py).

ProjectDoc.md: A formal write-up addressing the evaluation criteria:

Approach: Explain the hybrid data loading (Git Clone + URL scraping).

Code Quality: Explain modular structure (src/).

Innovation: Explain memory, guardrails (prompt engineering), and source citation transparency in the UI.